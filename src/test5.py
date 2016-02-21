import os, sys, inspect, thread, time, math

src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
arch_dir = '../lib/x64' if sys.maxsize > 2**32 else '../lib/x86'
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))

import Leap, collections, pygame
from collections import defaultdict
#import pyglet

def mid_vector(VectorA, VectorB):
    return VectorA + (VectorB - VectorA) / 2


class DrumkitListen(Leap.Listener):
    note_kick = 36
    note_snare = 40
    note_hihat = 46
    note_piano_G = 4
    note_piano_A = 3
    note_piano_Bb = 2
    note_piano_B = 1
    note_piano_C = 0
    note_piano_D = 10
    note_piano_Eb = 11
    note_piano_E = 12
    note_piano_F = 13
    note_piano_GHI = 14

    VELOCITY_THRESHOLD = -400
    MULTISAMPLE_THRESHOLD = 0.5
    NOTE_HOLD = 40000
    play_audio = False # if audio has been initialized
    
    trackerDict = {} # a set for hands
    trackerFingerDict = {} # a set for fingers
    notes_playing = [] # a list
    sounds = {}

    def on_init(self, controller):
        print "Initialized\n"

    def on_frame(self, controller):
        trash = [] # Trash bin to store things marked for deletion, then delte
        
        # Get the immediate frame from controller
        frame = controller.frame()

        # Now we want to only iterate through if hands exist
        # frame.hands returns a list of (possibly empty) pointables
        if len(frame.hands) != 0 and self.play_audio == True:
            for hand in frame.hands:
                # If any pointables exceed the threshold, and are not on
                # the list, add them to list of trackerDict, which is
                # a list of dictionaries mapping Position names to their values
                # Note tip_velocity returns a vector, for now we
                # only care about the y direction (into the LEAP)
                if hand.palm_velocity.y < self.VELOCITY_THRESHOLD and hand.id not in self.trackerDict:
                    # Another note: we store references to the hand object
                    # through the id of the hand object as an index
                    self.trackerDict[hand.id] = defaultdict(dict)
                    # Now to store the position tuple? in the dictionary
                    # we could probably come up with a better method for doing this, idk
                    self.trackerDict[hand.id]['PositionA'] = hand.palm_position
#----------------------------------FINGER
        if len(frame.fingers) != 0 and self.play_audio == True:
            for pointable in frame.fingers:
                if (((pointable.direction)[1] < -.65 and pointable.id not in self.trackerFingerDict) or
                    (pointable.type == 0 and (pointable.direction)[1] <  -0.35 and pointable.id not in self.trackerFingerDict)):
                    self.trackerFingerDict[pointable.id] = collections.defaultdict(dict)
                    self.trackerFingerDict[pointable.id]['PositionA'] = pointable.tip_position
#----------------------------------HANDS
        # Now that we have added all things to the list, we must go
        # through the list and do stuff with them (ie. play sounds)

        # iterate over the indicies of trackerDict
        for beat_id in self.trackerDict:
            beat = self.trackerDict[beat_id]
            # if we have already played this beat, then add it to trash
            if 'note' in beat:
                # we only want to play notes for a certain time, so after NOTE HOLD
                # we must release/kill the note
                if frame.timestamp - beat['timestamp'] > self.NOTE_HOLD:
                    # remove the dictionary value that the note key references
                    # in notes_playing
                    self.notes_playing.remove(beat['note']) 
                    #add the id of the beat to be deleted
                    trash.append(beat_id)
            # Note has not been played yet, so we can process it as new
            else:
                hand = frame.hand(beat_id) #access most recent frame
                #access second most recent frame
                hand_prev = controller.frame(1).hand(beat_id)

                # Only proceed if current frame is valid since
                # it may give us an invalid pointable
                if hand.is_valid:
                    # only play if 2nd to most recent pointable is valid
                    # and if velocity is decreasing (accelaration is negative)
                    # since we are playing with LEAP below us, we need > -V
                    if (hand_prev.is_valid and hand.palm_velocity.y - 
                        hand_prev.palm_velocity.y > -self.VELOCITY_THRESHOLD / 3):
                        # we want the max velocity, and since we the 2nd to last is bigger
                        # than the most recent one, we're assuming third derivative is 0
                        # so 2nd to last is max velocity
                        beat['velocity'] = hand_prev.palm_velocity.y

                        # WE CAN CHANGE THIS FOR MORE STUFF
                        # we determine what note is played based on coords
                        if hand.palm_position.z < 0:
                            beat['note'] = self.note_hihat
                        elif hand.palm_position.x > 0:
                            beat['note'] = self.note_kick
                        else:
                            beat['note'] = self.note_snare

                        # We also must know if the note is already playing
                        # if so we must delete it so as to not double-play
                        if beat['note'] in self.notes_playing:
                            # trash dat shit
                            trash.append(beat_id)
                        else:
                            # we want to store the hit position for optional stuff later on
                            # maybe, we could delete this if we have no use
                            beat['PositionB'] = hand.palm_position
                            beat['Position'] = mid_vector(beat['PositionA'], beat['PositionB'])
                            
                            # Pass to the play_sound method, so we can module-ize this
                            self.play_sound(hand, beat)
                else:
                    # if not a valid pointable, we can just delete the thingy
                    trash.append(beat_id)
#----------------------------FINGER      
        for beat_id in self.trackerFingerDict:
            beat = self.trackerFingerDict[beat_id]
            # if we have already played this beat, then add it to trash
            if 'note' in beat:
                # we only want to play notes for a certain time, so after NOTE HOLD
                # we must release/kill the note
                if frame.timestamp - beat['timestamp'] > self.NOTE_HOLD:
                    # remove the dictionary value that the note key references
                    # in notes_playing
                    self.notes_playing.remove(beat['note']) 
                    #add the id of the beat to be deleted
                    trash.append(beat_id)
            # Note has not been played yet, so we can process it as new
            else:
                pointableX = frame.finger(beat_id) #access most recent frame
                #access second most recent frame
                pointableX_prev = controller.frame(1).finger(beat_id)

                # Only proceed if current frame is valid since
                # it may give us an invalid pointable
                if pointableX.is_valid:
                    # only play if 2nd to most recent pointable is valid
                    # and if velocity is decreasing (accelaration is negative)
                    # since we are playing with LEAP below us, we need > -V
                    beat['velocity'] = 1

                    # WE CAN CHANGE THIS FOR MORE STUFF
                    # we determine what note is played based on coords
                    if pointableX.hand.is_left:
                        beat['note'] = pointableX.type
                    else:
                        beat['note'] = 10 + pointableX.type

                    # We also must know if the note is already playing
                    # if so we must delete it so as to not double-play
                    if beat['note'] in self.notes_playing:
                        # trash dat shit
                        trash.append(beat_id)
                    else:
                        # we want to store the hit position for optional stuff later on
                        # maybe, we could delete this if we have no use
                        
                        # Pass to the play_sound method, so we can module-ize this
                        self.play_soundfinger(pointableX, beat)
                else:
                    # if not a valid pointable, we can just delete the thingy
                    trash.append(beat_id)
        

        for beat_id in trash:
            del self.trackerDict[beat_id]




    def play_soundfinger(self, finger, beat):
        # We want to say how long we have held the note, so we timestamp from the frame
        beat['timestamp'] = finger.frame.timestamp

        self.sounds[beat['note']][0].set_volume(velocity)
        self.sounds[beat['note']][0].play()

        # register that we're playing the note
        self.notes_playing.append(beat['note'])



    # REQUIRES init_audio first
    def play_sound(self, hand, beat):
        # We want to say how long we have held the note, so we timestamp from the frame
        beat['timestamp'] = hand.frame.timestamp


        # Now we want to find out the actual velocity
        # math to map to 0-127 taken from stocyr at github
        velocity = - beat['velocity'] - 500.0
        velocity /= 5000.0
        velocity = min(velocity, 1.0)
        velocity = max(0.0, velocity)
        velocity = math.pow(velocity, 0.4)

        if velocity < self.MULTISAMPLE_THRESHOLD:
            # this is soft then
            multisample = 0
        else:
            # this is hard
            multisample = 1
            velocity -= self.MULTISAMPLE_THRESHOLD/3
            velocity /= (1 - self.MULTISAMPLE_THRESHOLD/3)
        self.sounds[beat['note']][multisample].set_volume(velocity ** 0.2)
        self.sounds[beat['note']][multisample].play()

        # register that we're playing the note
        self.notes_playing.append(beat['note'])



    def init_audio(self):
        self.play_audio = True
        print "\nSetting up audio"
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.mixer.init()
        pygame.init()
        # These are the lists of sounds currently
        self.sounds[self.note_snare] = (pygame.mixer.Sound('../sound/pearlkit-snare1.wav'), pygame.mixer.Sound('../sound/pearlkit-snare1.wav'))
        self.sounds[self.note_kick] = (pygame.mixer.Sound('../sound/pearlkit-kick.wav'), pygame.mixer.Sound('../sound/pearlkit-kick.wav'))
        self.sounds[self.note_hihat] = (pygame.mixer.Sound('../sound/pearlkit-hihat.wav'), pygame.mixer.Sound('../sound/pearlkit-hihatO.wav'))
        self.sounds[self.note_piano_G] = (pygame.mixer.Sound('../sound/G.wav'))
        self.sounds[self.note_piano_A] = (pygame.mixer.Sound('../sound/A.wav'))
        self.sounds[self.note_piano_Bb] = (pygame.mixer.Sound('../sound/Bb.wav'))
        self.sounds[self.note_piano_B] = (pygame.mixer.Sound('../sound/B.wav'))
        self.sounds[self.note_piano_C] = (pygame.mixer.Sound('../sound/C.wav'))
        self.sounds[self.note_piano_D] = (pygame.mixer.Sound('../sound/D.wav'))
        self.sounds[self.note_piano_Eb] = (pygame.mixer.Sound('../sound/Eb.wav'))
        self.sounds[self.note_piano_E] = (pygame.mixer.Sound('../sound/E.wav'))
        self.sounds[self.note_piano_F] = (pygame.mixer.Sound('../sound/F.wav'))
        self.sounds[self.note_piano_GHI] = (pygame.mixer.Sound('../sound/Ghi.wav'))




def main():
    # Create a sample listener and controller
    listener = DrumkitListen()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)


    listener.init_audio()

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)


if __name__ == "__main__":
    main()  
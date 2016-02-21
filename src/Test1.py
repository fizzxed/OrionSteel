import os, sys, inspect, thread, time, math

src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
arch_dir = '../lib/x64' if sys.maxsize > 2**32 else '../lib/x86'
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))

import Leap, collections, pygame
#import pyglet

def mid_vector(VectorA, VectorB):
    return VectorA + (VectorB - VectorA) / 2


class DrumkitListen(Leap.Listener):
    note_kick = 36
    note_snare = 40
    VELOCITY_THRESHOLD = -600
    MULTISAMPLE_THRESHOLD = 0.5
    NOTE_HOLD = 40000
    play_audio = False # if audio has been initialized
    
    fingerTrackerDict = {} # a set
    notes_playing = [] # a list
    sounds = {}

    def on_init(self, controller):
        print "Initialized\n"

    def on_frame(self, controller):
        trash = [] # Trash bin to store things marked for deletion, then delte
        
        # Get the immediate frame from controller
        frame = controller.frame()

        # Now we want to only iterate through if pointables exist
        # frame.pointables returns a list of (possibly empty) pointables
        if len(frame.pointables) != 0 and self.play_audio == True:
            for pointableX in frame.pointables:
                # If any pointables exceed the threshold, and are not on
                # the list, add them to list of fingerTrackerDict, which is
                # a list of dictionaries mapping Position names to their values
                # Note tip_velocity returns a vector, for now we
                # only care about the y direction (into the LEAP)
                if pointableX.tip_velocity.y < self.VELOCITY_THRESHOLD and pointableX.id not in self.fingerTrackerDict:
                    # Another note: we store references to the pointableX object
                    # through the id of the pointable object as an index
                    self.fingerTrackerDict[pointableX.id] = collections.defaultdict(dict)
                    # Now to store the position tuple? in the dictionary
                    # we could probably come up with a better method for doing this, idk
                    self.fingerTrackerDict[pointableX.id]['PositionA'] = pointableX.tip_position

        # Now that we have added all things to the list, we must go
        # through the list and do stuff with them (ie. play sounds)

        # iterate over the indicies of fingerTrackerDict
        for beat_id in self.fingerTrackerDict:
            beat = self.fingerTrackerDict[beat_id]
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
                pointableX = frame.pointable(beat_id) #access most recent frame
                #access second most recent frame
                pointableX_prev = controller.frame(1).pointable(beat_id)

                # Only proceed if current frame is valid since
                # it may give us an invalid pointable
                if pointableX.is_valid:
                    # only play if 2nd to most recent pointable is valid
                    # and if velocity is decreasing (accelaration is negative)
                    # since we are playing with LEAP below us, we need > -V
                    if (pointableX_prev.is_valid and pointableX.tip_velocity.y - 
                        pointableX_prev.tip_velocity.y > -self.VELOCITY_THRESHOLD / 3):
                        # we want the max velocity, and since we the 2nd to last is bigger
                        # than the most recent one, we're assuming third derivative is 0
                        # so 2nd to last is max velocity
                        beat['velocity'] = pointableX_prev.tip_velocity.y

                        # WE CAN CHANGE THIS FOR MORE STUFF
                        # we determine what note is played based on coords
                        if pointableX.tip_position.x > 0:
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
                            beat['PositionB'] = pointableX.tip_position
                            beat['Position'] = mid_vector(beat['PositionA'], beat['PositionB'])
                            
                            # Pass to the play_sound method, so we can module-ize this
                            self.play_sound(pointableX, beat)
                else:
                    # if not a valid pointable, we can just delete the thingy
                    trash.append(beat_id)
        
        for beat_id in trash:
            del self.fingerTrackerDict[beat_id]

    # REQUIRES init_audio first
    def play_sound(self, pointableX, beat):
        # We want to say how long we have held the note, so we timestamp from the frame
        beat['timestamp'] = pointableX.frame.timestamp

        # Now we want to find out the actual velocity
        # math to map to 0-127 taken from stocyr at github
        velocity = - beat['velocity'] - 500.0
        velocity /= 6000.0
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
        self.sounds[beat['note']][multisample].set_volume(velocity)
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
        self.sounds[self.note_snare] = (pygame.mixer.Sound('../sound/Snare_soft.ogg'), pygame.mixer.Sound('../sound.Snare_hard.ogg'))
        self.sounds[self.note_kick] = (pygame.mixer.Sound('../sound/Kick_soft.ogg'), pygame.mixer.Sound('../sound/Kick_hard.ogg'))


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
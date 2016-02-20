import os, sys, inspect, thread, time
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
arch_dir = '../lib/x64' if sys.maxsize > 2**32 else '../lib/x86'
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))

import Leap, pyglet, collections

class DrumkitListen(Leap.Listener):
    note_kick = 36
    note_snare = 40
    VELOCITY_THRESHOLD = -600
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
        if not frame.pointables.empty and self.play_audio == True:
            for pointableX in frame.pointables:
                # If any pointables exceed the threshold, and are not on
                # the list, add them to list of fingerTrackerDict, which is
                # a list of dictionaries mapping Position names to their values
                # Note tip_velocity returns a vector, for now we
                # only care about the y direction (into the LEAP)
                if (pointableX.tip_velocity.y < self.VELOCITY_THRESHOLD and 
                    pointableX.id not in self.fingerTrackerDict):
                    # Another note: we store references to the pointableX object
                    # through the id of the pointable object as an index
                    self.fingerTrackerDict[pointableX.id] = collections.defaultdict(dict)
                    # Now to store the position tuple? in the dictionary
                    # we could probably come up with a better method for doing this, idk
                    self.fingerTrackerDict[pointableX.id]['PositionA'] = pointableX.tip_position

        # Now that we have added all things to the list, we must go
        # through the list and do stuff with them (ie. play sounds)





def main():
    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

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
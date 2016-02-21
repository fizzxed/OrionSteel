import os, sys, inspect, pyglet, mingus, mingus.extra.lilypond
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
arch_dir = '../lib/x64' if sys.maxsize > 2**32 else '../lib/x86'
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))

import Leap, sys, thread, time

snare_sound = pyglet.media.load("..\sound\E-Mu-Proteus-FX-Wacky-Snare.wav", streaming=False)

hihat_sound = pyglet.media.load("..\sound\Closed-Hi-Hat-1.wav", streaming=False)

bass_sound = pyglet.media.load("..\sound\Bass-Drum-1 (1).wav", streaming=False)

A = pyglet.media.load("..\sound\piano-a.wav", streaming=False)

B = pyglet.media.load("..\sound\piano-b.wav", streaming=False)

C = pyglet.media.load("..\sound\piano-c.wav", streaming=False)

D = pyglet.media.load("..\sound\piano-d.wav", streaming=False)

E = pyglet.media.load("..\sound\piano-e.wav", streaming=False)

F = pyglet.media.load("..\sound\piano-f.wav", streaming=False)

G = pyglet.media.load("..\sound\piano-g.wav", streaming=False)

one = pyglet.media.load("..\sound\Another one.wav", streaming=False)

emilio = pyglet.media.load("..\sound\we da best.wav", streaming=False)

soundlist = [A, B, C, D, E]

instrument = raw_input("what instrument?")

class SampleListener(Leap.Listener):
    def on_init(self, controller):
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"

    def on_disconnect(self, controller):
        print "Disconnected"

    def on_exit(self, controller):
        mingus.extra.lilypond.to_png(mingus.extra.lilypond.from_Track(self.track), "Sheet Music")
        print "Exited"
    time_right = [0] * 2
    vel = [0] * 2
    count = 0
    tempo = 0
    cmp_array = [0] * 2
    track = mingus.containers.track.Track()
    counter = 0
    vel2 = [0] * 2

    listoffingers = ["thumb","index","middle", "ring", "pinky"]

    def on_frame(self, controller):
        frame = controller.frame()
        if instrument == "drums":
            for hand in frame.hands:
                if (abs(hand.palm_velocity[1]) > 500):

                    self.vel[0] = self.vel[1]
                    self.vel[1] = hand.palm_velocity[1]

                    if (self.vel[0] > 0 and self.vel[1] < 0):
                        if hand.is_left:
                            snare_sound.play()
                        else:
                            self.time_right[0] = self.time_right[1]
                            self.time_right[1] = frame.timestamp

                            #Record first four notes and the time between them
                            if (self.count <= 4):
                                if (self.count == 3):
                                    self.tempo += self.time_right[1] - self.time_right[0]
                                self.count += 1
                            if (self.count > 4 and (self.time_right[1] - self.time_right[0] + 0.0) / self.tempo < .6):
                                self.track.add_notes('G', 8)
                            else:
                                self.track.add_notes('G')
                            hihat_sound.play()
                            time.sleep(.1)
                        self.count = self.count + 1
        elif instrument == "piano":
            for hand in frame.hands:
                for pointable in hand.pointables:
                    if (pointable.direction)[1]< -.65:
                        note = pointable.id % 10
                        finger = self.listoffingers[note]
                        soundlist[note].play()
                        time.sleep(.1)
        elif instrument == "DJ":
            for hand in frame.hands:
                if (abs(hand.palm_velocity[1]) > 500):
                    self.vel[0] = self.vel[1]
                    self.vel[1] = hand.palm_velocity[1]
                    if (self.vel[0] > 0 and self.vel[1] < 0):
                        if hand.is_left:
                            one.play()
                        else:
                            emilio.play()
                            time.sleep(.1)
                        self.count = self.count + 1





def magnitude(l):
    sum = 0
    for i in l:
        sum += i ** 2
    return sum ** 0.5

def main():
    listener = SampleListener()
    controller = Leap.Controller()
    controller.add_listener(listener)

    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        controller.remove_listener(listener)

if __name__ == "__main__":
    main()
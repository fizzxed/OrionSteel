import os, sys, inspect, pyglet
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
arch_dir = '../lib/x64' if sys.maxsize > 2**32 else '../lib/x86'
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))

import Leap, sys, thread, time

snare_sound = pyglet.media.load("..\sound\E-Mu-Proteus-FX-Wacky-Snare.wav", streaming=False)

hihat_sound = pyglet.media.load("..\sound\Closed-Hi-Hat-1.wav", streaming=False)

bass_sound = pyglet.media.load("..\sound\Bass-Drum-1 (1).wav", streaming=False)


class SampleListener(Leap.Listener):
	def on_init(self, controller):
		print "Initialized"

	def on_connect(self, controller):
		print "Connected"

	def on_disconnect(self, controller):
		print "Disconnected"

	def on_exit(self, controller):
		print "Exited"

	vel = [0] * 2
	count = 0

	def on_frame(self, controller):
		frame = controller.frame()
		#tool = frame.tools.frontmost
		#if tool.is_valid:
		#	print(tool.tip_velocity)
		for hand in frame.hands:
			hand_name = "Left" if hand.is_left else "Right"
			if (abs(hand.palm_velocity[1]) > 500):
				self.vel[0] = self.vel[1]
				self.vel[1] = hand.palm_velocity[1]
				if (self.vel[0] > 0 and self.vel[1] < 0):
					if hand.is_left:
						snare_sound.play()
					else:
						hihat_sound.play() 
					print self.count
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
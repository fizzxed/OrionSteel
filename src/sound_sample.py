

import pyglet
from pyglet.window import key

window = pyglet.window.Window()
keys = key.KeyStateHandler()
window.push_handlers(keys)


snare_sound = pyglet.media.load("C:\Users\Hans\Downloads\E-Mu-Proteus-FX-Wacky-Snare.wav", streaming=False)

hihat_sound = pyglet.media.load("C:\Users\Hans\Downloads\Closed-Hi-Hat-1.wav", streaming=False)

bass_sound = pyglet.media.load("C:\Users\Hans\Downloads\Bass-Drum-1 (1).wav", streaming=False)

A = pyglet.media.load("C:\Users\Hans\Downloads\piano-a.wav", streaming=False)

B = pyglet.media.load("C:\Users\Hans\Downloads\piano-b.wav", streaming=False)

C = pyglet.media.load("C:\Users\Hans\Downloads\piano-c.wav", streaming=False)

D = pyglet.media.load("C:\Users\Hans\Downloads\piano-d.wav", streaming=False)

E = pyglet.media.load("C:\Users\Hans\Downloads\piano-e.wav", streaming=False)

F = pyglet.media.load("C:\Users\Hans\Downloads\piano-f.wav", streaming=False)

G = pyglet.media.load("C:\Users\Hans\Downloads\piano-g.wav", streaming=False)



def drums():
    @window.event
    def on_key_press(symbols, modifiers):
        if symbols == key.SPACE:
            snare_sound.play()
        if symbols == key.A:
            hihat_sound.play()
        if symbols == key.B:
            bass_sound.play()

def piano():
    @window.event
    def on_key_press(symbols, modifiers):
        if symbols == key.S:
            A.play()
        if symbols == key.D:
            B.play()
        if symbols == key.F:
            C.play()
        if symbols == key.G:
            D.play()
        if symbols == key.H:
            E.play()
        if symbols == key.J:
            F.play()
        if symbols == key.K:
            G.play()
    # this lets the sound complete


    # also tried this with 'update()'
    #player.queue(bullet_sound)

#def update(dt):
#    player.play()
#pyglet.clock.schedule_interval(update, 1/120.0)
drums()

pyglet.app.run()
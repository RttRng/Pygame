import pygame as p
import os
import random as r
from pygameUtils import c

def reset():
    global sound_events
    sound_events = {"shoot": False,"hit": False}
class Sound:
    def __init__(self,name):
        self.path = "Assets/Sfx"
        self.files =  [f for f in os.listdir(self.path) if os.path.isfile(os.path.join(self.path,f)) and name in f]
        self.sound = [p.mixer.Sound("Assets/Sfx/" + f) for f in self.files ]
    def __call__(self):
        s =  r.choice(self.sound)
        s.set_volume(c.sfxvolume/100)
        s.play()
class Music:
    def __init__(self,name_and_type):
        self.path = "Assets/Music"
        self.file = self.path + "/" + name_and_type
    def __call__(self, *args, **kwargs):
        p.mixer.music.load(self.file)
        p.mixer.music.play(loops=0, start=0.0, fade_ms=0)
        p.mixer.music.set_volume(c.musicvolume/100)
p.mixer.init()
sound_events = {"shoot": False,"hit": False}
hit = Sound("hit")
shoot = Sound("shoot")
main_theme = Music("TEST.mp3")

def apply_volume():
    p.mixer.music.set_volume(c.musicvolume / 100)


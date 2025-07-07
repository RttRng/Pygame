import pygame as p
import os
import random as r



class Sound:
    def __init__(self,name):
        self.path = "Assets/Sfx"
        self.files =  [f for f in os.listdir(self.path) if os.path.isfile(os.path.join(self.path,f)) and name in f]
        self.sound = [p.mixer.Sound("Assets/Sfx/" + f) for f in self.files ]
    def __call__(self, *args, **kwargs):
        r.choice(self.sound).play()
p.mixer.init()
sound_events = {"shoot": False,"hit": False}
hit = Sound("hit")
shoot = Sound("shoot")
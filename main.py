import threading
import pygameLib as l
from pygameLib import *
from networkingLib import *
import sound as sfx
import pygame as p
import scenes

host = None
client = None
sm = scenes.sm

if __name__ == "__main__":
    sm.change_scene("MainMenu")
    while c.running:
        try:
            sm.handle_events(p.event.get())0
            sm.update()
            sm.draw(c.screen)
            c.clock.tick(c.fps)
        except KeyboardInterrupt:
            running = False







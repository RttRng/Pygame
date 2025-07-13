import pygame as p
from networkingLib import *
from pygameLib import *

class Controler:
    def __init__(c):
        p.init()
        c.clock = p.time.Clock()

        c.base_size = (768, 432)
        c.fullscreen_size = (1920, 1080)
        c.screen_ratio = (16,9)
        c.canvas_size = (768, 432)
        ratio = c.screen_ratio[0]/c.screen_ratio[1]

        c.base_size = (c.base_size[0],c.base_size[0]/ratio)
        c.fullscreen_size = (c.fullscreen_size[0],c.fullscreen_size[0]/ratio)

        c.bounds = (-50, -50, c.canvas_size[0] + 50, c.canvas_size[1] + 50)
        c.warp_bounds = (0, 0, c.canvas_size[0], c.canvas_size[1])

        c.display = p.display.set_mode(c.canvas_size)
        c.screen = p.surface.Surface(c.canvas_size)

        c.fullscreen = False
        c.update_screen()
        c.scale = 1
        c.delta_time = 1
        c.master = True
        c.running = True
        c.fps = 60
        c.net = False
        c.spawn = False
        c.sfxvolume = 50
        c.musicvolume = 50
        c.FONT = p.font.SysFont("Arial", 18)
        c.PORT = 42069
        c.IP = "25.21.131.22"

        c.loadout = 0
        c.list_bosses = ["JohnBoss","Enemy"]
        # c.IP = "192.168.0.150"
    def toggle_fullscreen(c):
        c.fullscreen = not c.fullscreen
        c.update_screen()
    def update_screen(c):
        if c.fullscreen:
            c.display = p.display.set_mode(c.fullscreen_size, p.FULLSCREEN)
        else:
            c.display = p.display.set_mode(c.base_size)
        c.scale = c.display.get_width()/c.canvas_size[0]
    def output_to_display(c):
        scaled_screen = p.transform.scale(c.screen, c.display.get_size())
        c.display.blit(scaled_screen, (0, 0))
        p.display.flip()

c = Controler()
import pygameLib as l
import networking as n

import math as m
import pygame as p
import random as r
import asyncio as a
import socket as s
import threading as t

import trig

if __name__ == "__main__":
    size = (800,600)
    p.init()
    p.mixer.init()
    screen = p.display.set_mode(size)
    clock = p.time.Clock()


    mouse = l.mouse
    player = l.Player(400,300)
    enemies = [l.Enemy(100,100)]


    running = True
    while running:
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
        screen.fill("purple")
        mouse.update()
        l.gAll.update()
        l.gAll.draw(screen)
        if r.randint(1,20)==20:
            spawnx,spawny = trig.speeddeg_xy(500+r.randint(0,200),r.randint(0,360))
            enemies.append(l.Enemy(400+spawnx,  300+spawny))





        clock.tick(60)
        p.display.flip()

import math as m

import pygame
import pygame as p
import random as r
import asyncio as a
import socket as s
import threading as t

import pygame as g
import math as m
import random as r
import asyncio as a

import trig





class Mouse:
    def __init__(self):
        self.pos = (0,0)
        self.pressed = (False,False,False)
        self.clicked = (False,False,False)
        self.released = (False,False,False)
    def update(self):
        self.pos = p.mouse.get_pos()
        pressed_new = p.mouse.get_pressed()
        delta = (pressed_new[0] != self.pressed[0], pressed_new[1] != self.pressed[1],
                    pressed_new[2] != self.pressed[2])
        self.clicked = (pressed_new[0] and delta[0], pressed_new[1] and delta[1], pressed_new[2] and delta[2])
        self.released = (self.pressed[0] and delta[0], self.pressed[1] and delta[1], self.pressed[2] and delta[2])
        self.pressed = p.mouse.get_pressed()
    def pressed(self):
        return self.pressed
    def click(self):
        return self.clicked
    def release(self):
        return self.released
    def position(self):
        return self.pos
mouse = Mouse()

gAll = p.sprite.Group()
gPlayer = p.sprite.Group()
gEnemies = p.sprite.Group()
gPlayerProjectiles = p.sprite.Group()

class Object(p.sprite.Sprite):
    def __init__(self,x,y,sprite):
        super().__init__()
        gAll.add(self)
        self.x = x
        self.y = y
        self.sprite = "Assets/Sprites/Png/"+sprite
        self.mask = p.mask.from_surface(p.image.load(self.sprite))
        self.image = p.image.load(self.sprite)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.x, self.y
    def update(self):
        self.rect.x,self.rect.y = self.x,self.y


class Player(Object):
    def __init__(self,x,y):
        super().__init__(x,y,"Player.png")
        gPlayer.add(self)
    def update(self):
        keys = p.key.get_pressed()
        if keys[p.K_w]:
            self.y -= 5
        if keys[p.K_s]:
            self.y += 5
        if keys[p.K_a]:
            self.x -= 5
        if keys[p.K_d]:
            self.x += 5
        if mouse.click()[0]:
            proj = Projectile(self.x,self.y,trig.angledeg((self.x,self.y),mouse.position()))


        super().update()
class Projectile(Object):
    def __init__(self,x,y,direction):
        super().__init__(x,y,"Pellet.png")
        self.dx,self.dy = trig.speeddeg_xy(5, direction)
        gPlayerProjectiles.add(self)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        super().update()

class Enemy(Object):
    def __init__(self,x,y):
        super().__init__(x,y,"Enemy.png")
        self.speed = 4
        self.dx,self.dy = 0,0
        gEnemies.add(self)
        self.hit = p.mixer.Sound("Assets/Sfx/Hit1.wav")
    def update(self):
        target = trig.get_nearest_sprite(self,gPlayer)
        if target is not None:
            angle = trig.angledeg((self.x,self.y),(target.x,target.y))
            self.dx,self.dy = trig.speeddeg_xy(self.speed,angle)
            self.x += self.dx
            self.y += self.dy
        super().update()
        if pygame.sprite.spritecollide(self,gPlayerProjectiles,True):
            self.kill()
            self.hit.play()
        if pygame.sprite.spritecollide(self,gPlayer,True):
            self.kill()
            self.hit.play()
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



master = True
def def_sound(location):
    return p.mixer.Sound("Assets/Sfx/"+location+".wav")


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
size = (0,0)
bounds = (0,0,0,0)
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
        self.sprite = "Assets/Sprites/Png/"+sprite+".png"
        self.mask = p.mask.from_surface(p.image.load(self.sprite))
        self.image = p.image.load(self.sprite)
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = self.x, self.y
    def resize(self,size):
        self.image = p.transform.scale(self.image,size)
        self.rect = self.image.get_rect()
        self.mask = p.mask.from_surface(self.image)

    def update(self):
        self.rect.centerx, self.rect.centery = self.x, self.y

    def draw(self,screen):
        try:
            if self.image and self.rect:
                super().draw(screen)
        except Exception as e:
            print(f"Chyba při vykreslování: {e}")


class Player(Object):
    def __init__(self,x,y):
        super().__init__(x,y,"Player")
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
            Events.projectile((self.x,self.y),mouse.position())
        if self.x > bounds[2]:
            self.x = bounds[2]
        if self.x < bounds[0]:
            self.x = bounds[0]
        if self.y > bounds[3]:
            self.y = bounds[1]
        super().update()
class Player2(Object):
    def __init__(self, x, y):
        super().__init__(x, y, "Player2")
        gPlayer.add(self)


class Projectile(Object):
    def __init__(self,x,y,direction):
        super().__init__(x,y,"Pellet")
        self.resize((10,10))
        self.dx,self.dy = trig.speeddeg_xy(5, direction)
        gPlayerProjectiles.add(self)

    def update(self):
        if master:
            self.x += self.dx
            self.y += self.dy
        super().update()
        if self.x > bounds[2] or self.x < bounds[0] or self.y > bounds[3] or self.y < bounds[1]:
            self.kill()

class Enemy(Object):
    def __init__(self,x,y):
        super().__init__(x,y,"Enemy")
        self.speed = 4
        self.dx,self.dy = 0,0
        gEnemies.add(self)

    def update(self):
        if master:
            target = trig.get_nearest_sprite(self,gPlayer)
            if target is not None:
                angle = trig.angledeg((self.x,self.y),(target.x,target.y))
                self.dx,self.dy = trig.speeddeg_xy(self.speed,angle)
                self.x += self.dx
                self.y += self.dy
        super().update()


shooting = (False,0,0)
sound_events = {"shoot": False,"hit": False}
p.mixer.init()
hit = def_sound("Hit1")
shoot = def_sound("Shoot1")
class Events:
    def __init__(self):
        pass
    
    @staticmethod
    def check_collisions():
        global hit
        # Player collides with enemies
        collisions1 = p.sprite.groupcollide(gPlayer, gEnemies, True, True)
        for player, enemies in collisions1.items():
            for enemy in enemies:
                print("Player collided with enemy!")
                if master:
                    hit.play()
                    sound_events["hit"] = True
                # Run your custom logic here (e.g. lose life, play sound, etc.)

        # Player projectiles hit enemies
        collisions2 = p.sprite.groupcollide(gEnemies, gPlayerProjectiles, True, True)
        for enemy, projectiles in collisions2.items():
            for projectile in projectiles:
                print("Enemy hit by projectile!")
                if master:
                    hit.play()
                    sound_events["hit"] = True
                # Run your custom logic here (e.g. increase score, spawn explosion, etc.)

    @staticmethod
    def projectile(playerxy, mousexy):
        global sound_events, shooting  # Deklarace globálních proměnných na začátku metody
        
        if master:
            Projectile(playerxy[0], playerxy[1], trig.angledeg(playerxy, mousexy))
            shoot.play()
            sound_events["shoot"] = True
        else:
            shooting = (True, mousexy[0], mousexy[1])
            shoot.play()
            sound_events["shoot"] = True
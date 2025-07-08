import pygame as p
import trig
import events as e
import sound as sfx
from pygameUtils import *
import random as r
from sound import sound_events
master = True

screen_size = (800, 600)
bounds = (-50, -50, 850, 650)
warp_bounds = (0, 0, 800, 600)

mouse = Mouse()
gPlayer = p.sprite.Group()
gEnemies = p.sprite.Group()
gPlayerProjectiles = p.sprite.Group()

class Player(Object):
    def __init__(self,x,y):
        super().__init__(x,y,"Player")
        gPlayer.add(self)
        self.acceleration = 1
        self.rotation_speed = 5
        self.dx,self.dy = 0,0
        self.friction_coef = 0.02
        self.direction = 0
        self.hp = 3
        self.firerate = 120
        self.last_shot = 0
        self.shoot_type = 1

    def update(self):
        keys = p.key.get_pressed()
        self.desired_direction = trig.angledeg(self.rect.center, (mouse.position()))

        self.image = p.transform.rotate(self.original_image, -self.direction)
        self.rect = self.image.get_rect(center=self.rect.center)

        self.direction = self.rotate_toward()

        if mouse.press()[2]:
            self.add_speed()
        self.friction()


        self.rect.centerx += self.dx * self.delta_time
        self.rect.centery += self.dy * self.delta_time
        self.shoot()
        self.wrap(warp_bounds)
        super().update()
    def shoot(self):
        if mouse.press()[0]:
            current_time = p.time.get_ticks()
            if current_time - self.last_shot > self.firerate:
                self.last_shot = p.time.get_ticks() + r.randint(-40, 40)
                if self.shoot_type == 0:
                    e.projectile(self.rect.center, self.direction, master)
                if self.shoot_type == 1:
                    for i in range(3):
                        e.projectile(self.rect.center, self.direction+r.randint(-10,10), master)

    def kill(self):
        e.events["Player2Died"] = True
        super().kill()

class Player2(Object):
    def __init__(self, x, y):
        super().__init__(x, y, "Player2")
        gPlayer.add(self)


class Projectile(Object):
    def __init__(self,x,y,direction=0):
        super().__init__(x,y,"Pellet")
        self.resize((10,10))
        self.dx,self.dy = trig.speeddeg_xy(5, direction)
        gPlayerProjectiles.add(self)

    def update(self):


        try:
            if master:
                self.rect.centerx += self.dx * self.delta_time
                self.rect.centery += self.dy * self.delta_time
            super().update()
            self.out_of_bounds(bounds)
        except Exception as e:
            try:
                self.kill()
            except:
                pass
class Enemy(Object):
    def __init__(self,x,y):
        super().__init__(x,y,"Enemy")
        self.speed = 4
        self.dx,self.dy = 0,0
        gEnemies.add(self)
        self.hp = 3

    def update(self):
        try:
            if master:
                target = trig.get_nearest_sprite(self,gPlayer)
                if target is not None:
                    angle = trig.angledeg(self.rect.center,target.rect.center)
                    self.dx,self.dy = trig.speeddeg_xy(self.speed,angle)
                    self.rect.centerx += self.dx * self.delta_time
                    self.rect.centery += self.dy * self.delta_time
            super().update()
        except Exception as e:
            try:
                self.kill()
            except:
                pass


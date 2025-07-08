import pygame as p
import trig
import events as e
import sound as sfx
from pygameUtils import *
from main import SIZE, BOUNDS, WRAP_BOUNDS
from sound import sound_events

master = True
mouse = Mouse()
gPlayer = p.sprite.Group()
gEnemies = p.sprite.Group()
gPlayerProjectiles = p.sprite.Group()

class Player(Object):
    def __init__(self,x,y):
        super().__init__(x,y,"Player")
        gPlayer.add(self)
        self.acceleration = 4
        self.rotation_speed = 15
        self.dx,self.dy = 0,0
        self.friction_coef = 0.05
        self.direction = 0
        self.hp = 3

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
        if mouse.click()[0]:
            e.events["Shooting"] = e.projectile(self.rect.center,self.direction,master)
        self.wrap(WRAP_BOUNDS)
        super().update()
    def kill(self):
        e.events["Player2Died"][0] = True
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
            self.out_of_bounds(BOUNDS)
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


import pygame as p
import trig
import events as e
import sound as sfx
from pygameUtils import *
import random as r
from sound import sound_events
from control import c


mouse = Mouse()
gPlayer = p.sprite.Group()
gEnemies = p.sprite.Group()
gPlayerProjectiles = p.sprite.Group()
gEnemyProjectiles = p.sprite.Group()
gBoss = p.sprite.Group()


def switch(scene):
    c.scene = scene
    gAll.empty()
    gText.empty()
    gUI.empty()
    c.reset = True

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
        self.shoot_type = c.loadout
        self.alive = True
        self.invincible_cooldown = 1000
        self.resize((20,20))


    def update(self):
        keys = p.key.get_pressed()
        self.desired_direction = trig.angledeg(self.rect.center, (mouse.position()))

        self.image = p.transform.rotate(self.scaled_image, -self.direction)
        self.rect = self.image.get_rect(center=self.rect.center)

        self.direction = self.rotate_toward()

        if mouse.press()[2]:
            self.add_speed()
        self.friction()

        self.hit(-1, self.direction)
        self.rect.centerx += self.dx * c.delta_time
        self.rect.centery += self.dy * c.delta_time
        self.shoot()
        self.wrap()
        super().update()
        self.shoot_type = c.loadout
    def shoot(self):
        if mouse.press()[0]:
            if p.time.get_ticks() - self.last_shot > self.firerate:
                sfx.shoot()
                self.last_shot = p.time.get_ticks() + r.randint(-40, 40)
                if self.shoot_type == 0:
                    dmg = 20
                    e.projectile(self.rect.center, self.direction, dmg, c.master)
                if self.shoot_type == 1:
                    dmg = 1
                    for i in range(3):
                        e.projectile(self.rect.center, self.direction+15* (r.random()*2-1),dmg , c.master)

    def kill(self):
        self.alive = False
        super().kill()

class Player2(Object):
    def __init__(self, x, y):
        super().__init__(x, y, "Player2")
        self.hp = 3
        self.resize((20,20))
        gPlayer.add(self)
        self.invincible_cooldown = 1000

class Projectile(Object):
    def __init__(self,x,y,direction=0,dmg = 1):
        super().__init__(x,y,"Pellet")
        self.speed = 15
        self.resize((5,5))
        self.dmg = dmg
        self.dx,self.dy = trig.speeddeg_xy(self.speed, direction)
        gPlayerProjectiles.add(self)
        self.lastx, self.lasty = -10,-10
    def update(self):
        try:
            if c.master:
                self.rect.centerx += self.dx * c.delta_time
                self.rect.centery += self.dy * c.delta_time
            super().update()
            if abs(self.x - self.rect.centerx) + abs(self.lasty - self.rect.centery) < self.speed/2 or not self in gAll.sprites():
                self.kill()
            self.lastx, self.lasty = self.rect.center
            if self.out_of_bounds():
                self.kill()
        except Exception as e:
            try:
                self.kill()
            except Exception as ex:
                raise Warning(ex)
class Enemy(Object):
    def __init__(self,x,y):
        super().__init__(x,y,"Enemy")
        self.speed = 4
        self.resize((20,20))
        self.dx,self.dy = 0,0
        gEnemies.add(self)
        self.hp = 3

    def update(self):
        try:
            if c.master:
                target = trig.get_nearest_sprite(self,gPlayer)
                if target is not None:
                    angle = trig.angledeg(self.rect.center,target.rect.center)
                    self.dx,self.dy = trig.speeddeg_xy(self.speed,angle)
                    self.rect.centerx += self.dx * c.delta_time
                    self.rect.centery += self.dy * c.delta_time
            super().update()
        except Exception as ex:
            try:
                self.kill()
            except:
                pass
class EnemyProjectile(Object):
    def __init__(self,x,y,direction=0):
        super().__init__(x,y,"Pellet")
        self.speed = 50
        self.resize((10,10))
        self.dx,self.dy = trig.speeddeg_xy(self.speed, direction)
        gEnemyProjectiles.add(self)
        self.lastx, self.lasty = -10,-10
        self.wrap_times = 1
    def update(self):
        try:
            if c.master:
                self.rect.centerx += self.dx * c.delta_time
                self.rect.centery += self.dy * c.delta_time
            super().update()
            if self.wrap_times > 0:
                if self.wrap():
                    self.wrap_times -= 1
            else:
                if self.out_of_bounds():
                    self.kill()
            if abs(self.x - self.rect.centerx) + abs(self.lasty - self.rect.centery) < self.speed/2 or not self in gAll.sprites():
                self.kill()
            self.lastx, self.lasty = self.rect.center

        except Exception as e:
            try:
                self.kill()
            except Exception as ex:
                raise Warning(ex)

class JohnBoss(Object):
    def __init__(self,x,y):
        super().__init__(x,y,"Enemy")
        self.resize((100,100))
        self.size = 100
        gBoss.add(self)
        self.type = "JohnBoss"
        self.hp = 20
        self.speed = 10
        self.dx,self.dy = 0,0
        self.nearest_player = None
        self.target = None
        self.knockback = 0
        self.states = ["roam","backshot"]
        self.state = "transition_to_backshot"
        # self.state = "roam"
        self.state_time = 0
        self._state_start = 0
        self.state_new = True
        self.direction = 0
        self.roam_speed = 20
        self.rotation_speed = 2
        self.last_shot = 0
        self.shoot_type = 0
        self.firerate = 100
    def update(self):
        if c.master:
            self.wrap()
            self.nearest_player = trig.get_nearest_sprite(self,gPlayer)
            if self.state_new:
                self._state_start = p.time.get_ticks()
                self.target = r.choice(gPlayer.sprites())
            self.state_time = p.time.get_ticks() - self._state_start
            match self.state:
                case "roam":
                    if self.state_new:
                        self.direction = r.randint(0,359)

                    dx,dy = trig.speeddeg_xy(self.roam_speed,self.direction)
                    self.direction += r.randint(-2,2)
                    self.rect.centerx += dx * c.delta_time
                    self.rect.centery += dy * c.delta_time
                    if self.state_time > 1000:
                        self.state = "transition_to_backshot"
                        self.state_new = True
                        return
                case "backshot":
                    t = self.target.rect.center
                    a = c.warp_bounds[2]
                    b = c.warp_bounds[3]
                    m1 = (t[0]+a,t[1])
                    m2 = (t[0]-a,t[1])
                    m3 = (t[0],t[1]+b)
                    m4 = (t[0],t[1]-b)
                    m1 = (m1[0],m1[1],trig.distance(self.rect.center,m1))
                    m2 = (m2[0],m2[1],trig.distance(self.rect.center,m2))
                    m3 = (m3[0],m3[1],trig.distance(self.rect.center,m3))
                    m4 = (m4[0],m4[1],trig.distance(self.rect.center,m4))
                    mirror_target = min(m1,m2,m3,m4, key=lambda x: x[2])[0:2]
                    self.desired_direction = trig.angledeg(self.rect.center, mirror_target)
                    self.direction = self.rotate_toward()
                    self.rect.centerx += self.speed * c.delta_time / 4
                    self.rect.centery += self.speed * c.delta_time / 2
                    self.wrap()
                    self.shoot()
                    if self.state_time > 1000:
                        self.state = "transition_to_roam"
                        self.state_new = True
                        return
                case "transition_to_backshot":
                    self.size -= 2
                    self.resize((self.size,self.size))
                    if self.size <= 20:
                        self.state = "backshot"
                        self.state_new = True
                    return
                case "transition_to_roam":
                    self.size += 2
                    self.resize((self.size,self.size))
                    if self.size >= 100:
                        self.state = "roam"
                        self.state_new = True
                    return
            if self.state_new:
                self.state_new = False
        else:
            self.resize((self.size,self.size))
    def shoot(self):
        if p.time.get_ticks() - self.last_shot > self.firerate:
            sfx.shoot()
            self.last_shot = p.time.get_ticks() + r.randint(-40, 40)
            if self.shoot_type == 0:
                EnemyProjectile(self.rect.centerx, self.rect.centery, self.direction)
            if self.shoot_type == 1:
                for i in range(3):
                    EnemyProjectile(self.rect.centerx, self.rect.centery, self.direction+5* (r.random()*2-1) )






class Button(p.sprite.Sprite):
    def __init__(self,x,y,w,h,text,action,color=(255,255,255),size=18,tx=0,ty=0):
        super().__init__()
        gUI.add(self)
        self.action = action
        self.tx, self.ty = tx, ty
        self.text = text
        self.text_object = Text(c.screen,text,(tx+x,ty+y),size=size)
        self.color = color
        self.rect = p.Rect(x,y,w,h)
    def update(self):
        super().update()
        self.text_object(self.text)
        if mouse.click()[0] and self.rect.collidepoint(mouse.position()):
            self.action()
    def draw(self,screen):
        p.draw.rect(c.screen, self.color, self.rect)
        self.text_object.draw(screen)

    def kill(self):
        self.text_object.kill()
        super().kill()

class Slider(p.sprite.Sprite):
    def __init__(self,x,y,w,h,min,max,value,round_to = 1,color=(255,255,255),size=18,tx=0,ty=0):
        super().__init__()
        gUI.add(self)
        self.tx, self.ty = tx, ty
        self.round_to = round_to
        self.text_object = Text(c.screen,value,(tx+x,ty+y),size=size)
        self.color = color
        self.rect = p.Rect(x,y,w,h)
        self.min,self.max = min,max
        self.slider = trig.map(value, min, max, self.rect.left, self.rect.right)
        self.value = value
    def update(self):
        super().update()
        self.value = round(trig.map(self.slider, self.rect.left, self.rect.right, self.min, self.max),self.round_to)
        if self.round_to == 0:
            self.value = int(self.value)
        self.text_object(self.value)

        if mouse.press()[0] and self.rect.collidepoint(mouse.position()):
            self.slider = mouse.position()[0]
    def get_release(self):
        if mouse.release()[0] and self.rect.collidepoint(mouse.position()):
            return True
        return False

    def draw(self,screen):
        p.draw.rect(screen, self.color, self.rect)
        p.draw.circle(screen, (100, 100, 100), (self.slider, self.rect.centery), 10)
        self.text_object.draw(screen)



    def get_value(self):
        return self.value

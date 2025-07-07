import pygame as p
import trig
import events as e
import sound as sfx


master = True
class Text(p.sprite.Sprite):
    def __init__(self,screen,msg,xy,color=(255,255,255),font="Arial",size=18,antialias=True):
        super().__init__()
        gText.add(self)
        self.font = p.font.SysFont(font, size)
        self.msg = msg
        self.color = color
        self.x,self.y = xy
        self.antialias = antialias
        self.screen = screen
        self.text = self.font.render(self.msg, self.antialias, self.color)
        self.text_rect = self.text.get_rect(x=self.x, y=self.y)
    def __call__(self, msg):
        self.msg = msg
        self.text = self.font.render(self.msg, self.antialias, self.color)
        self.text_rect = self.text.get_rect(x=self.x, y=self.y)
    def update(self):
        self.screen.blit(self.text, self.text_rect)

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
    def press(self):
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
wrap_bounds = (0,0,0,0)
gAll = p.sprite.Group()
gPlayer = p.sprite.Group()
gEnemies = p.sprite.Group()
gPlayerProjectiles = p.sprite.Group()
gText = p.sprite.Group()
shooting = (False,0)
sound_events = sfx.sound_events
delta_time = 1




class Object(p.sprite.Sprite):
    def __init__(self,x,y,sprite):
        super().__init__()
        gAll.add(self)
        self.x = x
        self.y = y
        self.sprite = "Assets/Sprites/Png/"+sprite+".png"
        self.mask = p.mask.from_surface(p.image.load(self.sprite))
        self.image = p.image.load(self.sprite)
        self.original_image = self.image
        self.rect = self.image.get_rect()
        self.rect.center = self.x, self.y
        self.delta = 0
        self.hp = 0
        self.desired_direction = 0
        self.direction = 0
        self.acceleration = 0
        self.rotation_speed = 0
        self.dx,self.dy = 0,0
        self.friction_coef = 0.05

    def add_speed(self):
        direction = self.direction
        acceleration = self.acceleration
        dx, dy = trig.speeddeg_xy(acceleration - trig.current_speed(self) / 10, direction)
        self.dx += dx * delta_time
        self.dy += dy * delta_time

    def friction(self):
        self.dx -= self.dx * self.friction_coef * delta_time
        self.dy -= self.dy * self.friction_coef * delta_time

    def hit(self,dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.kill()

    def rotate_toward(self):
        rotation_speed = self.rotation_speed * delta_time
        if abs(self.direction - self.desired_direction) < rotation_speed:
            return self.desired_direction

        direction = trig.get_rotation_direction(self.direction, self.desired_direction)
        new_angle = self.direction + direction * rotation_speed

        # Clamp to avoid overshooting
        if direction == 1 and (self.desired_direction - new_angle + 360) % 360 < rotation_speed:
            return self.desired_direction
        elif direction == -1 and (new_angle - self.desired_direction + 360) % 360 < rotation_speed:
            return self.desired_direction

        return new_angle % 360


    def resize(self,size):
        self.image = p.transform.scale(self.image,size)
        self.rect = self.image.get_rect()
        self.mask = p.mask.from_surface(self.image)
        self.rect.center = self.x, self.y

    def update(self):
        self.rect.centerx, self.rect.centery = self.x, self.y

    def draw(self,screen):
        try:
            if self.image and self.rect:
                super().draw(screen)
        except Exception as e:
            print(f"Chyba při vykreslování: {e}")
    def wrap(self,wrap):
        if self.x > wrap[2]:
            self.x -= wrap[2]-10
        if self.x < wrap[0]:
            self.x += wrap[2]-10
        if self.y > wrap[3]:
            self.y -= wrap[3]-10
        if self.y < wrap[1]:
            self.y += wrap[3]-10
    def out_of_bounds(self):
        if self.x > bounds[2] or self.x < bounds[0] or self.y > bounds[3] or self.y < bounds[1]:
            self.kill()
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
        global shooting
        keys = p.key.get_pressed()
        self.desired_direction = trig.angledeg((self.x, self.y), (mouse.position()))

        self.image = p.transform.rotate(self.original_image, -self.direction)
        self.rect = self.image.get_rect(center=self.rect.center)

        self.direction = self.rotate_toward()

        if mouse.press()[2]:
            self.add_speed()
        self.friction()


        self.x += self.dx * delta_time
        self.y += self.dy * delta_time
        if mouse.click()[0]:
            shooting = e.projectile((self.x,self.y),self.direction,master)
        self.wrap(wrap_bounds)
        super().update()
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
                self.x += self.dx * delta_time
                self.y += self.dy * delta_time
            super().update()
            self.out_of_bounds()
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
                    angle = trig.angledeg((self.x,self.y),(target.x,target.y))
                    self.dx,self.dy = trig.speeddeg_xy(self.speed,angle)
                    self.x += self.dx * delta_time
                    self.y += self.dy * delta_time
            super().update()
        except Exception as e:
            try:
                self.kill()
            except:
                pass


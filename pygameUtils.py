import pygame as p
import trig
gAll = p.sprite.Group()
gText = p.sprite.Group()
delta_time = 1

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
        self.msg = str(msg)
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
        self.delta_time = 1

    def add_speed(self):
        direction = self.direction
        acceleration = self.acceleration
        dx, dy = trig.speeddeg_xy(acceleration - trig.current_speed(self) / 30, direction)
        self.dx += dx * self.delta_time
        self.dy += dy * self.delta_time

    def friction(self):
        self.dx -= self.dx * self.friction_coef * self.delta_time
        self.dy -= self.dy * self.friction_coef * self.delta_time
        if abs(self.dx) < self.friction_coef:
            self.dx = 0
        if abs(self.dy) < self.friction_coef:
            self.dy = 0


    def hit(self,dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.kill()

    def rotate_toward(self):
        rotation_speed = self.rotation_speed * self.delta_time
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
        super().update()
        self.delta_time = delta_time

    def draw(self,screen):
        try:
            if self.image and self.rect:
                super().draw(screen)
        except Exception as e:
            print(f"Chyba při vykreslování: {e}")
    def wrap(self,wrap):
        if self.rect.centerx > wrap[2]:
            self.rect.centerx -= wrap[2]-10
        if self.rect.centerx < wrap[0]:
            self.rect.centerx += wrap[2]-10
        if self.rect.centery > wrap[3]:
            self.rect.centery -= wrap[3]-10
        if self.rect.centery < wrap[1]:
            self.rect.centery += wrap[3]-10
    def out_of_bounds(self,bounds):
        if self.rect.centerx > bounds[2] or self.rect.centerx < bounds[0] or self.rect.centery > bounds[3] or self.rect.centery < bounds[1]:
            self.kill()
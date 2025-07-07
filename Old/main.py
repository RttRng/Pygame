import pygame as g
import math as m
import random as r
import asyncio as a
class Engine:
    def __init__(self):
        self.physics_subs = []
        self.mouse_subs = []
        self.draw_subs = []
        self.mouse_state = g.mouse.get_pressed()
    def physics(self):
        for obj in self.physics_subs:
            obj.tick()
    def draw(self):
        for obj in self.draw_subs:
            obj.update(screen)

    def mouse_event(self):
        d_mouse = (g.mouse.get_pressed()[0]!=self.mouse_state[0],g.mouse.get_pressed()[1]!=self.mouse_state[1],g.mouse.get_pressed()[2]!=self.mouse_state[2])
        self.mouse_state = g.mouse.get_pressed()
        for obj in self.mouse_subs:
            obj.click(g.mouse.get_pos(), self.mouse_state, d_mouse)

class Physics:
    def __init__(self,engine):
        self.x = 0
        self.y = 0
        self.direction = 0
        self.speed = 0
        self.color = "red"
        self.size = 40
        engine.physics_subs.append(self)
        engine.draw_subs.append(self)
    def tick(self):
        self.x += self.speed * m.cos(m.radians(self.direction))
        self.y += self.speed * m.sin(m.radians(self.direction))
    def render(self, screen):
        g.draw.circle(screen, self.color, (self.x,self.y), self.size)

class Player(Physics):
    def __init__(self,engine,constructor):
        super().__init__(engine)
        engine.mouse_subs.append(self)
        self.constructor = constructor
        self.engine = engine
        self.obj = Projectile
    def tick(self):
        keys = g.key.get_pressed()
        if keys[g.K_w]:
            self.y -= self.speed
        if keys[g.K_s]:
            self.y += self.speed
        if keys[g.K_a]:
            self.x -= self.speed
        if keys[g.K_d]:
            self.x += self.speed
    def click(self,pos,state,delta):
        if delta[0] and state[0]:
            self.constructor.new(self.engine,self.obj,(self.x,self.y),pos)
class Projectile(Physics):
    pass


class Hp:
    def __init__(self, engine):
        self.health = 3

    def hit(self):
        self.health -= 1
        if self.health <= 0:
            del self


class Constructor:
    @staticmethod
    def new(engine,cl,source,destination):
        new_object = cl(engine)
        new_object.x = source[0]
        new_object.y = source[1]
        new_object.direction = m.degrees(m.atan2(destination[1]-source[1],destination[0]-source[0]))
        new_object.speed = 10
        new_object.color = "white"
        new_object.size = 12

class Enemy(Physics,Hp):
    def __init__(self,engine,target):
        super().__init__(engine)
        self.target = target
        self.speed = 4
        self.color = "blue"

    def tick(self):
        self.direction = m.degrees(m.atan2(self.target.y-self.y,self.target.x-self.x))
        super().tick()
    def colision(self):
        self.hit()



def spawn_enemy():
    new_enemy = Enemy(engine1,player)


if __name__ == "__main__":
    g.init()
    screen = g.display.set_mode((800, 600))
    clock = g.time.Clock()

    engines = []
    engine1 = Engine()
    engines.append(engine1)
    gun = Constructor()



    player = Player(engine1,gun)
    player.speed = 5

    running = True
    while running:
        for event in g.event.get():
            if event.type == g.QUIT:
                running = False
        screen.fill("purple")
        for e in engines:
            e.mouse_event()
            e.physics()
            e.draw()
        if r.randint(1,60) == 60:
            spawn_enemy()



        clock.tick(60)
        g.display.flip()

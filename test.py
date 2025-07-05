import pygame as g
import math

g.init()
screen = g.display.set_mode((800, 600))
clock = g.time.Clock()
running = True
speed = 5
player_pos = g.Vector2(screen.get_width() / 2, screen.get_height() / 2)
projectiles = []


class Projectile(g.sprite.Sprite):
    def __init__(self, x, y, direction):
        g.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 5

    def tick(self):
        self.x += self.speed * math.cos(self.direction)
        self.y += self.speed * math.sin(self.direction)
        g.draw.circle(screen, "white", (self.x, self.y), 20)


while running:
    for event in g.event.get():
        if event.type == g.QUIT:
            running = False
    screen.fill("purple")
    g.draw.circle(screen, "red", player_pos, 40)

    keys = g.key.get_pressed()
    if keys[g.K_w]:
        player_pos.y -= speed
    if keys[g.K_s]:
        player_pos.y += speed
    if keys[g.K_a]:
        player_pos.x -= speed
    if keys[g.K_d]:
        player_pos.x += speed

    mouse_pos = g.mouse.get_pos()
    mouse_pressed = g.mouse.get_pressed()

    if mouse_pressed[0]:
        dx = mouse_pos[0] - player_pos.x
        dy = mouse_pos[1] - player_pos.y
        angle = math.atan2(dy, dx)
        projectiles.append(Projectile(player_pos.x, player_pos.y, angle))

    for obj in projectiles:
        obj.tick()
    g.display.flip()
    clock.tick(60)
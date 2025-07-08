import pygame as p
import trig
import sound as sfx
import pygameLib as l
events = {"Player2Died":False,"Shooting":False,"ShootingDir":0}
def reset():
    global events
    events.update({"Player2Died": False, "Shooting": False})

def check_collisions_group(groupA, groupB, onHitA=None, onHitB=None):
    collisions = p.sprite.groupcollide(groupA, groupB, False, False)

    for spriteA, collidedBs in collisions.items():
        for spriteB in collidedBs:
            print(f"A: {spriteA}, B: {spriteB}")

            if onHitA is not None:
                onHitA(spriteA)

            if onHitB is not None:
                onHitB(spriteB)


def projectile(playerxy, angle ,master=True):
    sfx.shoot()
    global events
    if master:
        l.Projectile(playerxy[0], playerxy[1], angle)
    else:
        print("SEEEEEEEEEEEEEEEEEEEEEEEEEEEX")
        events["Shooting"],events["ShootingDir"] = True, int(angle)
def correct_sprites(have,want, spawn):
    haveCount = len(have)
    
    wantCount = len(want)
    

    if haveCount > wantCount:
        for i in range(haveCount - wantCount):
            have[-1].kill()

    if haveCount < wantCount:
        for i in range(wantCount - haveCount):
            _new = spawn(-32,-32)


def move_sprites(have,want):
    wantCount = len(want)
    for i in range(wantCount):
        have[i].rect.center = want[i]

def onHit(sprite):
    sprite.hit(1)
    sfx.hit()
def onHitSilent(sprite):
    sprite.hit(1)
def kill(sprite):
    sprite.kill()
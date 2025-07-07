import pygame as p
import trig
import sound as sfx
import pygameLib as l
events = {"Player2Died":False}
def check_collisions_group(groupA,groupB,onHit=None):
    collisions = p.sprite.groupcollide(groupA, groupB, True, True)
    for A in collisions.items():
        for B in A:
            print(f"A: {A}, B: {B}")
            if onHit is not None:
                onHit()

def projectile(playerxy, angle ,master=True):
    sfx.shoot()
    if master:
        return l.Projectile(playerxy[0], playerxy[1], angle)
    else:
        return True, angle
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
        have[i].x, have[i].y = want[i]

import pygame as p
import trig
import sound as sfx
import pygameLib as l
events = {"Player2Died":[False,False],"Shooting":False,"ShootingData":[]}
def reset():
    global events
    events.update({"Player2Died": [False,False], "Shooting": False,"ShootingData":[]})

def projectile(playerxy, angle, dmg ,master=True):
    global events
    if master:
        l.Projectile(playerxy[0], playerxy[1], angle, dmg)
    else:
        print("[LOG] Shooting as client...")
        events["Shooting"] = True
        events["ShootingData"].append([angle,dmg])

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
        have[i].rect.center = want[i][0:2]
        if len(want[i]) > 2:
            extra = want[i][2]
            if extra is not None:
                extra_keys = extra.keys()
                if "size" in extra_keys:
                    have[i].size = extra["size"]
                if "direction" in extra_keys:
                    have[i].direction = extra["direction"]
                if "dmg" in extra_keys:
                    have[i].dmg = extra["dmg"]
                if "type" in extra_keys:
                    have[i].type = extra["type"]
                if "hp" in extra_keys:
                    have[i].hp = extra["hp"]
                if "speed" in extra_keys:
                    have[i].speed = extra["speed"]
                if "dx" in extra_keys:
                    have[i].dx = extra["dx"]
                if "dy" in extra_keys:
                    have[i].dy = extra["dy"]
                if "move_direction" in extra_keys:
                    have[i].move_direction = extra["move_direction"]
                if "knockback" in extra_keys:
                    have[i].knockback = extra["knockback"]
                if "target" in extra_keys:
                    have[i].target = extra["target"]
                if "friction_coef" in extra_keys:
                    have[i].friction_coef = extra["friction_coef"]
                if "tx" in extra_keys:
                    have[i].tx = extra["tx"]
                if "ty" in extra_keys:
                    have[i].ty = extra["ty"]



def check_collisions_group(groupA, groupB, onHitA=None, onHitB=None):
    collisions = p.sprite.groupcollide(groupA, groupB, False, False)

    for spriteA, collidedBs in collisions.items():
        for spriteB in collidedBs:
            print(f"[LOG] Collision: A: {spriteA}, B: {spriteB}")
            print(f"[LOG] Dmg: A: {spriteA.dmg}, B: {spriteB.dmg}")

            if onHitA is not None:
                angle = trig.angledeg(spriteA.rect.center, spriteB.rect.center)
                onHitA(spriteA,spriteB.dmg,angle)

            if onHitB is not None:
                angle = trig.angledeg(spriteB.rect.center, spriteA.rect.center)
                onHitB(spriteB,spriteA.dmg,angle)


def onHit(sprite,dmg,angle):
    sprite.hit(dmg,angle)
    sfx.hit()
def onHitSilent(sprite,dmg,angle):
    sprite.hit(dmg,angle)

def kill(sprite,dmg,angle):
    sprite.kill()


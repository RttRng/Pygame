import pygameLib as l
import networking as n

import math as m
import pygame as p
import random as r
import asyncio as a
import socket as s
import threading as t

import trig

if __name__ == "__main__":
    l.size = (800,600)
    l.bounds = (-50,-50,l.size[0]+50,l.size[1]+50)
    p.init()
    screen = p.display.set_mode(l.size)
    clock = p.time.Clock()


    mouse = l.mouse
    player = l.Player(400,300)
    font = p.font.SysFont("Arial", 18)
    port = 42069
    ip = "25.21.131.22"
    #ip = "192.168.0.150"
    net = False

    running = True
    msg1 = "H to Host, C to Connect"
    msg2 = ip

    def callback(msg):
        
        player2.x,player2.y = msg["Player"]
        if not l.master:
            myEnemies = len(l.gEnemies.sprites())
            myProjectiles = len(l.gPlayerProjectiles.sprites())
            recEnemies = len(msg["Enemies"])
            recProjectiles = len(msg["Projectiles"])

            if myEnemies > recEnemies:
                for i in range(myEnemies-recEnemies):
                    l.gEnemies.sprites()[-1].kill()
            if myProjectiles > recProjectiles:
                for i in range(myProjectiles-recProjectiles):
                    l.gPlayerProjectiles.sprites()[-1].kill()
            if myEnemies < recEnemies:
                for i in range(recEnemies-myEnemies):
                    l.gEnemies.add(l.Enemy(-32,-32))
            if myProjectiles < recProjectiles:
                for i in range(recProjectiles-myProjectiles):
                    l.gPlayerProjectiles.add(l.Projectile(-32,-32,0))

            for i in range(recEnemies):
                l.gEnemies.sprites()[i].x,l.gEnemies.sprites()[i].y = msg["Enemies"][i]
            for i in range(recProjectiles):
                l.gPlayerProjectiles.sprites()[i].x,l.gPlayerProjectiles.sprites()[i].y = msg["Projectiles"][i]

        sound = msg["Sound_events"]
        if sound["hit"]:
            l.hit.play()
        if sound["shoot"]:
            l.shoot.play()



        if l.master:
            if msg["Shooting"][0]:
                l.Events.projectile((player2.x,player2.y),(msg["Shooting"][1],msg["Shooting"][2]))


########################################################################################################################
    while running:
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
        keys = p.key.get_pressed()
        screen.fill("purple")
        mouse.update()

        if l.master:
            if r.randint(1,20)==20:
                spawnx,spawny = trig.speeddeg_xy(500+r.randint(0,200),r.randint(0,360))
                l.Enemy(400+spawnx,  300+spawny)

            l.Events.check_collisions()
        l.gAll.update()
        l.gAll.draw(screen)
        if net:
            if l.master:
                data = {"Player":(player.x,player.y),
                        "Enemies":[(i.x,i.y)for i in l.gEnemies.sprites()],
                        "Projectiles":[(i.x,i.y)for i in l.gPlayerProjectiles.sprites()],
                        "Sound_events":l.sound_events}
            else:
                data = {"Player":(player.x,player.y),
                        "Shooting":l.shooting,
                        "Sound_events":l.sound_events}
#
            l.shooting = (False,0,0)
            for i in l.sound_events.keys():
                print(i)
                l.sound_events[i] = False

            networkManager.send(data)
        else:
            if keys[p.K_h] or keys[p.K_c]:
                if keys[p.K_h]:
                    networkManager = n.Host(port,callback)
                    networkManager.start()
                    msg1 = "Hosting"
                    msg2 = str(networkManager.client_address[0])+":"+str(networkManager.client_address[1])

                elif keys[p.K_c]:
                    networkManager = n.Client(callback)
                    networkManager.connect(ip,port)
                    l.master = False
                    msg1 = "Connected"
                    msg2 = ip+":"+str(port)
                net = True
                player2 = l.Player2(400, 300)


        ipText = "None"
        text1 = font.render(msg1, True, (255, 255, 255))  # White text
        text1_rect = text1.get_rect(x=10, y=10)
        text2 = font.render(msg2, True, (255, 255, 255))
        text2_rect = text2.get_rect(x=10, y=30)
        screen.blit(text1, text1_rect)  # Draw text
        screen.blit(text2, text2_rect)




        clock.tick(30)
        p.display.set_caption(
            "FPS: " + str(round(clock.get_fps(), 1))
        )
        p.display.flip()

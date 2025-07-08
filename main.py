import trig
import pygame as p
import random as r
from networking import *
from pygameLib import *
import pygameLib as l
import events as e
import sound as sfx
import threading
from pygameUtils import delta_time as new_delta_time
host = None
client = None
def initialize_network(isHost=True):
    global host, client
    if isHost:
        host = Host(12345, callback_host)
    else:
        client = Client("192.168.0.150", 12345, callback_client)


def recieve_update(type,data):
    print(f"[CALLBACK] Type: {type} Data: {data}")

    ev = data["Events"]
    if ev["Player2Died"]:
        player2.kill()


    px2, py2 = data["Player"]
    if px2 is None or py2 is None:
        if player2 in gPlayer.sprites():
            player2.kill()
    else:
        player2.rect.center = data["Player"]
    sound = data["Sound_events"]
    if sound["hit"]:
        sfx.hit()
    if sound["shoot"]:
        sfx.shoot()


def callback_host(type,data):
    if type == "UPDATE":
        recieve_update(type,data)
        ev = data["Events"]
        if ev["Shooting"]:
            e.projectile(player2.rect.center, ev["ShootingDir"])
    else:
        print(f"[CALLBACK] Type: {type}")
def callback_client(type,data):
    if type == "UPDATE":
        recieve_update(type,data)
        e.correct_sprites(gEnemies.sprites(), data["Enemies"], Enemy)
        e.move_sprites(gEnemies.sprites(), data["Enemies"])
        e.correct_sprites(gPlayerProjectiles.sprites(), data["Projectiles"], Projectile)
        e.move_sprites(gPlayerProjectiles.sprites(), data["Projectiles"])
    else:
        print(f"[CALLBACK] Type: {type}")
def send(isHost=True):
    try:
        if player in gPlayer.sprites():
            px, py = player.rect.center
        else:
            px, py = None, None
        data = {"Player": (px, py),
                "Sound_events": sound_events,
                "Events": e.events}
        if isHost:
            data.update({
                    "Enemies": [i.rect.center for i in gEnemies.sprites()],
                    "Projectiles": [i.rect.center for i in gPlayerProjectiles.sprites()],
            })

            host.send("UPDATE", data)
            reset_events()
        else:
            client.send("UPDATE",data)
            reset_events()
    except:
        pass
def reset_events():
    sfx.reset()
    e.reset()


screen_size = (1920, 1080)
SIZE = screen_size
bounds = (-50, -50, screen_size[0] + 50, screen_size[1] + 50)
warp_bounds = (0, 0, screen_size[0], screen_size[1])
delta_time = 1

if __name__ == "__main__":
    running = True
    while running:
        fullscreen = True
        p.init()
        screen = p.display.set_mode(screen_size, p.FULLSCREEN)
        clock = p.time.Clock()
        player = Player(400,300)
        FONT = p.font.SysFont("Arial", 18)
        PORT = 42069
        # IP = "25.21.131.22"
        IP = "192.168.0.150"
        fp = 60
        net = False


        msg1 = "H to Host, C to Connect"
        msg2 = IP
        master = True
        spawn = False
        reset = False
        text1 = Text(screen,"msg1",(10,10))
        text2 = Text(screen,"msg2",(10,30))
        text3 = Text(screen,"msg3",(10,50))
        text4 = Text(screen,"msg4",(10,70))
        info = p.display.Info()
        screen_width = info.current_w
        screen_height = info.current_h
        screen_size = screen_width, screen_height
        bounds = (-50, -50, screen_size[0] + 50, screen_size[1] + 50)
        warp_bounds = (0, 0, screen_size[0], screen_size[1])
        l.screen_size = screen_size
        l.bounds = bounds
        l.warp_bounds = warp_bounds
    ########################################################################################################################
        while running:
            for event in p.event.get():
                if event.type == p.QUIT:
                    running = False
                if event.type == p.KEYDOWN:
                    if event.key == p.K_ESCAPE:
                        running = False
                    if event.key == p.K_SPACE:
                        spawn = not spawn
                    if event.key == p.K_r:
                        reset = True
                    if event.key == p.K_s:
                        fp -= 5
                    if event.key == p.K_w:
                        fp += 5
                    if event.key == p.K_F11:
                        fullscreen = not fullscreen
                        if fullscreen:
                            screen = p.display.set_mode(screen_size, p.FULLSCREEN)
                            info = p.display.Info()
                            screen_width = info.current_w
                            screen_height = info.current_h
                            screen_size = screen_width, screen_height
                        else:
                            screen = p.display.set_mode(SIZE)

                        bounds = (-50, -50, screen_size[0] + 50, screen_size[1] + 50)
                        warp_bounds = (0, 0, screen_size[0], screen_size[1])
                        l.screen_size = screen_size
                        l.bounds = bounds
                        l.warp_bounds = warp_bounds

            if reset:
                for i in gAll.sprites():
                    i.kill()
                for i in gText.sprites():
                    i.kill()
                break
            keys = p.key.get_pressed()

            screen.fill("purple")
            mouse.update()

            if master:
                if r.randint(1,int(round(clock.get_fps(), 0))+1)==1:
                    if spawn:
                        spawnx,spawny = trig.speeddeg_xy(screen_size[0] / 2 + screen_size[1] / 2 + r.randint(0, 200), r.randint(0, 360))
                        Enemy(screen_size[0] / 2 + spawnx, screen_size[1] / 2 + spawny)

                e.check_collisions_group(gPlayerProjectiles,gEnemies,e.kill,e.onHit)
                e.check_collisions_group(gPlayer,gEnemies,e.onHit,e.kill)
            new_delta_time = delta_time
            gAll.update()
            gAll.draw(screen)


            if net:
                if player in gPlayer.sprites():
                    px,py = player.x,player.y
                else:
                    px,py = None,None
                send(master)
            else:
                if keys[p.K_h] or keys[p.K_c]:
                    net = True
                    player2 = Player2(400, 300)
                    if keys[p.K_h]:
                        initialize_network(isHost=True)
                        msg1 = "Hosting"
                        msg2 = "Sex?"

                    elif keys[p.K_c]:
                        initialize_network(isHost=False)
                        master = False
                        msg1 = "Connected"
                        msg2 = IP + ":" + str(PORT)





            ipText = "None"
            msg2 = str(delta_time)
            msg3 = "Spawning: " + str(spawn)
            msg4 = "HP: " + str(player.hp)
            text1(msg1)
            text2(msg2)
            text3(msg3)
            text4(msg4)
            gText.update()


            l.master = master
            clock.tick(fp)
            fps = round(clock.get_fps(), 1)
            delta_time = 30 / (fps+0.0001)
            p.display.set_caption(
                "FPS: " + str(fps)
            )
            p.display.flip()
        try:
            for thread in threading.enumerate():
                if thread != threading.current_thread() and thread != threading.main_thread():
                    thread.join()
            host.send("DISCONNECT")
        except:
            pass
        try:
            for thread in threading.enumerate():
                if thread != threading.current_thread() and thread != threading.main_thread():
                    thread.join()
            client.send("DISCONNECT")
        except:
            pass

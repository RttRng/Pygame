import trig
import pygame as p
import random as r
import networking as n
import pygameLib as l
import events as e
import sound as sfx
class Network:
    def __bool__(self):
        return True
    def __init__(self):
        global player2
        global networkManager
    @staticmethod
    def callback(msg):
        ev = msg["Events"]
        if ev["Player2Died"]:
            player2.kill()
        px2, py2 = msg["Player"]
        if px2 is None or py2 is None:
            if player2 in l.gPlayer.sprites():
                player2.kill()
        else:
            player2.x, player2.y = msg["Player"]
        sound = msg["Sound_events"]
        if sound["hit"]:
            sfx.hit()
        if sound["shoot"]:
            sfx.shoot()

    @staticmethod
    def callback_host(msg):
        Network.callback(msg)
        if msg["Shooting"][0]:
            e.projectile((player2.x, player2.y), msg["Shooting"][1])

    @staticmethod
    def callback_client(msg):
        Network.callback(msg)
        e.correct_sprites(l.gEnemies.sprites(), msg["Enemies"], l.Enemy)
        e.move_sprites(l.gEnemies.sprites(), msg["Enemies"])
        e.correct_sprites(l.gPlayerProjectiles.sprites(), msg["Projectiles"], l.Projectile)
        e.move_sprites(l.gPlayerProjectiles.sprites(), msg["Projectiles"])
    @staticmethod
    def send():
        if player in l.gPlayer.sprites():
            px, py = player.x, player.y
        else:
            px, py = None, None
        data = {"Player": (px, py),
                "Sound_events": l.sound_events,
                "Events": e.events}
        return data
    @staticmethod
    def sendHost():
        data = Network.send()
        data.update({
                "Enemies": [(i.x, i.y) for i in l.gEnemies.sprites()],
                "Projectiles": [(i.x, i.y) for i in l.gPlayerProjectiles.sprites()],
        })
        networkManager.send(data)
        Network.reset()
    @staticmethod
    def sendClient():
        data = Network.send()
        data.update({
                "Shooting": l.shooting
        })
        networkManager.send(data)
        Network.reset()
    @staticmethod
    def reset():
        l.shooting = (False, 0)
        for i in l.sound_events.keys():
            l.sound_events[i] = False
        for i in e.events.keys():
            e.events[i] = False

if __name__ == "__main__":
    running = True
    while running:

        l.size = (800,600)
        l.bounds = (-50,-50,l.size[0]+50,l.size[1]+50)
        l.wrap_bounds = (0,0,l.size[0],l.size[1])
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


        msg1 = "H to Host, C to Connect"
        msg2 = ip

        spawn = False
        reset = False

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

            if reset:
                for i in l.gAll.sprites():
                    i.kill()
                break
            keys = p.key.get_pressed()

            screen.fill("purple")
            mouse.update()

            if l.master:
                if r.randint(1,20)==20:
                    if spawn:
                        spawnx,spawny = trig.speeddeg_xy(500+r.randint(0,200),r.randint(0,360))
                        l.Enemy(400+spawnx,  300+spawny)

                e.check_collisions_group(l.gPlayerProjectiles,l.gEnemies,sfx.hit)
                e.check_collisions_group(l.gPlayer,l.gEnemies,sfx.hit)
            l.gAll.update()
            l.gAll.draw(screen)
            if net:
                if player in l.gPlayer.sprites():
                    px,py = player.x,player.y
                else:
                    px,py = None,None
                if l.master:
                    Network.sendHost()
                else:
                    Network.sendClient()
            else:
                if keys[p.K_h] or keys[p.K_c]:
                    net = Network()
                    player2 = l.Player2(400, 300)
                    if keys[p.K_h]:
                        networkManager = n.NetworkManager(net.callback_host, is_host=True)
                        networkManager.start(port)
                        msg1 = "Hosting"
                        msg2 = str(networkManager.client_address[0])+":"+str(networkManager.client_address[1])

                    elif keys[p.K_c]:
                        networkManager = n.NetworkManager(net.callback_client, is_host=False)
                        networkManager.start(port,ip)
                        l.master = False
                        msg1 = "Connected"
                        msg2 = ip+":"+str(port)





            ipText = "None"
            msg3 = "Spawning: " + str(spawn)

            text1 = font.render(msg1, True, (255, 255, 255))  # White text
            text1_rect = text1.get_rect(x=10, y=10)
            text2 = font.render(msg2, True, (255, 255, 255))
            text2_rect = text2.get_rect(x=10, y=30)
            text3 = font.render(msg3, True, (255, 255, 255))
            text3_rect = text3.get_rect(x=10, y=50)
            screen.blit(text1, text1_rect)  # Draw text
            screen.blit(text2, text2_rect)
            screen.blit(text3, text3_rect)




            clock.tick(30)
            p.display.set_caption(
                "FPS: " + str(round(clock.get_fps(), 1))
            )
            p.display.flip()

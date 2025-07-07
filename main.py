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
        text1 = l.Text(screen,"msg1",(10,10))
        text2 = l.Text(screen,"msg2",(10,30))
        text3 = l.Text(screen,"msg3",(10,50))
        text4 = l.Text(screen,"msg4",(10,70))
        fp = 60

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

            if reset:
                for i in l.gAll.sprites():
                    i.kill()
                break
            keys = p.key.get_pressed()

            screen.fill("purple")
            mouse.update()

            if l.master:
                if r.randint(1,int(round(clock.get_fps(), 0))+1)==1:
                    if spawn:
                        spawnx,spawny = trig.speeddeg_xy(500+r.randint(0,200),r.randint(0,360))
                        l.Enemy(400+spawnx,  300+spawny)

                e.check_collisions_group(l.gPlayerProjectiles,l.gEnemies,e.kill,e.onHit)
                e.check_collisions_group(l.gPlayer,l.gEnemies,e.onHit,e.kill)
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
            msg4 = "HP: " + str(player.hp)
            text1(msg1)
            text2(msg2)
            text3(msg3)
            text4(msg4)
            l.gText.update()



            clock.tick(fp)
            fps = round(clock.get_fps(), 1)
            l.delta_time = 30 / (fps+0.0001)
            p.display.set_caption(
                "FPS: " + str(fps)
            )
            p.display.flip()

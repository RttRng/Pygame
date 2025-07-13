import pygame as p

import events
from control import c
from networkingLib import *
from pygameLib import *
from pygameUtils import *

class SceneManager:
    def __init__(self):
        self.scenes = {"MainMenu": MainMenu, "GameScene": GameScene}
        self.overlays = {"Pause": PauseScene}
        self.net = None
        self.active_scene = None
        self.active_overlays = {"Pause":None}
    def start_network(self, ip, port, isHost=True):
        self.net = NetworkOverlay(ip, port, isHost)
    def change_scene(self, scene_name):
        if self.active_scene is not None:
            self.active_scene.__del__()
        self.add_scene(scene_name)
    def toggle_overlay(self, overlay_name):
        if overlay_name in self.overlays:
            if self.is_overlay_active(overlay_name):
                self.active_overlays[overlay_name] = None
            else:
                self.active_overlays[overlay_name] = self.overlays[overlay_name]()
        else:
            print(f"[ERROR] Overlay {overlay_name} not found.")
    def is_overlay_active(self, overlay_name):
        try:
            return self.active_overlays[overlay_name] is not None
        except:
            print(f"[ERROR] Overlay {overlay_name} not found.")


    def add_scene(self, scene_name):
        self.active_scene = self.scenes[scene_name]()
    def update(self):
        self.active_scene.update()
        for overlay in self.active_overlays.values():
            if overlay is not None:
                overlay.update()
    def draw(self, screen):
        self.active_scene.draw(screen)
        for overlay in self.active_overlays.values():
            if overlay is not None:
                overlay.draw(screen)
        c.output_to_display()
    def handle_events(self, events):
        mouse.update()
        for event in events:
            if event.type == p.QUIT:
                c.running = False
            if event.type == p.USEREVENT+1:
                sfx.track_ended()
        self.active_scene.handle_events(events)
        for overlay in self.active_overlays.values():
            if overlay is not None:
                overlay.handle_events(events)

class Scene:
    def __init__(self):
        self.objects = p.sprite.Group()

    def handle_events(self, events):
        pass
    def draw(self, screen):
        for i in self.objects.sprites():
            i.draw(screen)
    def update(self):
        c.delta_time = 30/c.clock.get_fps()
        for i in self.objects.sprites():
            i.update()
    def __del__(self):
        for i in self.objects.sprites():
            i.kill()
        self.objects.empty()

class MainMenu(Scene):
    def __init__(self):
        super().__init__()
        self.text1 = Text(c.screen, "", (10, 10))
        self.text2 = Text(c.screen, "", (10, 30))
        self.button1 = Button(100, 50, 55, 38, "Start", self.start_game, color=(0, 255, 0), tx=10, ty=10)
        self.slider1 = Slider(55, 100, 100, 20, 0, 100, c.sfxvolume, tx=110)
        self.slider2 = Slider(55, 150, 100, 20, 0, 100, c.musicvolume, tx=110)
        self.slider3 = Slider(55, 200, 100, 20, 0, 1, c.loadout, tx=110, round_to=0)
        self.slider4 = Slider(55, 250, 100, 20, 0, 3, c.skin, tx=110, round_to=0)
        self.button2 = Button(100,300,50,38,"Host",self.start_host, color=(0, 0, 255), tx=10, ty=10)
        self.button3 = Button(200,300,70,38,"Connect",self.start_client, color=(0, 0, 255), tx=10, ty=10)
        self.showcase = Showcase(300,260)
        self.showcase2 = None
        self.objects.add(self.showcase)
        self.objects.add(self.text1)
        self.objects.add(self.text2)
        self.objects.add(self.button1)
        self.objects.add(self.button2)
        self.objects.add(self.button3)
        self.objects.add(self.slider1)
        self.objects.add(self.slider2)
        self.objects.add(self.slider3)
        self.objects.add(self.slider4)
        self.ready = False
        self.ready2 = True
        self.solo = True
        sfx.main_theme()
        self.msg2 = "Not Connected"
        self.showcase.update_sprite(0)
    def set_ready2(self):
        if self.ready and self.ready2:
            sm.change_scene("GameScene")
    def start_game(self):
        if self.solo:
            sm.change_scene("GameScene")
        else:
            self.ready = True
            if c.master:
                sm.net.host.send("READY", {"Name":"Host"})
            else:
                sm.net.client.send("READY", {"Name":"Client"})
            self.button1.text = "Ready"
            self.button1.color = (0, 255, 0)
            if self.ready and self.ready2:
                sm.change_scene("GameScene")
    def handle_events(self, events):
        for event in events:
            if event.type == p.KEYDOWN:
                if event.key == p.K_F1:
                    c.toggle_fullscreen()


    def update(self):
        self.text1("Main Menu")
        self.text2(self.msg2)
        c.sfxvolume = self.slider1.get_value()
        if self.slider1.get_release(): sfx.hit()
        c.musicvolume = self.slider2.get_value()
        c.loadout = self.slider3.get_value()
        c.skin = self.slider4.get_value()
        self.showcase.update_sprite(c.skin)
        if self.showcase2 is not None:
            self.showcase2.update_sprite(c.skin2)
            if c.master:
                sm.net.host.send("SKIN", {"Skin":c.skin})
            else:
                sm.net.client.send("SKIN", {"Skin":c.skin})

        sfx.apply_volume()
        for i in self.objects.sprites():
            i.update()
        self.slider1.text_object("SFX: " + str(c.sfxvolume))
        self.slider2.text_object("Music: " + str(c.musicvolume))
        self.slider3.text_object("Loadout: " + str(["Sniper","Shotgun"][c.loadout]))
        self.slider4.text_object("Skin: " + str(["Heart","Spade","Club","Diamond"][c.skin]))
    def draw(self, screen):
        screen.fill("black")
        super().draw(screen)
    def start_host(self):
        sm.start_network(c.IP, c.PORT, True)
        sm.net.callback = self.callback
        self.button2.kill()
        self.button3.kill()
        self.msg2 = "Hosting"
    def  start_client(self):
        sm.start_network(c.IP, c.PORT, False)
        sm.net.callback = self.callback
        c.master = False
        self.button2.kill()
        self.button3.kill()
        self.msg2 = "Connecting"
        sm.net.client.send("CONNECT", {"Name":"Client"})
    def __del__(self):
        super().__del__()

    def callback(self,isHost,type,data):
        if type == "CONNECT":
            self.showcase2 = Showcase(350, 260)
            self.objects.add(self.showcase2)
            print(f"[CALLBACK] Type: {type} Data: {data}")
            self.msg2 = "Connected"
            self.button1.text = "Not ready"
            self.button1.color = (255,0,0)
            self.ready2 = False
            self.solo = False
            if data["Name"] == "Client" and isHost:
                sm.net.host.send("CONNECT", {"Name": "Host"})
        if type == "READY" or type == "UPDATE":
            self.ready2 = True
            self.set_ready2()
        if type == "SKIN":
            self.showcase2.update_sprite(data["Skin"])
            c.skin2 = data["Skin"]


class GameScene(Scene):
    def __init__(self):
        super().__init__()
        self.text1 = Text(c.screen, "", (10, 10))
        self.text2 = Text(c.screen, "", (10, 30))
        self.text3 = Text(c.screen, "", (10, 50))
        self.text4 = Text(c.screen, "", (10, 70))
        self.text5 = Text(c.screen, "", (10, 90))
        self.text6 = Text(c.screen, "", (10, 110))
        self.objects.add(self.text1)
        self.objects.add(self.text2)
        self.objects.add(self.text3)
        self.objects.add(self.text4)
        self.objects.add(self.text5)
        self.objects.add(self.text6)
        self.player = Player(c.canvas_size[0] / 2, c.canvas_size[1] / 2,c.skin)
        self.objects.add(self.player)
        self.player2 = None
        if sm.net is not None:
            if sm.net.callback is not None:
                sm.net.callback = self.callback


    def update(self):
        if sm.is_overlay_active("Pause"):
            return
        super().update()
        if c.master:
            if r.randint(1, int(round(c.clock.get_fps(), 0)) + 1) == 1:
                if c.spawn:
                    spawnx, spawny = trig.speeddeg_xy(
                        c.canvas_size[0] / 2 + c.canvas_size[1] / 2 + r.randint(0, 200),
                        r.randint(0, 360))
                    AsteroidBig(c.canvas_size[0] / 2 + spawnx, c.canvas_size[1] / 2 + spawny,r.randint(50,c.canvas_size[0]-50),r.randint(50,c.canvas_size[1]-50))
            e.check_collisions_group(gPlayerProjectiles, gEnemies, e.kill, e.onHit)
            e.check_collisions_group(gPlayer, gEnemies, e.onHit, e.onHitSilent)
            e.check_collisions_group(gPlayer, gBoss, e.onHit, e.onHitSilent)
            e.check_collisions_group(gPlayer,gEnemyProjectiles,e.onHit,e.kill)
            e.check_collisions_group(gPlayerProjectiles, gBoss, e.kill, e.onHit)
            e.check_collisions_group(gPlayer,gAsteroids,e.onHit,e.onHitSilent)
            e.check_collisions_group(gPlayerProjectiles, gAsteroids, e.kill, e.onHit)

        gAll_copy = gAll.copy()
        try:
            gAll_copy.update()
        except Exception as ex:
            print(f"[ERROR] Operation with gAll failed: {ex}")


        msg1 = "FPS: " + str(round(c.clock.get_fps(), 1))
        msg2 = "Delta coef: " + str(c.delta_time)
        if c.master:
            msg3 = "Spawning: " + str(c.spawn)
        else:
            msg3 = "Connected to: " + c.IP + ":" + str(c.PORT) + ""
        msg4 = "HP: " + str(self.player.hp)
        msg5 = "Press esc to pause"
        msg6 = "Scale: "+str(round(c.scale,3)*100) + "%"
        self.text1(msg1)
        self.text2(msg2)
        self.text3(msg3)
        self.text4(msg4)
        self.text5(msg5)
        self.text6(msg6)
        if sm.net is not None:
            self.send()

    def draw(self, screen):
        screen.fill("purple")
        if sm.is_overlay_active("Pause"):
            return
        super().draw(screen)
        gAll_copy = gAll.copy()
        try:
            gAll_copy.draw(screen)
        except Exception as ex:
            print(f"[ERROR] Operation with gAll failed: {ex}")

    def handle_events(self, events):
        if sm.is_overlay_active("Pause"):
            for event in events:
                if event.type == p.KEYDOWN:
                    if event.key == p.K_F1:
                        c.toggle_fullscreen()
                    if event.key == p.K_ESCAPE:
                        sm.toggle_overlay("Pause")
        else:
            for event in events:
                if event.type == p.KEYDOWN:
                    if event.key == p.K_SPACE:
                        c.spawn = not c.spawn
                    if event.key == p.K_ESCAPE:
                        sm.toggle_overlay("Pause")
                    if event.key == p.K_BACKSPACE:
                        JohnBoss(c.canvas_size[0] / 2, c.canvas_size[1] / 2)

        if sm.net is not None and self.player2 is None:
            self.player2 = Player2(c.canvas_size[0], c.canvas_size[1],c.skin2)
            self.objects.add(self.player2)

    def callback(self,isHost, type, data):
        if isHost:
            if type == "UPDATE":
                self.recieve_update(type, data)
                ev = data["Events"]
                if ev["Player2Died"][0]:
                    self.player2.kill()
                if ev["Shooting"]:
                    for i in ev["ShootingData"]:
                        e.projectile(self.player2.rect.center, i[0], i[1],c.master)
            else:
                print(f"[CALLBACK HOST] Type: {type}")
        else:
            if type == "UPDATE":
                self.recieve_update(type, data)
                ev = data["Events"]
                if ev["Player2Died"][0]:
                    self.player2.kill()
                if ev["Player2Died"][1]:
                    self.player.kill()


                e.correct_sprites(gBoss.sprites(), data["Boss"]["JohnBoss"], JohnBoss)
                e.move_sprites(gBoss.sprites(), data["Boss"]["JohnBoss"])

                e.correct_sprites(gEnemyProjectiles.sprites(), data["EProjectiles"], EnemyProjectile)
                e.move_sprites(gEnemyProjectiles.sprites(), data["EProjectiles"])
                e.correct_sprites(gEnemies.sprites(), data["Enemies"], Enemy)
                e.move_sprites(gEnemies.sprites(), data["Enemies"])
                e.correct_sprites(gPlayerProjectiles.sprites(), data["Projectiles"], Projectile)
                e.move_sprites(gPlayerProjectiles.sprites(), data["Projectiles"])

                e.correct_sprites(gAsteroids.sprites(), data["Asteroids"]["Big"], AsteroidBig)
                e.move_sprites(gAsteroids.sprites(), data["Asteroids"]["Big"])

                e.correct_sprites(gAsteroids.sprites(), data["Asteroids"]["Small"], AsteroidSmall)
                e.move_sprites(gAsteroids.sprites(), data["Asteroids"]["Small"])
            else:
                print(f"[CALLBACK CLIENT] Type: {type}")
    def recieve_update(self, type, data):
        print(f"[CALLBACK] Type: {type} Data: {data}")
        ev = data["Events"]


        px2, py2 = data["Player"][0:2]
        if px2 is None or py2 is None:
            if self.player2 in gPlayer.sprites():
                self.player2.kill()
        else:
            self.player2.rect.center = data["Player"][0:2]
            self.player2.direction = data["Player"][4]
            if not c.master:
                self.player2.hp = data["Player"][2]
                self.player.hp = data["Player"][3]
        sound = data["Sound_events"]
        if sound["hit"]:
            sfx.hit()
        if sound["shoot"]:
            sfx.shoot()
    def send(self):
        try:
            e.events["Player2Died"] =  not self.player.alive, not self.player2.alive
            if self.player in gPlayer.sprites():
                px, py = self.player.rect.center
                hp = self.player.hp
                hp2 = self.player2.hp
                d = self.player.direction
            else:
                px, py, hp, hp2, d = None, None, 0, 0, 0
            data = {"Player": (px, py, hp, 0, d),
                    "Sound_events": sound_events,
                    "Events": e.events}
            if sm.net.isHost:
                data.update({
                    "Player": (px, py, hp, hp2, d),
                    "Enemies": [i.rect.center for i in gEnemies.sprites()],
                    "Projectiles": [(i.rect.centerx,i.rect.centery,{"dmg":i.dmg}) for i in gPlayerProjectiles.sprites()],
                    "EProjectiles": [i.rect.center for i in gEnemyProjectiles.sprites()],
                    "Boss": {a:[(i.rect.centerx,i.rect.centery,{"size":i.size})for i in filter(lambda x:x.type == a,[b for b in gBoss.sprites()])] for a in c.list_bosses},
                    "Asteroids": {a: [(i.rect.centerx, i.rect.centery, {"size": i.size, "hp": i.hp, "direction": i.direction,"move_direction": i.move_direction, "speed": i.speed}) for i in filter(lambda x: x.type == a, [b for b in gAsteroids.sprites()])] for a in c.list_asteroids},

                })


                sm.net.host.send("UPDATE", data)
                sm.net.reset_events()
            else:
                sm.net.client.send("UPDATE", data)
                sm.net.reset_events()
        except Exception as ex:
            print(f"[ERROR] Sending failed: {ex}")

class PauseScene(Scene):
    def __init__(self):
        super().__init__()
        self.text1 = Text(c.screen, "Pause", (10, 10))
        self.text2 = Text(c.screen, "Press ESC to continue", (10, 30))
        self.text3 = Text(c.screen, "Press F1 to toggle fullscreen", (10, 50))
        self.slider1 = Slider(100, 100, 100, 20, 0, 100, c.sfxvolume, tx=-70)
        self.slider2 = Slider(100, 150, 100, 20, 0, 100, c.musicvolume, tx=-80)
        self.objects.add(self.text1)
        self.objects.add(self.text2)
        self.objects.add(self.text3)
        self.objects.add(self.slider1)
        self.objects.add(self.slider2)

    def __eq__(self, other):
        return isinstance(other, PauseScene)


    def update(self):
        c.sfxvolume = self.slider1.get_value()
        if self.slider1.get_release(): sfx.hit()
        c.musicvolume = self.slider2.get_value()
        sfx.apply_volume()
        for i in self.objects.sprites():
            i.update()
        self.slider1.text_object("SFX: " + str(c.sfxvolume))
        self.slider2.text_object("Music: " + str(c.musicvolume))



class NetworkOverlay(Scene):
    def __init__(self, ip, port, isHost=True):
        super().__init__()
        self.isHost = isHost
        if isHost:
            self.host = Host(port, self.callback_host)
        else:
            self.client = Client(ip, port, self.callback_client)
        self.callback = None

    def callback_host(self,type, data):
        self.callback(True,type, data)

    def callback_client(self,type, data):
        self.callback(False,type,data)

    def reset_events(self):
        sfx.reset()
        e.reset()


sm = SceneManager()

import time
import requests
import threading
import os
from functools import partial
from config import *
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from ui.modals import *
from ui.buttons import MenuBtn, DummyBtn


class LobbyScreen(Screen):
    active_pop = None  # active popup on the screen
    player_list = ObjectProperty(None)  # layout for players
    lobby_code = ObjectProperty(None)  # layout for players

    def __init__(self, CApp, **kwargs):
        super(LobbyScreen, self).__init__(**kwargs)
        self.app = CApp
        self.secret = None  # secret required for server messages
        self.lobby_thread = None
        self.lobby_thread_flag = 0 #whether or not the thread is running
        self.watch_player = None  # id of player to watch for spectating, TODO
        self.player_id = None  # our own ID as provided by the JSON
        self.code = None  # lobby code
        self.lobby_updater = None  # thread to manage lobby updates

    def create(self, j, first=False, type=""):  # json response object
        print(j)
        self.player_list.clear_widgets()
        if first:
            self.player_id = j['msg']
            self.code = j['id']
            self.lobby_code.text = "%s Lobby Code: %s" % (type, self.code)

        challenging_ids = []
        # TODO: come up with a solution for players with identical names (this does not affect the server )
        if j['challenges'] != []:
            h = DummyBtn()
            h.text = 'Challenges (click to accept)'
            Clock.schedule_once(partial(self.add_to_list, h), -1)
            for i in j['challenges']:  # name, id, ip of challenger
                print(i)
                print(self.player_id)
                challenging_ids.append(i[1])
                p = MenuBtn()
                p.text = i[0]
                p.bind(on_release=partial(
                    self.accept_challenge, name=i[0], id=i[1], ip=i[2]))
                # self.playerList.add_widget(p)
                Clock.schedule_once(partial(self.add_to_list, p), -1)

        if j['idle'] != []:
            h = DummyBtn()
            h.text = 'Idle players (click to challenge)'
            # self.playerList.add_widget(h)
            Clock.schedule_once(partial(self.add_to_list, h), -1)
            for i in j['idle']:
                if i[1] not in challenging_ids:
                    p = MenuBtn()
                    p.text = i[0]
                    if i[1] != self.player_id:
                        p.bind(on_release=partial(
                            self.send_challenge, name=i[0], id=i[1]))
                    else:
                        p.text += " (self)"
                    # self.playerList.add_widget(p)
                    Clock.schedule_once(partial(self.add_to_list, p), -1)

        if j['playing'] != []:
            h = DummyBtn()
            h.text = 'Now playing (click to watch)'
            # self.playerList.add_widget(h)
            Clock.schedule_once(partial(self.add_to_list, h), -1)
            for i in j['playing']:
                p = MenuBtn()
                p.text = "%s vs %s" % (i[0], i[1])
                if i[2] != self.player_id and i[3] != self.player_id:
                    p.bind(on_release=partial(self.watch_match,
                           name="%s vs %s" % (i[0], i[1]), ip=i[4]))
                # self.playerList.add_widget(p)
                Clock.schedule_once(partial(self.add_to_list, p), -1)

        if first:
            self.lobby_thread_flag = 0
            self.lobby_updater = threading.Thread(
                target=self.auto_refresh, daemon=True)  # netplay watchdog
            self.lobby_updater.start()

    def add_to_list(self, p, *args):
        self.player_list.add_widget(p)

    def auto_refresh(self):
        while True:
            if self.lobby_thread_flag == 0:
                p = {
                    'action': 'status',
                    'id': self.code,
                    'p': self.player_id,
                    'secret': self.secret
                }
                print(p)
                self.create(requests.get(url=LOBBYURL, params=p).json())
                time.sleep(2)
            else:
                break

    def exit(self):
        self.lobby_thread_flag = 1
        self.player_list.clear_widgets()
        p = {
            'action': 'leave',
            'id': self.code,
            'p': self.player_id,
            'secret': self.secret
        }
        requests.get(url=LOBBYURL, params=p)
        self.secret = None
        self.lobby_thread = None
        self.watch_player = None
        self.player_id = None
        self.code = None
        self.lobby_updater = None

    def send_challenge(self, obj, name, id, *args):
        caster = threading.Thread(
            target=self.app.game.host, args=[self], daemon=True)
        caster.start()
        while True:
            if self.app.game.adr is not None:
                popup = GameModal()
                popup.modal_txt.text = 'Challenging %s' % name
                popup.close_btn.text = 'Stop Hosting'
                popup.close_btn.bind(on_release=partial(
                    self.dismiss, t=caster, p=popup))
                self.active_pop = popup
                popup.open()
                break
        p = {
            't': id,
            'p': self.player_id,
            'action': 'challenge',
            'id': self.code,
            'ip': self.app.game.adr,
            'secret': self.secret
        }
        print(p)
        c = requests.get(url=LOBBYURL, params=p).json()
        print(c)

    def accept_challenge(self, obj, name, id, ip, *args):
        caster = threading.Thread(target=self.app.game.join, args=[
                                  ip, self, id], daemon=True)
        caster.start()
        popup = GameModal()
        popup.modal_txt.text = 'Connecting to %s' % name
        popup.close_btn.text = 'Stop Playing'
        popup.close_btn.bind(on_release=partial(
            self.dismiss, t=caster, p=popup))
        self.active_pop = popup
        popup.open()

    def confirm(self, obj, r, d, p, n, t=None, *args):
        self.app.game.rf = int(r.text)
        self.app.game.df = int(d.text)
        self.active_pop.modal_txt.text += "\nConnected to: %s, %s Delay & %s Rollback" % (
            n, d.text, r.text)
        p.dismiss()
        if t: #if accepting, run MBAA check
            threading.Thread(target=self.wait_for_MBAA, args=[t]).start()

    def wait_for_MBAA(self, t):
        time.sleep(3)
        if self.app.game.playing is True and self.active_pop != None:
            resp = {
                't': t,
                'p': self.player_id,
                'action': 'accept',
                'id': self.code,
                'secret': self.secret
            }
            print(resp)
            c = requests.get(url=LOBBYURL, params=resp).json()
            print(c)
            self.current_player = t

    def watch_match(self, obj, name, ip, *args):
        popup = GameModal()
        caster = threading.Thread(
            target=self.app.game.watch, args=[ip,popup.modal_txt], daemon=True)
        self.active_pop = popup
        popup.modal_txt.text = 'Watching %s' % name
        popup.close_btn.text = 'Close game'
        popup.close_btn.bind(on_release=partial(
            self.dismiss, t=caster, p=popup))
        popup.open()
        caster.start()

    def set_frames(self, name, delay, ping, target=None):
        popup = FrameModal()
        popup.frame_txt.text = 'Connected to: %s\nPing: %s Network Delay: %s, Suggested: Rollback %s,  Delay %s' % (
            name, ping, delay, self.app.game.rs, self.app.game.ds)
        popup.r_input.text = str(self.app.game.rs)
        popup.d_input.text = str(self.app.game.ds)
        popup.start_btn.bind(on_release=partial(
            self.confirm, p=popup, r=popup.r_input, d=popup.d_input, n=name, t=target))
        popup.close_btn.bind(on_release=partial(
            self.dismiss, t=self.app.game.aproc, p=popup))
        popup.open()

    # TODO prevent players from dismissing caster until MBAA is open to avoid locking issues
    def dismiss(self, obj, t, p, *args):
        self.app.game.adr = None
        self.app.game.rs = -1
        self.app.game.ds = -1
        self.app.game.rf = -1
        self.app.game.df = -1
        os.system('start /min taskkill /f /im cccaster.v3.0.exe')
        del(t)
        r = {
            'action': 'end',
            'p': self.player_id,
            'id': self.code,
            'secret': self.secret
        }
        requests.get(url=LOBBYURL, params=r)
        p.dismiss()
        if self.active_pop != None:
            self.active_pop.dismiss()
        self.active_pop = None
        self.app.game.aproc = None
        self.app.game.playing = False
        if self.app.sound.bgm.state == 'stop' and self.app.sound.muted is False:
            self.app.sound.cut_bgm()

import time
import requests
import threading
from functools import partial
from config import *
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from ui.modals import *
from ui.buttons import MenuBtn, DummyBtn


class LobbyScreen(Screen):
    active_pop = None  # active popup on the screen
    player_list = ObjectProperty(None)  # layout for players
    challenge_list = ObjectProperty(None)  # layout for players
    match_list = ObjectProperty(None)  # layout for players
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
        self.widget_index = {} #ids of players, widget of lobby
        self.error = False


    def create(self, j, first=False, type=""):  # json response object
        print(j)

        if first:
            self.player_id = j['msg']
            self.code = j['id']
            self.lobby_code.text = "%s Lobby Code: %s" % (type, self.code)
            self.widget_index = {}
            self.player_list.clear_widgets()
            self.match_list.clear_widgets()
            self.challenge_list.clear_widgets()

        challenging_ids = []
        # TODO: come up with a solution for players with identical names (this does not affect the server )
        if j['challenges'] != []:
            if 'c' not in self.widget_index:
                h = DummyBtn()
                h.text = 'Challenges (click to accept)'
                self.challenge_list.add_widget(h)
                self.widget_index.update({'c':h})

            for i in j['challenges']:  # name, id, ip of challenger
                challenging_ids.append(i[1])
                if i[1] in self.widget_index:
                    if self.widget_index.get(i[1]).parent == self.challenge_list:
                        pass
                    else: #remove idle player
                        self.widget_index.get(i[1]).parent.remove_widget(self.widget_index.get(i[1]))
                        p = MenuBtn()
                        p.text = i[0]
                        p.bind(on_release=partial(
                            self.accept_challenge, name=i[0], id=i[1], ip=i[2]))
                        self.challenge_list.add_widget(p)
                        self.widget_index.update({i[1]:p})
                else:
                    p = MenuBtn()
                    p.text = i[0]
                    p.bind(on_release=partial(
                        self.accept_challenge, name=i[0], id=i[1], ip=i[2]))
                    self.challenge_list.add_widget(p)
                    self.widget_index.update({i[1]:p})
        else:
            n = []
            for k,v in self.widget_index.items():
                if v in self.challenge_list.children:
                    v.parent.remove_widget(v)
                    n.append(k)
            for i in n:
                self.widget_index.pop(i)

        if j['idle'] != []:
            for i in j['idle']:
                if i[1] not in challenging_ids:
                    if i[1] in self.widget_index:
                        pass
                    else:
                        p = MenuBtn()
                        p.text = i[0]
                        if i[1] != self.player_id:
                            p.bind(on_release=partial(
                                self.send_challenge, name=i[0], id=i[1]))
                        else:
                            p.text += " (self)"
                        self.player_list.add_widget(p)
                        self.widget_index.update({i[1]:p})

        if j['playing'] != []:
            if 'w' not in self.widget_index:
                h = DummyBtn()
                h.text = 'Now playing (click to watch)'
                self.challenge_list.add_widget(h)
                self.widget_index.update({'w':h})
            for i in j['playing']:
                if (i[2],i[3]) in self.widget_index:
                    pass
                else:
                    p = MenuBtn()
                    p.text = "%s vs %s" % (i[0], i[1])
                    if i[2] != self.player_id and i[3] != self.player_id:
                        p.bind(on_release=partial(self.watch_match,
                            name="%s vs %s" % (i[0], i[1]), ip=i[4]))
                    self.match_list.add_widget(p)
                    self.widget_index.update({(i[2],i[3]):p})
        else:
            n = []
            for k,v in self.widget_index.items():
                if v in self.match_list.children:
                    v.parent.remove_widget(v)
                    n.append(k)
            for i in n:
                self.widget_index.pop(i)

        #if any widgets in the list don't correspond to json items, remove them
        n = []
        for k in self.widget_index.keys():
            ok = False
            if k != 'w' and k != 'c':
                for i in j['challenges']:
                    if k == i[1]:
                        ok = True
                for i in j['idle']:
                    if k == i[1]:
                        ok = True
                for i in j['playing']:
                    if k == i[2] or k == i[3]:
                        ok = True
                if ok is False:
                    n.append(k)
        for i in n:
            self.widget_index.get(i).parent.remove_widget(self.widget_index.get(i))
            self.widget_index.pop(i)

        if first:
            self.lobby_thread_flag = 0
            self.lobby_updater = threading.Thread(
                target=self.auto_refresh, daemon=True)  # netplay watchdog
            self.lobby_updater.start()
            #self.lobby_updater = Clock.schedule_interval(lambda dt: self.auto_refresh(),2)

    def auto_refresh(self):
        if self.lobby_thread_flag == 0:
            p = {
                'action': 'status',
                'id': self.code,
                'p': self.player_id,
                'secret': self.secret
            }
            print(p)
            try:
                r = requests.get(url=LOBBYURL, params=p).json()
                if r['msg'] == 'OK':
                    self.create(r)
                    time.sleep(2)
                    self.auto_refresh()
                else:
                    self.exit()
            except ValueError:
                    self.exit()
            except requests.exceptions.ConnectionError:
                    self.exit()

    def exit(self):
        self.lobby_thread_flag = 1
        try:
            p = {
                'action': 'leave',
                'id': self.code,
                'p': self.player_id,
                'secret': self.secret
            }
            requests.get(url=LOBBYURL, params=p)
        except:
            pass
        self.secret = None
        self.lobby_thread = 1 #kill clock thread
        self.watch_player = None
        self.player_id = None
        self.code = None
        #Clock.unschedule(self.lobby_updater)
        self.lobby_updater = None
        self.app.LobbyList.refresh()

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
                break
            elif self.error == True:
                break
        

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

    def error_message(self,e):
        self.error = True
        popup = GameModal()
        for i in e:
            popup.modal_txt.text += i + '\n'
        popup.close_btn.bind(on_release=partial(self.dismiss_error,p = popup))
        popup.close_btn.text = "Close"
        if self.active_pop != None:
            self.active_pop.dismiss()
        popup.open()
    
    def dismiss_error(self,obj,p):
        p.dismiss()
        self.error = False

    # TODO prevent players from dismissing caster until MBAA is open to avoid locking issues
    def dismiss(self, obj, t, p, *args):
        self.app.game.adr = None
        self.app.game.rs = -1
        self.app.game.ds = -1
        self.app.game.rf = -1
        self.app.game.df = -1
        self.app.game.kill_caster()
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

from mbaacc import MOON
import time
import requests
import threading
import pyperclip
import subprocess
from functools import partial
from config import *
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from ui.modals import *
from ui.buttons import DummyBtn, PlayerRow
import presence
import logging
import webbrowser

CHARACTER_WIKI = {
    0 : "Sion_Eltnam_Atlasia",
    1 : "Arcueid_Brunestud",
    2 : "Ciel",
    3 : "Akiha_Tohno",
    4 : "Hisui_%26_Kohaku",
    5 : "Hisui",
    6 : "Kohaku",
    7 : "Shiki_Tohno",
    8 : "Miyako_Arima",
    9 : "Warachia",
    10 : "Nero_Chaos",
    11 : "Sion_TATARI",
    12 : "Red_Arcueid",
    13 : "Akiha_Vermillion",
    14 : "Mech-Hisui",
    15 : "Shiki_Nanaya",
    17 : "Satsuki_Yumiduka",
    18 : "Len",
    19 : "Powerd_Ciel",
    20 : "Neco-Arc",
    22 : "Aoko_Aozaki",
    23 : "White_Len",
    25 : "Neco-Arc_Chaos",
    28 : "Kouma_Kishima",
    29 : "Akiha_Tohno_(Seifuku)",
    30 : "Riesbyfe_Stridberg",
    31 : "Roa",
    32 : "Dust of Osiris", # TODO "Is it neccesary if boss characters are never selectable? Why only Dust and not every other boss then?
    33 : "Shiki_Ryougi",
    34 : "Neco_%26_Mech",
    35 : "Koha_%26_Mech",
    51 : "Archetype:_Earth"
}

MOON_WIKI = {
    0 : 'Crescent_Moon',
    1 : 'Full_Moon',
    2 : 'Half_Moon'
}


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
        self.lobby_thread_flag = 0 #whether or not the thread is running
        self.watch_player = None  # id of player to watch for spectating, TODO
        self.player_id = None  # our own ID as provided by the JSON
        self.code = None  # lobby code
        self.lobby_updater = None  # thread to manage lobby updates
        self.widget_index = {} #ids of players, widget of lobby
        self.error = False
        self.challenge_name = None #name of player being challenged
        self.opponent = None # name of player currently being played against
        self.challenge_id = None #id of player being challenged
        self.type = None
        self.get_attempts = 0 #if 2, exit


    def create(self, j, first=False, type=""):  # json response object
        print(j)
        #this does not use self.type because it should only run once per lobby.
        #the reason for this is that a player may start a Direct Online match separately and we do not want to erase that status.
        #self.type is used for update_stats in the Caster function to signal info to the presence.
        newSound = False
        if first:
            self.player_id = j['msg']
            self.code = j['id']
            self.lobby_code.text = "[%s Lobby Code: %s]" % (type, self.code)
            self.widget_index = {}
            self.player_list.clear_widgets()
            self.match_list.clear_widgets()
            self.challenge_list.clear_widgets()
            self.type = type
            if self.app.discord is True:
                if type.lower() == 'public':
                    self.app.mode = 'Public Lobby'
                    presence.public_lobby(self.code)
                elif type.lower() == 'private':
                    self.app.mode = 'Private Lobby'
                    presence.private_lobby()
                self.app.game.update_stats(once=True)
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
                        p = PlayerRow()
                        p.ids['PlayerBtn'].text = i[0]
                        p.ids['PlayerBtn'].bind(on_release=partial(
                            self.accept_challenge, name=i[0], id=i[1], ip=i[2]))
                        p.ids['WatchBtn'].text = ""
                        self.challenge_list.add_widget(p)
                        self.widget_index.update({i[1]:p})
                        if newSound is False:
                            self.app.sound.play_alert()
                            newSound = True
                else:
                    p = PlayerRow()
                    p.ids['PlayerBtn'].text = i[0]
                    p.ids['PlayerBtn'].bind(on_release=partial(
                        self.accept_challenge, name=i[0], id=i[1], ip=i[2]))
                    p.ids['WatchBtn'].text = ""
                    self.challenge_list.add_widget(p)
                    self.widget_index.update({i[1]:p})
                    if newSound is False:
                        self.app.sound.play_alert()
                        newSound = True
        else:
            n = []
            for k,v in self.widget_index.items():
                if v in self.challenge_list.children:
                    v.parent.remove_widget(v)
                    n.append(k)
            for i in n:
                self.widget_index.pop(i)

        if j['idle'] != []:
            if 'i' not in self.widget_index:
                h = DummyBtn()
                h.text = 'Idle players (click to challenge)'
                self.player_list.add_widget(h)
                self.widget_index.update({'i':h})
            for i in j['idle']:
                if i[1] not in challenging_ids:
                    if i[1] in self.widget_index:
                        pass
                    else:
                        p = PlayerRow()
                        p.ids['PlayerBtn'].text = i[0]
                        if i[1] != self.player_id:
                            p.ids['PlayerBtn'].bind(on_release=partial(
                                self.send_challenge, name=i[0], id=i[1]))
                            if i[1] == self.watch_player:
                                p.ids['WatchBtn'].text = 'FOLLOWING'
                            else:
                                p.ids['WatchBtn'].text = 'FOLLOW'
                            p.ids['WatchBtn'].bind(on_release=partial(self.follow_player, i=i[1]))
                        else:
                            p.ids['PlayerBtn'].text += " (self)"
                            p.ids['WatchBtn'].disabled = True
                            p.ids['WatchBtn'].text = ""
                        self.player_list.add_widget(p)
                        self.widget_index.update({i[1]:p})
        else:
            n = []
            for k,v in self.widget_index.items():
                if v in self.player_list.children:
                    v.parent.remove_widget(v)
                    n.append(k)
            for i in n:
                self.widget_index.pop(i)

        if j['playing'] != []:
            if 'w' not in self.widget_index:
                h = DummyBtn()
                h.text = 'Now playing (click to watch)'
                self.match_list.add_widget(h)
                self.widget_index.update({'w':h})
            for i in j['playing']:
                if (i[2],i[3]) in self.widget_index:
                    pass
                else:
                    p = PlayerRow()
                    p.ids['PlayerBtn'].text = "%s vs %s" % (i[0], i[1])
                    if i[2] != self.player_id and i[3] != self.player_id:
                        p.ids['PlayerBtn'].bind(on_release=partial(self.watch_match,
                            name="%s vs %s" % (i[0], i[1]), ip=i[4]))
                    p.ids['WatchBtn'].text = ""
                    self.match_list.add_widget(p)
                    self.widget_index.update({(i[2],i[3]):p})
                if i[2] == self.watch_player or i[3] == self.watch_player:
                    self.watch_match(name="%s vs %s" % (i[0], i[1]), ip=i[4])
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
            if k != 'w' and k != 'c' and k != 'i':
                for i in j['challenges']:
                    if k == i[1]:
                        ok = True
                for i in j['idle']:
                    if k == i[1]:
                        ok = True
                for i in j['playing']:
                    if k == (i[2],i[3]) or k == (i[3],i[2]):
                        ok = True
                if ok is False:
                    n.append(k)
        for i in n:
            self.widget_index.get(i).parent.remove_widget(self.widget_index.get(i))
            self.widget_index.pop(i)
        if first:
            self.app.lobby_button()
            self.lobby_thread_flag = 0
            self.lobby_updater = threading.Thread(
                target=self.auto_refresh, daemon=True)  # netplay watchdog
            self.lobby_updater.start()
        else:
            if len(self.challenge_list.children) > 0:
                self.app.update_lobby_button('LOBBY %s (%s)' % (self.code,len(self.challenge_list.children) - 1))
            else:
                self.app.update_lobby_button('LOBBY %s ' % self.code)
        self.get_attempts = 0

    def follow_player(self,obj,i):
        w = self.widget_index.get(i).ids['WatchBtn']
        if w.text == 'FOLLOW':
            self.watch_player = i
            for k,v in self.widget_index.items(): # clear first
                try:
                    if v.parent == self.player_list and k != self.player_id:
                        v.ids['WatchBtn'].text = 'FOLLOW'
                except KeyError:
                    pass
            w.text = 'FOLLOWING'
        else:
            self.watch_player = None
            w.text = 'FOLLOW'

    def auto_refresh(self):
        while True:
            if self.lobby_thread_flag != 0:
                break
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
                else:
                    self.exit(msg=r['msg'])
            except:
                logging.warning('Concerto: Lobby Error: %s' % sys.exc_info()[0])
                if self.get_attempts < 2:
                    self.get_attempts += 1
                else:
                    self.exit(msg='Error: %s' % sys.exc_info()[0])

    def exit(self,msg=None):
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
        self.watch_player = None
        self.player_id = None
        self.code = None
        self.type = None
        self.lobby_updater = None
        self.get_attempts = 0
        self.app.remove_lobby_button()
        self.app.LobbyList.refresh()
        if msg:
            popup = GameModal()
            popup.modal_txt.text = msg
            popup.close_btn.text = 'Close'
            popup.close_btn.bind(on_release=popup.dismiss)
            popup.open()
        # Set Rich Presence to main menu again
        if self.app.discord is True:
            presence.menu()
        self.app.game.update_stats(once=True)

    def send_challenge(self, obj, name, id, *args):
        self.watch_player = None
        for k,v in self.widget_index.items():
            try:
                if k != self.player_id and v.parent == self.player_list:
                    v.ids['WatchBtn'].text = "FOLLOW"
            except KeyError:
                pass
        self.challenge_name = name
        self.challenge_id = id
        popup = GameModal()
        popup.modal_txt.text = 'Challenging %s' % self.challenge_name
        popup.close_btn.text = 'Stop Playing'
        popup.close_btn.bind(on_release=partial(
            self.dismiss, p=popup))
        self.active_pop = popup
        popup.open()
        caster = threading.Thread(
            target=self.app.game.host, args=[self, app_config['settings']['netplay_port']], daemon=True)
        caster.start()

    def set_ip(self):
        pyperclip.copy('') #erase IP address from clipboard
        p = {
            't': self.challenge_id,
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
        self.watch_player = None
        for k,v in self.widget_index.items():
            try:
                if k != self.player_id and v.parent == self.player_list:
                    v.ids['WatchBtn'].text = "FOLLOW"
            except KeyError:
                pass
        caster = threading.Thread(target=self.app.game.join, args=[
                                  ip, self, id], daemon=True)
        caster.start()
        popup = GameModal()
        popup.modal_txt.text = 'Connecting to %s' % name
        popup.close_btn.text = 'Stop Playing'
        popup.close_btn.bind(on_release=partial(
            self.dismiss, p=popup))
        self.active_pop = popup
        popup.open()

    def confirm(self, obj, r, d, p, n, t=None, *args):
        try:
            self.app.game.confirm_frames(int(r.text),int(d.text))
            self.opponent = n
            self.active_pop.modal_txt.text += "\nConnected to: %s, %s Delay & %s Rollback" % (
            n, d.text, r.text)

            self.active_pop.p1_char_guide.text = 'P1 Guide'
            self.active_pop.p1_char_guide.visible = True
            self.active_pop.p1_char_guide.bind(on_release=partial(
                self.open_char_wiki, "p1"))

            self.active_pop.p2_char_guide.text = 'P2 Guide'
            self.active_pop.p2_char_guide.visible = True
            self.active_pop.p2_char_guide.bind(on_release=partial(
                self.open_char_wiki, "p2"))
            
            #self.fill_wiki_button(self)
            p.dismiss()
            if t: #if accepting, run MBAA check
                threading.Thread(target=self.wait_for_MBAA, args=[t]).start()
        except ValueError:
            pass
        
    def wait_for_MBAA(self, t):
        while True:
            if self.app.game.playing is True and self.active_pop != None:
                cmd = f"""tasklist /FI "IMAGENAME eq mbaa.exe" /FO CSV /NH"""
                task_data = subprocess.check_output(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL).decode("UTF8","ignore")
                try:
                    task_data.replace("\"", "").split(",")[1]
                except IndexError:
                    pass
                else:
                    if self.app.game.read_memory(0x54EEE8) == 20: #wait for char select
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
                        break
            else:
                break

    def watch_match(self, obj=None, name="", ip="", *args):
        self.watch_player = None
        for k,v in self.widget_index.items():
            try:
                if k != self.player_id and v.parent == self.player_list:
                    v.ids['WatchBtn'].text = "FOLLOW"
            except KeyError:
                pass
        popup = GameModal()
        caster = threading.Thread(
            target=self.app.game.watch, args=[ip,self], daemon=True)
        self.active_pop = popup
        popup.modal_txt.text = 'Watching %s' % name
        popup.close_btn.text = 'Stop watching'
        popup.close_btn.bind(on_release=partial(
            self.dismiss, p=popup))

        popup.p1_char_guide.text = 'P1 Guide'
        popup.p1_char_guide.visible = True
        popup.p1_char_guide.bind(on_release=partial(
            self.open_char_wiki, "p1"))

        popup.p2_char_guide.text = 'P2 Guide'
        popup.p2_char_guide.visible = True
        popup.p2_char_guide.bind(on_release=partial(
            self.open_char_wiki, "p2"))
        
        popup.open()
        self.app.offline_mode = 'Spectating' #needs to be an offline mode for lobby multitasking
        caster.start()

    def set_frames(self, name, delay, ping, target=None, mode="Versus", rounds=2):
        popup = FrameModal()
        if rounds != 0:
            rounds = ", %s rounds per game" % rounds
        else:
            rounds = ''
        popup.frame_txt.text = '[b]Connected to %s[/b]\n[size=14][u]%s mode%s[/u]\nNetwork delay: %s (%s ms)\nSuggested: Delay %s, Rollback %s[/size]' % (
            name, mode, rounds, delay, ping, self.app.game.ds, self.app.game.rs)
        popup.r_input.text = str(self.app.game.rs)
        popup.d_input.text = str(self.app.game.ds)
        popup.start_btn.bind(on_release=partial(
            self.confirm, p=popup, r=popup.r_input, d=popup.d_input, n=name, t=target))
        popup.close_btn.bind(on_release=partial(
            self.dismiss, p=popup))
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
        self.active_pop = None
        popup.open()
    
    def dismiss_error(self,obj,p):
        p.dismiss()
        self.error = False

    # TODO prevent players from dismissing caster until MBAA is open to avoid locking issues
    def dismiss(self, obj, p, *args):
        self.app.game.kill_caster()
        self.challenge_name = None
        self.opponent = None
        self.challenge_id = None
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
    
    def fill_wiki_button(self):
        self.active_pop.p1_char_guide.text = 'P1 Guide'
        self.active_pop.p1_char_guide.bind(on_release=partial(
            self.open_char_wiki, "p1"))
        
        self.active_pop.p2_char_guide.text = 'P2 Guide'
        self.active_pop.p2_char_guide.bind(on_release=partial(
            self.open_char_wiki, "p2"))
        
    def open_char_wiki(self,player):
        url_wiki = 'https://wiki.gbl.gg/w/Melty_Blood/MBAACC'

        val = url_wiki 
        try:
            if(self.app.game.stats):
                
                if player == 'p1':
                    try:
                        char_key = self.app.game.stats["p1char"]
                        char = CHARACTER_WIKI.get(char_key)
                        moon_key = self.app.game.stats["p1moon"]
                        moon  = MOON_WIKI.get(moon_key)
                    except:
                        webbrowser.open(val)
                    
                if player == 'p2':
                    try:
                        char_key = self.app.game.stats["p2char"]
                        char = CHARACTER_WIKI.get(char_key)
                        moon_key = self.app.game.stats["p2moon"]
                        moon  = MOON_WIKI.get(moon_key)
                    except:
                        webbrowser.open(val)

                if( char and char != "Dust of Osiris"):
                    val = val + '/' + char 

                    if  moon :
                        val = val +  '/' + moon

                webbrowser.open(val)
            else:
                webbrowser.open(val)
        except:
            webbrowser.open(val)

    def invite_link(self,*args):
        pyperclip.copy('https://invite.meltyblood.club/%s' % self.code)
        threading.Thread(target=self.invite_ui).start()

    def invite_ui(self):
        if self.lobby_code.text != 'Link copied to clipboard':
            t = self.lobby_code.text
            self.lobby_code.text = 'Link copied to clipboard'
            time.sleep(2)
            self.lobby_code.text = t

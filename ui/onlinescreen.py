import threading
from functools import partial
from kivy.uix.screenmanager import Screen
from ui.modals import *
import config
import re
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

class OnlineScreen(Screen):
    

    def __init__(self, CApp, **kwargs):
        super(OnlineScreen, self).__init__(**kwargs)
        self.direct_pop = None  # Direct match popup for user settings
        self.active_pop = None  # active popup on the screen during netplay
        self.broadcast_pop = None
        self.app = CApp
        self.error = False
        self.opponent = None

    def direct(self):
        self.direct_pop = DirectModal()
        self.direct_pop.screen = self
        self.direct_pop.open()

    def broadcast(self):
        self.broadcast_pop = BroadcastModal()
        self.broadcast_pop.screen = self
        self.broadcast_pop.mode_type.text = "Versus"
        self.broadcast_pop.open()

    def lobby(self):
        if config.caster_config['settings']['displayName'].strip() == '':
            self.error_message(['Please go to Options and set a display name.'])
        else:
            self.app.LobbyList.refresh()

    def host(self):
        caster = threading.Thread(
            target=self.app.game.host, args=[self,config.app_config['settings']['netplay_port'], self.direct_pop.game_type.text], daemon=True)
        caster.start()
        popup = GameModal()
        popup.modal_txt.text = 'Hosting %s mode...\n' % self.direct_pop.game_type.text
        popup.close_btn.text = 'Stop Hosting'
        popup.close_btn.bind(on_release=partial(
            self.dismiss, p=popup))
        self.app.mode = 'Direct Match'
        
        popup.p1_char_guide.text = 'P1 Guide'
        popup.p1_char_guide.visible = True
        popup.p1_char_guide.bind(on_release=partial(
            self.open_char_wiki, "p1"))

        popup.p2_char_guide.text = 'P2 Guide'
        popup.p2_char_guide.visible = True
        popup.p2_char_guide.bind(on_release=partial(
            self.open_char_wiki, "p2"))
        
        #self.fill_wiki_button(self)
        
        self.active_pop = popup
        popup.open()

    def start_broadcast(self):
        caster = threading.Thread(
            target=self.app.game.broadcast, args=[self,config.app_config['settings']['netplay_port'], self.broadcast_pop.mode_type.text], daemon=True)
        caster.start()
        popup = GameModal()
        popup.modal_txt.text = 'Broadcasting %s mode...\n' % self.broadcast_pop.mode_type.text
        popup.close_btn.text = 'Stop Playing'
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
        
        #self.fill_wiki_button(self)
        
        self.app.offline_mode = 'Broadcasting %s' % self.broadcast_pop.mode_type.text
        self.active_pop = popup
        popup.open()

    def set_ip(self):
        self.active_pop.modal_txt.text += 'IP: %s\n(copied to clipboard)' % self.app.game.adr

    def join(self, ip=None):
        if ip == None:
            ip = self.direct_pop.join_ip.text

        check_ip = re.findall(
            r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{,5}', ip)
        if check_ip == []:
            self.error_message(['Please supply a valid IP.'])
            return None
        caster = threading.Thread(target=self.app.game.join, args=[ip, self], daemon=True)
        caster.start()
        popup = GameModal()
        popup.modal_txt.text = 'Connecting to IP: %s' % ip
        popup.close_btn.text = 'Stop Playing'
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
#        self.fill_wiki_button(self)

        self.app.mode = 'Direct Match'
        self.active_pop = popup
        popup.open()

    def watch(self, ip=None):
        if ip == None:
            ip = self.direct_pop.watch_ip.text

        check_ip = re.findall(
            r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{,5}', ip)
        if check_ip == []:
            self.error_message(['Please supply a valid IP.'])
            return None
        popup = GameModal()
        self.active_pop = popup
        caster = threading.Thread(target=self.app.game.watch, args=[ip, self], daemon=True)
        caster.start()
        popup.modal_txt.text = 'Watching IP: %s' % ip
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
        #self.fill_wiki_button(self)

        self.app.offline_mode = 'Spectating' #needs to be an offline mode for lobby multitasking
        popup.open()

    def confirm(self, obj, r, d, p, n, *args):
        try:
            self.app.game.confirm_frames(int(r.text),int(d.text))
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
            
            #self.fill_wiki_button(self)    #TODO Fill popup for the wiki buttons here?
            p.dismiss()
        except ValueError:
            pass

    def set_frames(self, name, delay, ping, target=None, mode="Versus", rounds=2): #t is used by Lobby frameset, placed here as a dummy
        popup = FrameModal()
        self.opponent = name
        if rounds != 0:
            rounds = ", %s rounds per game" % rounds
        else:
            rounds = ''
        popup.frame_txt.text = '[b]Connected to %s[/b]\n[size=14][u]%s mode%s[/u]\nNetwork delay: %s (%s ms)\nSuggested: Delay %s, Rollback %s[/size]' % (
            name, mode, rounds, delay, ping, self.app.game.ds, self.app.game.rs)
        popup.r_input.text = str(self.app.game.rs)
        popup.d_input.text = str(self.app.game.ds)
        popup.start_btn.bind(on_release=partial(
            self.confirm, p=popup, r=popup.r_input, d=popup.d_input, n=name))
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

        #self.fill_wiki_button(self)
        
        if self.active_pop:
            self.active_pop.dismiss()
        self.active_pop = None
        popup.open()

    def dismiss_error(self,obj,p):
        p.dismiss()
        self.error = False

    # TODO prevent players from dismissing caster until MBAA is open to avoid locking issues
    def dismiss(self, obj, p, *args):
        self.app.game.kill_caster()
        self.opponent = None
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
        
    def open_char_wiki(self, *args):
        url_wiki = 'https://wiki.gbl.gg/w/Melty_Blood/MBAACC'
        val = url_wiki 
        try:
            if(self.app.game.stats and args[1]):
                
                if args[1] == 'p1':
                    try:
                        char_key = self.app.game.stats["p1char"]
                        char = CHARACTER_WIKI.get(char_key)
                        moon_key = self.app.game.stats["p1moon"]
                        moon  = MOON_WIKI.get(moon_key)
                    except:
                        webbrowser.open(val)
                    
                if args[1] == 'p2':
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

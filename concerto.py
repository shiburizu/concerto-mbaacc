# System
import requests
import time
import threading
import psutil
# Utility scripts
from config import *  # App config functions
# Melty Blood CCCaster
from mbaacc import Caster
# Kivy
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.app import App
# Internal UI objects
from ui import howtoscreen, lobbyscreen, lobbylist, offlinescreen, onlinescreen, mainscreen, resourcescreen, optionscreen, sound


class Concerto(App):
    def __init__(self, **kwargs):
        super(Concerto, self).__init__(**kwargs)
        self.sm = ScreenManager(transition=FadeTransition(duration=0.10))
        self.game = Caster(CApp=self)  # expects Caster object

    def build(self):
        self.sound = sound.Sound()
        self.sound.cut_bgm()
        self.MainScreen = mainscreen.MainScreen()
        self.OnlineScreen = onlinescreen.OnlineScreen(CApp=self)
        self.OfflineScreen = offlinescreen.OfflineScreen(CApp=self)
        self.ResourceScreen = resourcescreen.ResourceScreen()
        self.OptionScreen = optionscreen.OptionScreen()
        self.LobbyList = lobbylist.LobbyList(CApp=self)
        self.LobbyScreen = lobbyscreen.LobbyScreen(CApp=self)
        self.HowtoScreen = howtoscreen.HowtoScreen()
        self.sm.add_widget(self.MainScreen)
        self.sm.add_widget(self.OnlineScreen)
        self.sm.add_widget(self.OfflineScreen)
        self.sm.add_widget(self.ResourceScreen)
        self.sm.add_widget(self.OptionScreen)
        self.sm.add_widget(self.LobbyList)
        self.sm.add_widget(self.LobbyScreen)
        self.sm.add_widget(self.HowtoScreen)
        c = threading.Thread(target=self.checkPop,daemon=True)
        c.start()
        return self.sm

    def checkPop(self, *args):
        n = False #if N is true, netplay was killed. So don't trigger alternative offline check
        if self.game.aproc != None and self.game.offline is False: #netplay checker
            if self.game.aproc.isalive():
                print("found online mbaa")
                pass
            else:
                if self.OnlineScreen.active_pop != None:
                    self.OnlineScreen.active_pop.dismiss()
                    self.OnlineScreen.active_pop = None
                if self.LobbyScreen.active_pop != None:
                    self.LobbyScreen.active_pop.dismiss()
                    self.LobbyScreen.active_pop = None
                    r = {
                        'action': 'end',
                        'p': self.LobbyScreen.player_id,
                        'id': self.LobbyScreen.code,
                        'secret': self.LobbyScreen.secret
                    }
                    print(r)
                    print(requests.get(url=LOBBYURL, params=r).json())
                self.game.aproc = None
                self.game.playing = False
                self.game.offline = False #just in case
                self.game.adr = None
                self.game.rs = -1
                self.game.ds = -1
                self.game.rf = -1
                self.game.df = -1
                os.system('start /min taskkill /f /im cccaster.v3.0.exe')
                n = True
                if self.sound.bgm.state == 'stop':
                    self.sound.cut_bgm() #toggle audio if needed
        if n is False and self.game.offline is True: #this check only works for offline functions where activePop is not present.
            q = [p.info['name'] for p in psutil.process_iter(['name'])]
            if 'MBAA' in q:
                pass #currently playing
            else:
                if 'cccaster' in q: #not playing, caster is open, kill
                    os.system('start /min taskkill /f /im cccaster.v3.0.exe')
                    self.game.aproc = None
                    self.game.offline = False
                if self.sound.bgm.state == 'stop':
                    self.sound.cut_bgm() #toggle audio if needed
        time.sleep(2)
        self.checkPop()
            

def run():
    CApp = Concerto()
    try:
        CApp.run()
    finally:
        if CApp.LobbyScreen.code != None:
            CApp.LobbyScreen.exit()


if __name__ == '__main__':
    run()

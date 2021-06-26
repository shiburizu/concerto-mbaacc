# System
import requests
import os
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
        return self.sm

    def checkPop(self, *args):
        if self.game.aproc != None:
            if self.game.aproc.isalive():
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
                self.game.adr = None
                self.game.rs = -1
                self.game.ds = -1
                self.game.rf = -1
                self.game.df = -1
                os.system('start /min taskkill /f /im cccaster.v3.0.exe')
                self.sound.cut_bgm()


def run():
    CApp = Concerto()
    try:
        Clock.schedule_interval(lambda dt: CApp.checkPop(), 2)
        CApp.run()
    finally:
        if CApp.LobbyScreen.code != None:
            CApp.LobbyScreen.exit()


if __name__ == '__main__':
    run()

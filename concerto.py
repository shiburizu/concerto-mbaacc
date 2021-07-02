import logging
logging.basicConfig(filename="concerto.log", level=logging.DEBUG)
# System
import requests
import time
import threading
import subprocess
# Utility scripts
from config import *  # App config functions
# Melty Blood CCCaster
from mbaacc import Caster
# Kivy
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.app import App
from kivy.lang import Builder
Builder.load_file('Concerto.kv')
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
        print("run")
        if self.game.aproc != None:
            if self.game.aproc.isalive():
                if self.game.offline is True:
                    w = subprocess.run('qprocess mbaa.exe', stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
                    print("offline")
                    print(w.stderr)
                    if w.stderr == b'No Process exists for mbaa.exe\r\n': #case sensitive
                        print("no MBAA found")
                        self.kill_caster()
                        self.game.aproc = None
                        self.game.offline = False
            else:
                print("game dead")
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
                    requests.get(url=LOBBYURL, params=r).json()
                self.kill_caster()
                    
        if hasattr(self,'sound'):
            w = subprocess.run('qprocess mbaa.exe', stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
            if w.stderr == b'No Process exists for mbaa.exe\r\n': #case sensitive
                if self.sound.bgm.state == 'stop':
                    self.sound.cut_bgm()
            else:
                if self.sound.bgm.state == 'play':
                    self.sound.cut_bgm()

        time.sleep(2)
        self.checkPop()

    def kill_caster(self):
        subprocess.run('taskkill /f /im cccaster.v3.0.exe', creationflags=subprocess.CREATE_NO_WINDOW)
                    
def run():
    CApp = Concerto()
    try:
        CApp.run()
    finally:
        if CApp.LobbyScreen.code != None:
            CApp.LobbyScreen.exit()


if __name__ == '__main__':
    run()

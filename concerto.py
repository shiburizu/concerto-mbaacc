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
from ui import howtoscreen, lobbyscreen, lobbylist, offlinescreen, onlinescreen, mainscreen, resourcescreen, optionscreen, aboutscreen, sound

class Concerto(App):
    def __init__(self, **kwargs):
        super(Concerto, self).__init__(**kwargs)
        self.sm = ScreenManager(transition=FadeTransition(duration=0.10))
        self.game = Caster(CApp=self)  # expects Caster object

    def build(self):
        self.sound = sound.Sound()
        if app_config['settings']['mute_bgm'] == '1':
            self.sound.muted = True
        else:
            self.sound.cut_bgm()
        self.MainScreen = mainscreen.MainScreen()
        self.OnlineScreen = onlinescreen.OnlineScreen(CApp=self)
        self.OfflineScreen = offlinescreen.OfflineScreen(CApp=self)
        self.ResourceScreen = resourcescreen.ResourceScreen()
        self.OptionScreen = optionscreen.OptionScreen(CApp=self)
        self.LobbyList = lobbylist.LobbyList(CApp=self)
        self.LobbyScreen = lobbyscreen.LobbyScreen(CApp=self)
        self.HowtoScreen = howtoscreen.HowtoScreen()
        self.AboutScreen = aboutscreen.AboutScreen()
        self.sm.add_widget(self.MainScreen)
        self.sm.add_widget(self.OnlineScreen)
        self.sm.add_widget(self.OfflineScreen)
        self.sm.add_widget(self.ResourceScreen)
        self.sm.add_widget(self.OptionScreen)
        self.sm.add_widget(self.LobbyList)
        self.sm.add_widget(self.LobbyScreen)
        self.sm.add_widget(self.HowtoScreen)
        self.sm.add_widget(self.AboutScreen)
        c = threading.Thread(target=self.checkPop,daemon=True)
        c.start()
        return self.sm

    def checkPop(self, *args):
        if self.game.aproc != None:
            if self.game.aproc.isalive():
                if self.game.offline is True:
                    w = subprocess.run('qprocess mbaa.exe', stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
                    if w.stderr == b'No Process exists for mbaa.exe\r\n': #case sensitive
                        self.game.kill_caster()
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
                    requests.get(url=LOBBYURL, params=r).json()
                self.game.kill_caster()    
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
                    
def run():
    CApp = Concerto()
    try:
        CApp.run()
    finally:
        CApp.game.kill_caster()
        if CApp.LobbyScreen.code != None:
            CApp.LobbyScreen.exit()


if __name__ == '__main__':
    run()

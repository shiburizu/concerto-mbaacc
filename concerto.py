import sys
# System
import requests
import time
import threading
import subprocess
import winreg
# Utility scripts
from config import *  # App config functions
# Logging
import logging
logging.basicConfig(filename= PATH + '\concerto.log', level=logging.DEBUG)
# Melty Blood CCCaster
from mbaacc import Caster
# Discord Rich Presence
import presence

# Kivy
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.app import App
from kivy.lang import Builder
Builder.load_file('Concerto.kv')
# Internal UI objects
from ui import howtoscreen, lobbyscreen, lobbylist, offlinescreen, onlinescreen, mainscreen, resourcescreen, optionscreen, aboutscreen, sound, buttons

class Concerto(App):
    def __init__(self, **kwargs):
        super(Concerto, self).__init__(**kwargs)
        self.mode = 'Menu' # current mode selection
        self.sm = ScreenManager(transition=FadeTransition(duration=0.10))
        self.game = Caster(CApp=self)  # expects Caster object

    def build(self):
        self.sound = sound.Sound()
        self.MainScreen = mainscreen.MainScreen(CApp=self)
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

    def on_start(self):
        #necessary file sanity checks
        e = []

        # Register concerto:// url protocol handler
        try:
            key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, 'concerto')
            winreg.SetValueEx(key, '', 0, winreg.REG_SZ, 'URL:Concerto Protocol')
            winreg.SetValueEx(key, 'URL Protocol', 0, winreg.REG_SZ, '')
            winreg.SetValueEx(winreg.CreateKey(key, 'DefaultIcon'), '', 0, winreg.REG_SZ, 'concerto.exe,0')
            winreg.SetValueEx(winreg.CreateKey(key, 'shell\\open\\command'), '', 0, winreg.REG_SZ, '"' + sys.argv[0] + '" "%1"')
            if key:
                winreg.CloseKey(key)
        except:
            logging.warning('Concerto: please start as admin once to add concerto protocol handler')
        
        if caster_config is None:
            e.append('cccaster/config.ini not found.')
            e.append('Please fix the above problems and restart Concerto.')
        if e != []:
            self.sound.muted = True
            self.MainScreen.error_message(e)
        else:
            #if all is well, start loading in user options
            if app_config['settings']['mute_bgm'] == '1':
                self.sound.muted = True
            else:
                self.sound.cut_bgm()

        # Connect discord rich presence
        presence.connect()
        presence.menu()

        # Execute launch params
        if len(sys.argv) > 1:
            params = sys.argv[1].replace('concerto://', '').rstrip('/').split(':', 1)
            if params[0] == 'lobby':
                self.LobbyList.join(code=int(params[1]))
            elif params[0] == 'connect':
                self.OnlineScreen.join(ip=params[1])
            elif params[0] == 'watch':
                self.OnlineScreen.watch(ip=params[1])

    def lobby_button(self, *args):
        lst = [
            self.MainScreen.ids['lobbyAnchor'],
            self.OnlineScreen.ids['lobbyAnchor'],
            self.OfflineScreen.ids['lobbyAnchor'],
            self.ResourceScreen.ids['lobbyAnchor'],
            self.OptionScreen.ids['lobbyAnchor'],
            self.HowtoScreen.ids['lobbyAnchor'],
            self.AboutScreen.ids['lobbyAnchor']
        ]
        for i in lst:
            b = buttons.LobbyBtn()
            b.text += ' %s' % self.LobbyScreen.code
            b.bind(on_release=self.switch_to_lobby)
            i.clear_widgets()
            i.add_widget(b)
    
    def remove_lobby_button(self, *args):
        lst = [
            self.MainScreen.ids['lobbyAnchor'],
            self.OnlineScreen.ids['lobbyAnchor'],
            self.OfflineScreen.ids['lobbyAnchor'],
            self.ResourceScreen.ids['lobbyAnchor'],
            self.OptionScreen.ids['lobbyAnchor'],
            self.HowtoScreen.ids['lobbyAnchor'],
            self.AboutScreen.ids['lobbyAnchor']
        ]
        for i in lst:
            i.clear_widgets()

    def update_lobby_button(self,text,*args):
        lst = [
            self.MainScreen.ids['lobbyAnchor'].children,
            self.OnlineScreen.ids['lobbyAnchor'].children,
            self.OfflineScreen.ids['lobbyAnchor'].children,
            self.ResourceScreen.ids['lobbyAnchor'].children,
            self.OptionScreen.ids['lobbyAnchor'].children,
            self.HowtoScreen.ids['lobbyAnchor'].children,
            self.AboutScreen.ids['lobbyAnchor'].children
        ]
        for i in lst:
            for n in i:
                n.text = text
        
    def switch_to_main(self, *args):
        self.sm.current = 'Main'

    def switch_to_lobby(self, *args):
        self.sm.current = 'Lobby'

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
                    self.LobbyScreen.challenge_id = None
                    self.LobbyScreen.challenge_name = None
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
        # close rich presence connection
        presence.close()
        CApp.game.kill_caster()
        if CApp.LobbyScreen.code != None:
            CApp.LobbyScreen.exit()


if __name__ == '__main__':
    run()

import sys
from config import *  # App config functions
# System
import requests
import time
import threading
import subprocess
import winreg
# Utility scripts
# Discord Rich Presence
import presence
# Melty Blood CCCaster
from mbaacc import Caster
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
        self.discord = False #Discord support flag
        self.mode = 'Menu' # current mode selection
        self.offline_mode = None #secondary Offline activity, mostly for lobby
        self.sm = ScreenManager(transition=FadeTransition(duration=0.10))
        self.game = Caster(CApp=self)  # expects Caster object
        self.player_name = 'Concerto Player' #static player name to use for online lobbies

    def build(self):
        self.sound = sound.Sound()
        self.MainScreen = mainscreen.MainScreen(CApp=self)
        self.OnlineScreen = onlinescreen.OnlineScreen(CApp=self)
        self.OfflineScreen = offlinescreen.OfflineScreen(CApp=self)
        self.ResourceScreen = resourcescreen.ResourceScreen(CApp=self)
        self.OptionScreen = optionscreen.OptionScreen(CApp=self)
        self.LobbyList = lobbylist.LobbyList(CApp=self)
        self.LobbyScreen = lobbyscreen.LobbyScreen(CApp=self)
        self.HowtoScreen = howtoscreen.HowtoScreen(CApp=self)
        self.AboutScreen = aboutscreen.AboutScreen(CApp=self)
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
        logging.warning('Concerto: old CWD is %s' % os.getcwd()) 
        os.chdir(PATH)
        logging.warning('Concerto: new CWD is %s' % os.getcwd())
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
            try:
                winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, 'concerto')
            except:
                self.MainScreen.ids['welcome'].text = 'To join lobbies via Discord/invite links run Concerto as admin once.'
                logging.warning('Concerto: please start as admin once to add concerto protocol handler')

        logging.warning('Concerto: argv is %s' % sys.argv[0])
        s = PATH
        logging.warning('Concerto: PATH is %s' % s)

        if caster_config is None:
            e.append('"cccaster" folder not found.')
            e.append('Please fix the above problems and restart Concerto.')
        if e != []:
            self.sound.muted = True
            self.MainScreen.error_message(e,fatal=True)
        else:
            #if all is well, start loading in user options
            if app_config['settings']['mute_bgm'] == '1':
                self.sound.muted = True
            else:
                self.sound.cut_bgm()
            if app_config['settings']['discord'] == '1':
                self.discord = True
                # Connect discord rich presence
                presence.connect()
                presence.menu()
            self.sound.mute_alerts = app_config['settings']['mute_alerts'] == '1'
            self.player_name = caster_config['settings']['displayName']
        # Execute launch params
        if len(sys.argv) > 1:
            params = sys.argv[1].replace('concerto://', '').rstrip('/').split(':', 1)
            if params[0] == 'lobby':
                check = self.OnlineScreen.online_login()
                if check != []:
                    self.OnlineScreen.error_message(check)
                else:
                    self.LobbyList.join(code=params[1])
            elif params[0] == 'connect':
                self.OnlineScreen.join(ip=params[1])
            elif params[0] == 'watch':
                self.OnlineScreen.watch(ip=params[1])

    def on_stop(self,*args):
        self.game.kill_caster()
        if self.LobbyScreen.code != None:
            self.LobbyScreen.exit()
        if self.discord is True:
            presence.close()

    def lobby_button(self, *args):
        for i in self.sm.screens:
            if 'lobbyAnchor' in i.ids and i != self.LobbyScreen:
                a = i.ids['lobbyAnchor']
                b = buttons.LobbyBtn()
                b.text += ' %s' % self.LobbyScreen.code
                b.bind(on_release=self.switch_to_lobby)
                a.clear_widgets()
                a.add_widget(b)
    
    def remove_lobby_button(self, *args):
        for i in self.sm.screens:
            if 'lobbyAnchor' in i.ids  and i != self.LobbyScreen:
                i.ids['lobbyAnchor'].clear_widgets()

    def update_lobby_button(self,text,*args):
        for i in self.sm.screens:
            if 'lobbyAnchor' in i.ids and i != self.LobbyScreen:
                a = i.ids['lobbyAnchor'].children
                for n in a:
                    n.text = text

    def switch_to_lobby(self, *args):
        self.sm.current = 'Lobby'

    def switch_to_main(self, *args):
        self.sm.current = 'Main'

    def checkPop(self, *args):
        while True:
            if self.game.aproc != None:
                if self.game.aproc.isalive():
                    if self.game.offline is True:
                        cmd = f"""tasklist /FI "IMAGENAME eq mbaa.exe" /FO CSV /NH"""
                        task_data = subprocess.check_output(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL).decode("UTF8","ignore")
                        try:
                            task_data.replace("\"", "").split(",")[1]
                        except IndexError:
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
                cmd = f"""tasklist /FI "IMAGENAME eq mbaa.exe" /FO CSV /NH"""
                task_data = subprocess.check_output(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL).decode("UTF8","ignore")
                try:
                    task_data.replace("\"", "").split(",")[1]
                except IndexError:
                    if self.sound.bgm.state == 'stop':
                        self.sound.cut_bgm()
                else:
                    if self.sound.bgm.state == 'play':
                        self.sound.cut_bgm()              
            time.sleep(2)
                    
def run():
    CApp = Concerto()
    CApp.run()
        
        

if __name__ == '__main__':
    run()

from kivy import config
from kivy.core.audio import SoundLoader
from config import *  # App config functions

class Sound():

    def __init__(self):
        self.bgm = SoundLoader.load('res/' + app_config['settings']['bgm_track'] + '.mp3')
        self.alert = SoundLoader.load('res/alert.mp3')
        self.muted = False
        self.mute_alerts = False

    def switch(self):
        if self.bgm.state == 'play':
            self.bgm.stop()
        self.bgm = SoundLoader.load('res/' + app_config['settings']['bgm_track'] + '.mp3')
        self.cut_bgm()

    def cut_bgm(self, obj=None):
        if self.muted is False and self.bgm:
            if self.bgm.state == 'play':
                self.bgm.stop()
            elif self.bgm.state == 'stop':
                self.bgm.volume = 0.15
                self.bgm.loop = True
                self.bgm.play()

    def play_alert(self,obj=None):
        if self.mute_alerts is False:
            self.alert.volume = 0.5
            self.alert.play()

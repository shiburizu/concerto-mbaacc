from kivy.core.audio import SoundLoader


class Sound():

    def __init__(self):
        self.bgm = SoundLoader.load('res/main_bgm.flac')
        self.muted = False

    def cut_bgm(self, obj=None):
        print(self.bgm.state)
        if self.muted is False and self.bgm:
            if self.bgm.state == 'play':
                self.bgm.stop()
            elif self.bgm.state == 'stop':
                self.bgm.volume = 0.15
                self.bgm.loop = True
                self.bgm.play()

    def toggle_cut_bgm(self, obj=None):
        if self.muted is True:
            self.muted = False
            self.cut_bgm()
        else:
            self.cut_bgm()
            self.muted = True

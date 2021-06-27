from kivy.uix.screenmanager import Screen
import threading

class OfflineScreen(Screen):
    active_pop = None #active popup on the screen

    def __init__(self,CApp,**kwargs):
        super(OfflineScreen, self).__init__(**kwargs)
        self.app = CApp

    def training(self, *args):
        caster = threading.Thread(target=self.app.game.training,daemon=True)
        caster.start()

    def replays(self, *args):
        caster = threading.Thread(target=self.app.game.replays,daemon=True)
        caster.start()

    def local(self, *args):
        caster = threading.Thread(target=self.app.game.local,daemon=True)
        caster.start()

    def tournament(self, *args):
        caster = threading.Thread(target=self.app.game.tournament,daemon=True)
        caster.start()
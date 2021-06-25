from kivy.uix.screenmanager import Screen
import threading, os
from functools import partial

from ui.modals import GameModal

class OfflineScreen(Screen):
    active_pop = None #active popup on the screen

    def __init__(self,CApp,**kwargs):
        super(OfflineScreen, self).__init__(**kwargs)
        self.app = CApp

    def training(self, *args):
        caster = threading.Thread(target=self.app.game.training,daemon=True)
        caster.start()
        popup = GameModal()
        popup.modal_txt.text = 'Training mode started.'
        popup.close_btn.text = 'Close game'
        popup.close_btn.bind(on_release=partial(self.dismiss,t=caster,p=popup))
        self.active_pop = popup
        popup.open()

    def replays(self, *args):
        caster = threading.Thread(target=self.app.game.replays,daemon=True)
        caster.start()
        popup = GameModal()
        popup.modal_txt.text = 'Replay Theater started.'
        popup.close_btn.text = 'Close game'
        popup.close_btn.bind(on_release=partial(self.dismiss,t=caster,p=popup))
        self.active_pop = popup
        popup.open()

    def local(self, *args):
        caster = threading.Thread(target=self.app.game.local,daemon=True)
        caster.start()
        popup = GameModal()
        popup.modal_txt.text = 'Local VS started.'
        popup.close_btn.text = 'Close game'
        popup.close_btn.bind(on_release=partial(self.dismiss,t=caster,p=popup))
        self.active_pop = popup
        popup.open()

    def tournament(self, *args):
        caster = threading.Thread(target=self.app.game.tournament,daemon=True)
        caster.start()
        popup = GameModal()
        popup.modal_txt.text = 'Tournament Local VS started.'
        popup.close_btn.text = 'Close game'
        popup.close_btn.bind(on_release=partial(self.dismiss,t=caster,p=popup))
        self.active_pop = popup
        popup.open()
    
    def dismiss(self,obj,t,p,*args):
        os.system('start /min taskkill /f /im cccaster.v3.0.exe')
        del(t)
        p.dismiss()
        if self.active_pop != None:
            self.active_pop.dismiss()
        self.active_pop = None
        self.app.game.aproc = None
        if self.app.sound.bgm.state == 'stop' and self.app.sound.muted is False:
            self.app.sound.cut_bgm()
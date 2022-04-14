from ui.concertoscreen import ConcertoScreen
from ui.modals import GameModal
import threading

from functools import partial
import webbrowser
import logging
from ui.playerwiki import *

class OfflineScreen(ConcertoScreen):
    
    def __init__(self,CApp):
        super().__init__(CApp)

    def training(self, *args):
        self.offline_pop("Training",tip="Tip: Press F4 to bind controls.")
        caster = threading.Thread(target=self.app.game.training,args=[self],daemon=True)
        caster.start()

    def replays(self, *args):
        self.offline_pop("Replay Theater")
        caster = threading.Thread(target=self.app.game.replays,args=[self],daemon=True)
        caster.start()
    
    def trials(self, *args):
        self.offline_pop("Trials",tip="Tip: Press F3 ingame to open Trial options.")
        caster = threading.Thread(target=self.app.game.trials,args=[self],daemon=True)
        caster.start()

    def local(self, *args):
        self.offline_pop("Local VS")
        caster = threading.Thread(target=self.app.game.local,args=[self],daemon=True)
        caster.start()

    def cpu(self, *args):
        self.offline_pop("VS CPU")
        caster = threading.Thread(target=self.app.game.cpu,args=[self],daemon=True)
        caster.start()

    def tournament(self, *args):
        self.offline_pop("Tournament VS",tip="Tip: Hold down Start to pause.")
        caster = threading.Thread(target=self.app.game.tournament,args=[self],daemon=True)
        caster.start()

    def standalone(self, *args):
        self.offline_pop("Standalone")
        caster = threading.Thread(target=self.app.game.standalone,args=[self],daemon=True)
        caster.start()

    def offline_pop(self, mode, tip=""):
        popup = GameModal('Starting %s mode...\n\n%s' % (mode,tip),"Stand by...")
        popup.close_btn.disabled = True
        popup.remove_widget(popup.p1_char_guide)
        popup.remove_widget(popup.p2_char_guide)
        popup.open()
        self.active_pop = popup
        self.app.offline_mode = mode
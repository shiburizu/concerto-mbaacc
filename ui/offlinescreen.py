from ui.concertoscreen import ConcertoScreen
from ui.modals import GameModal
import threading
import ui.lang
from ui.playerwiki import *

class OfflineScreen(ConcertoScreen):
    
    def __init__(self,CApp):
        super().__init__(CApp)

    def training(self, *args):
        self.offline_pop(ui.lang.localize("OFFLINE_MENU_TRAINING"),tip=ui.lang.localize("TIP_CONTROLS"))
        caster = threading.Thread(target=self.app.game.training,args=[self],daemon=True)
        caster.start()

    def replays(self, *args):
        self.offline_pop(ui.lang.localize("OFFLINE_MENU_REPLAYS"))
        caster = threading.Thread(target=self.app.game.replays,args=[self],daemon=True)
        caster.start()
    
    def trials(self, *args):
        self.offline_pop(ui.lang.localize("OFFLINE_MENU_TRIALS"),tip=ui.lang.localize("TIP_TRIALS"))
        caster = threading.Thread(target=self.app.game.trials,args=[self],daemon=True)
        caster.start()

    def local(self, *args):
        self.offline_pop(ui.lang.localize("OFFLINE_MENU_LOCAL_VS"),tip=ui.lang.localize("TIP_CONTROLS"))
        caster = threading.Thread(target=self.app.game.local,args=[self],daemon=True)
        caster.start()

    def cpu(self, *args):
        self.offline_pop(ui.lang.localize("OFFLINE_MENU_CPU_VS"),tip=ui.lang.localize("TIP_CONTROLS"))
        caster = threading.Thread(target=self.app.game.cpu,args=[self],daemon=True)
        caster.start()

    def tournament(self, *args):
        self.offline_pop("Tournament VS",tip=ui.lang.localize("TIP_PAUSE"))
        caster = threading.Thread(target=self.app.game.tournament,args=[self],daemon=True)
        caster.start()

    def standalone(self, *args):
        self.offline_pop("Standalone")
        caster = threading.Thread(target=self.app.game.standalone,args=[self],daemon=True)
        caster.start()

    def offline_pop(self, mode, tip=""):
        popup = GameModal(ui.lang.localize('OFFLINE_MENU_STARTING') % (mode,tip),ui.lang.localize('TERM_STANDBY'))
        popup.close_btn.disabled = True
        popup.remove_widget(popup.p1_char_guide)
        popup.remove_widget(popup.p2_char_guide)
        popup.open()
        self.active_pop = popup
        self.app.offline_mode = mode
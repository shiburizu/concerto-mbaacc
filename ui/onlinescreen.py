import threading
import os
from functools import partial
from kivy.uix.screenmanager import Screen
from ui.modals import *


class OnlineScreen(Screen):
    

    def __init__(self, CApp, **kwargs):
        super(OnlineScreen, self).__init__(**kwargs)
        self.direct_pop = None  # Direct match popup for user settings
        self.active_pop = None  # active popup on the screen during netplay
        self.app = CApp

    def direct(self):
        self.direct_pop = DirectModal()
        self.direct_pop.screen = self
        self.direct_pop.open()

    def host(self):
        caster = threading.Thread(
            target=self.app.game.host, args=[self], daemon=True)
        caster.start()
        while True:
            if self.app.game.adr is not None:
                popup = GameModal()
                popup.modal_txt.text = 'Hosting to IP: %s\nAddress copied to clipboard.' % self.app.game.adr
                popup.close_btn.text = 'Stop Hosting'
                popup.close_btn.bind(on_release=partial(
                    self.dismiss, t=caster, p=popup))
                self.active_pop = popup
                popup.open()
                break
            elif self.app.game.aproc is None:
                break

    def join(self):
        caster = threading.Thread(target=self.app.game.join, args=[
                                  self.direct_pop.join_ip.text,self], daemon=True)
        caster.start()
        popup = GameModal()
        popup.modal_txt.text = 'Connecting to IP: %s' % self.direct_pop.join_ip.text
        popup.close_btn.text = 'Stop Playing'
        popup.close_btn.bind(on_release=partial(
            self.dismiss, t=caster, p=popup))
        self.active_pop = popup
        popup.open()

    def watch(self):
        popup = GameModal()
        self.active_pop = popup
        caster = threading.Thread(target=self.app.game.watch, args=[
                                  self.direct_pop.watch_ip.text,self], daemon=True)
        caster.start()
        popup.modal_txt.text = 'Watching IP: %s' % self.direct_pop.watch_ip.text
        popup.close_btn.text = 'Close game'
        popup.close_btn.bind(on_release=partial(
            self.dismiss, t=caster, p=popup))
        popup.open()

    def confirm(self, obj, r, d, p, n, *args):
        self.app.game.rf = int(r.text)
        self.app.game.df = int(d.text)
        self.active_pop.modal_txt.text += "\nConnected to: %s" % n
        p.dismiss()

    def set_frames(self, name, delay, ping, t=None): #t is used by Lobby frameset, placed here as a dummy
        fpopup = FrameModal()
        fpopup.frame_txt.text = 'Connected to: %s\nPing: %s Network Delay: %s, Suggested: Rollback %s,  Delay %s' % (
            name, ping, delay, self.app.game.rs, self.app.game.ds)
        fpopup.r_input.text = str(self.app.game.rs)
        fpopup.d_input.text = str(self.app.game.ds)
        fpopup.start_btn.bind(on_release=partial(
            self.confirm, p=fpopup, r=fpopup.r_input, d=fpopup.d_input, n=name))
        fpopup.close_btn.bind(on_release=partial(
            self.dismiss, t=self.app.game.aproc, p=fpopup))
        fpopup.open()

    def error_message(self,e):
        popup = GameModal()
        for i in e:
            popup.modal_txt.text += i + '\n'
        popup.close_btn.bind(on_release=popup.dismiss)
        popup.close_btn.text = "Close"
        if self.active_pop:
            self.active_pop.dismiss()
        popup.open()

    # TODO prevent players from dismissing caster until MBAA is open to avoid locking issues
    def dismiss(self, obj, t, p, *args):
        self.app.game.adr = None
        self.app.game.rs = -1
        self.app.game.ds = -1
        self.app.game.rf = -1
        self.app.game.df = -1
        os.system('start /min taskkill /f /im cccaster.v3.0.exe')
        del(t)
        p.dismiss()
        if self.active_pop != None:
            self.active_pop.dismiss()
        self.active_pop = None
        self.app.game.aproc = None
        self.app.game.playing = False

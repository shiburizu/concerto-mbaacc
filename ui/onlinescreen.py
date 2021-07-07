import threading
from functools import partial
from kivy.uix.screenmanager import Screen
from ui.modals import *
import config
import re

class OnlineScreen(Screen):
    

    def __init__(self, CApp, **kwargs):
        super(OnlineScreen, self).__init__(**kwargs)
        self.direct_pop = None  # Direct match popup for user settings
        self.active_pop = None  # active popup on the screen during netplay
        self.app = CApp
        self.error = False

    def direct(self):
        self.direct_pop = DirectModal()
        self.direct_pop.screen = self
        self.direct_pop.open()

    def host(self):
        caster = threading.Thread(
            target=self.app.game.host, args=[self,config.app_config['settings']['netplay_port'], self.direct_pop.game_type.text], daemon=True)
        caster.start()
        while True:
            if self.app.game.adr is not None:
                popup = GameModal()
                popup.modal_txt.text = 'Hosting to IP: %s\nAddress copied to clipboard.' % self.app.game.adr
                popup.close_btn.text = 'Stop Hosting'
                popup.close_btn.bind(on_release=partial(
                    self.dismiss, p=popup))
                self.active_pop = popup
                popup.open()
                print('open')
                break
            elif self.error == True:
                break

    def join(self):
        ip = re.findall(
            r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{,5}', self.direct_pop.join_ip.text)
        if ip == []:
            self.error_message(['Please supply a valid IP.'])
            return None
        caster = threading.Thread(target=self.app.game.join, args=[
                                  self.direct_pop.join_ip.text,self], daemon=True)
        caster.start()
        popup = GameModal()
        popup.modal_txt.text = 'Connecting to IP: %s' % self.direct_pop.join_ip.text
        popup.close_btn.text = 'Stop Playing'
        popup.close_btn.bind(on_release=partial(
            self.dismiss, p=popup))
        self.active_pop = popup
        popup.open()

    def watch(self):
        ip = re.findall(
            r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{,5}', self.direct_pop.watch_ip.text)
        if ip == []:
            self.error_message(['Please supply a valid IP.'])
            return None
        popup = GameModal()
        self.active_pop = popup
        caster = threading.Thread(target=self.app.game.watch, args=[
                                  self.direct_pop.watch_ip.text,self], daemon=True)
        caster.start()
        popup.modal_txt.text = 'Watching IP: %s' % self.direct_pop.watch_ip.text
        popup.close_btn.text = 'Close game'
        popup.close_btn.bind(on_release=partial(
            self.dismiss, p=popup))
        popup.open()

    def confirm(self, obj, r, d, p, n, *args):
        try:
            self.app.game.confirm_frames(int(r.text),int(d.text))
            self.active_pop.modal_txt.text += "\nConnected to: %s, %s Delay & %s Rollback" % (
            n, d.text, r.text)
            p.dismiss()
        except ValueError:
            pass

    def set_frames(self, name, delay, ping, target=None, mode="Versus", rounds=2): #t is used by Lobby frameset, placed here as a dummy
        popup = FrameModal()
        if rounds != 0:
            rounds = ", %s rounds per game" % rounds
        else:
            rounds = ''
        popup.frame_txt.text = '[b]Connected to %s[/b]\n[size=14][u]%s mode%s[/u]\nNetwork delay: %s (%s ms)\nSuggested: Delay %s, Rollback %s[/size]' % (
            name, mode, rounds, delay, ping, self.app.game.ds, self.app.game.rs)
        popup.r_input.text = str(self.app.game.rs)
        popup.d_input.text = str(self.app.game.ds)
        popup.start_btn.bind(on_release=partial(
            self.confirm, p=popup, r=popup.r_input, d=popup.d_input, n=name))
        popup.close_btn.bind(on_release=partial(
            self.dismiss, p=popup))
        popup.open()

    def error_message(self,e):
        self.error = True
        popup = GameModal()
        for i in e:
            popup.modal_txt.text += i + '\n'
        popup.close_btn.bind(on_release=partial(self.dismiss_error,p = popup))
        popup.close_btn.text = "Close"
        if self.active_pop:
            self.active_pop.dismiss()
        popup.open()

    def dismiss_error(self,obj,p):
        p.dismiss()
        self.error = False

    # TODO prevent players from dismissing caster until MBAA is open to avoid locking issues
    def dismiss(self, obj, p, *args):
        self.app.game.kill_caster()
        p.dismiss()
        if self.active_pop != None:
            self.active_pop.dismiss()
        self.active_pop = None

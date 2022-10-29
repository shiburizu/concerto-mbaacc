from json.decoder import JSONDecodeError
import requests
from functools import partial

from config import *

from kivy.properties import ObjectProperty
from ui.concertoscreen import ConcertoScreen
from kivy.clock import Clock

from ui.buttons import DummyBtn

class LobbyList(ConcertoScreen):
    lobby_type = ObjectProperty(None)  # public or private lobby to create
    lobby_code = ObjectProperty(None)  # lobby code to join
    lobby_view = ObjectProperty(None)  # lobby grid layout

    def __init__(self, CApp):
        super().__init__(CApp)

    def create(self):
        p = {
            'name': self.app.player_name,
            'action': 'create',
            'type': self.lobby_type.text
        }
        a = requests.get(url=LOBBYURL, params=p).json()
        if a['status'] == 'OK':
            self.app.sm.current = 'Lobby'
            self.app.LobbyScreen.secret = int(a['secret'])
            self.app.LobbyScreen.create(a, first=True, 
                type=a['type'])
        else:
            self.error_message('%s: %s' % (self.localize("ERR_LOBBY_CREATE"),a['msg']))

    def join(self, obj=None, code=None):
        if code is None:
            c = self.lobby_code.text.strip()
        else:
            c = code
        p = {
            'name': self.app.player_name,
            'action': 'join',
            'id': c
        }
        try:
            a = requests.get(url=LOBBYURL, params=p, timeout=5).json()
        except JSONDecodeError:
            self.error_message(self.localize("ERR_BAD_RESPONSE"))
        else:
            if a['status'] == 'OK':
                self.app.sm.current = 'Lobby'
                self.app.LobbyScreen.secret = int(a['secret'])
                self.app.LobbyScreen.create(
                    a, first=True, type=a['type'])
                self.lobby_code.text = ''
            else:
                self.error_message(a['msg'])

    def refresh(self):
        if self.app.LobbyScreen.lobby_updater != None:
            Clock.schedule_once(lambda dt: self.switch_to_lobby(),0)
            return None
        try:
            a = requests.get(url=LOBBYURL, params={'action':'list'}).json()
            self.lobby_view.clear_widgets()
            if a['lobbies'] != []:
                for i in a['lobbies']:
                    b = DummyBtn()
                    b.halign = 'left'
                    b.text = "ID %s: %s %s" % (i[0], i[1],self.localize("TERM_PLAYERS"))
                    b.bind(on_release=partial(self.join, code=i[0]))
                    self.lobby_view.add_widget(b)
            else:
                b = DummyBtn()
                b.halign = 'left'
                b.text = self.localize("ERR_NO_LOBBIES")
                self.lobby_view.add_widget(b)
            if self.app.sm.current != 'LobbyList':
                Clock.schedule_once(lambda dt: self.switch_to_list(),0)
        except requests.exceptions.ConnectionError as e:
            Clock.schedule_once(lambda dt: self.switch_to_online(),0)
            self.error_message(self.localize("ERR_LOBBY_CONN"))
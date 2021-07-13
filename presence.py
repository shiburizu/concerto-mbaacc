import time
import sys
from pypresence import Presence

APP_ID = '864412248310284289'
RPC = Presence(APP_ID)

previous = ['menu', '']

def connect():
    RPC.connect()

def close():
    RPC.close()

def to_previous():
    if previous[0] == 'menu':
        menu()
    elif previous[0] == 'public':
        public_lobby(previous[1])
    elif previous[0] == 'private':
        private_lobby()

def menu():
    generic('Menu')

def character_select():
    generic('Character Select')

def generic(mode):
    RPC.update(start=int(time.time()), details=mode, large_image='concerto_icon')
    previous = [mode.lower(), '']

def public_lobby(id):
    RPC.update(state='Idle', start=int(time.time()), details='In Public Lobby', large_image='concerto_icon', buttons=[{'label': 'Join', 'url': 'concerto://lobby:' + str(id)}])
    previous = ['public', id]

def private_lobby():
    RPC.update(state='Idle', start=int(time.time()), details='In Private Lobby', large_image='concerto_icon')
    previous = ['private', '']

def online_game(opponent_name, char_name, char_id, moon_id):
    RPC.update(state='Playing vs ' + opponent_name, start=int(time.time()), details='Online Game', large_image='char_' + str(char_id), large_text=char_name, small_image='moon_' + str(moon_id))

def offline_game(gamemode, char_name, char_id, moon_id):
    RPC.update(start=int(time.time()), details=gamemode, large_image='char_' + str(char_id), large_text=char_name, small_image='moon_' + str(moon_id))

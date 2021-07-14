import time
import sys
from pypresence import Presence

APP_ID = '864412248310284289'
RPC = Presence(APP_ID)

previous = ['Menu']

def connect():
    RPC.connect()

def close():
    RPC.close()

# switch to previous presence status
def to_previous():
    if previous[0].lower() == 'menu':
        menu()
    elif previous[0].lower() == 'public lobby':
        public_lobby(previous[1])
    elif previous[0].lower() == 'private lobby':
        private_lobby()

def in_game():
    if previous[0].lower() == 'public lobby':
        public_online_game(previous[1], previous[2])
    else
        
def menu():
    generic('Menu')

def character_select():
    generic('Character Select')

def generic(mode):
    RPC.update(start=int(time.time()), details=mode, large_image='concerto_icon')
    previous = [mode]

def public_lobby(id, opponent_name):
    RPC.update(state='Idle', start=int(time.time()), details='Public Lobby', large_image='concerto_icon', buttons=[{'label': 'Join', 'url': 'concerto://lobby:' + str(id)}])
    previous = ['Public Lobby', id, opponent_name]

def private_lobby(opponent_name):
    RPC.update(state='Idle', start=int(time.time()), details='Private Lobby', large_image='concerto_icon')
    previous = ['Private Lobby', opponent_name]

def online_game(mode, opponent_name, char_name, char_id, moon_id):
    RPC.update(state='Playing vs ' + opponent_name, start=int(time.time()), details=mode, large_image='char_' + str(char_id), large_text=char_name, small_image='moon_' + str(moon_id))
    
def public_online_game(id, opponent_name, char_name, char_id, moon_id):
    RPC.update(state='Playing vs ' + opponent_name, start=int(time.time()), details='Public Lobby', large_image='char_' + str(char_id), large_text=char_name, small_image='moon_' + str(moon_id), buttons=[{'label': 'Join', 'url': 'concerto://lobby:' + str(id)}])

def offline_game(gamemode, char_name, char_id, moon_id):
    RPC.update(start=int(time.time()), details=gamemode, large_image='char_' + str(char_id), large_text=char_name, small_image='moon_' + str(moon_id))

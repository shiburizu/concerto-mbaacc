import time
from pypresence import Presence

APP_ID = '864412248310284289'
RPC = Presence(APP_ID)

def connect():
    RPC.connect()

def close():
    RPC.close()

def menu():
    RPC.update(start=int(time.time()), details='Menu', large_image='concerto_icon')

def character_select(mode):
    RPC.update(state='Character Select', start=int(time.time()), details=mode, large_image='concerto_icon')

def generic(mode):
    RPC.update(start=int(time.time()), details=mode, large_image='concerto_icon')

def public_lobby(id):
    RPC.update(state='Idle', start=int(time.time()), details='Public Lobby', large_image='concerto_icon', buttons=[{'label': 'Join', 'url': 'concerto://lobby:' + str(id)}])

def private_lobby():
    RPC.update(state='Idle', start=int(time.time()), details='Private Lobby', large_image='concerto_icon')

def online_game(mode, opponent_name, char_name, char_id, moon_id):
    RPC.update(state='Playing vs ' + opponent_name, start=int(time.time()), details=mode, large_image='char_' + str(char_id), large_text=char_name, small_image='moon_' + str(moon_id))

def public_lobby_game(lobby_id, opponent_name, char_name, char_id, moon_id):
    RPC.update(state='Playing vs ' + opponent_name, start=int(time.time()), details='Public Lobby', large_image='char_' + str(char_id), large_text=char_name, small_image='moon_' + str(moon_id), buttons=[{'label': 'Join', 'url': 'concerto://lobby:' + str(lobby_id)}])

def offline_game(gamemode, char_name, char_id, moon_id):
    RPC.update(start=int(time.time()), details=gamemode, large_image='char_' + str(char_id), large_text=char_name, small_image='moon_' + str(moon_id))

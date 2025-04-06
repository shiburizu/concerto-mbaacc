import time
import sys
import logging
from pypresence import Presence

APP_ID = '864412248310284289'
try:
    RPC = Presence(APP_ID)
except:
    logging.warning('Concerto: DISCORD: %s' % sys.exc_info()[0])

def connect():
    try:
        RPC.connect()
    except:
        logging.warning('Concerto: DISCORD: %s' % sys.exc_info()[0])

def close():
    try:
        RPC.close()
    except:
        logging.warning('Concerto: DISCORD: %s' % sys.exc_info()[0])

def menu():
    try:
        RPC.update(start=int(time.time()), details='Menu', large_image='concerto_icon')
    except:
        logging.warning('Concerto: DISCORD: MENU %s' % sys.exc_info()[0])

def character_select(mode,lobby_id=None):
    try:
        if lobby_id:
            RPC.update(state='Character Select', start=int(time.time()), large_image='concerto_icon', details='Public Lobby #%s' % lobby_id, buttons=[{'label': 'Join Lobby', 'url': 'concerto://lobby/' + str(lobby_id)}])
        else:
            RPC.update(state='Character Select', start=int(time.time()), details=mode, large_image='concerto_icon')
    except:
        logging.warning('Concerto: DISCORD: CHARACTER SELECT %s' % sys.exc_info()[0])

def generic(mode):
    try:
        RPC.update(start=int(time.time()), details=mode, large_image='concerto_icon')
    except:
        logging.warning('Concerto: DISCORD: GENERIC %s' % sys.exc_info()[0])

def public_lobby(id):
    try:
        RPC.update(state='Idle', start=int(time.time()), details='Public Room #%s' % id, large_image='concerto_icon', buttons=[{'label': 'Join Room', 'url': 'concerto://lobby/ ' + str(id)}])
    except:
        logging.warning('Concerto: DISCORD: PUBLIC LOBBY %s' % sys.exc_info()[0])

def global_lobby():
    try:
        RPC.update(state='Idle', start=int(time.time()), details='Global Lobby', large_image='concerto_icon', buttons=[{'label': 'Join Lobby', 'url': 'https://invite.meltyblood.club/MBAACC'}])
    except:
        logging.warning('Concerto: DISCORD: GLOBAL LOBBY %s' % sys.exc_info()[0])

def private_lobby():
    try:
        RPC.update(state='Idle', start=int(time.time()), details='Private Room', large_image='concerto_icon')
    except:
        logging.warning('Concerto: DISCORD: PRIVATE LOBBY %s' % sys.exc_info()[0])

def online_game(mode, opponent_name, char1_name, char1_id, char2_name, char2_id):
    try:
        RPC.update(state='Playing vs ' + opponent_name, start=int(time.time()), details=mode, large_image='char_' + str(char1_id), large_text=char1_name, small_image='char_' + str(char2_id), small_text=char2_name)
    except:
        logging.warning('Concerto: DISCORD: ONLINE GAME %s' % sys.exc_info()[0])

def public_lobby_game(lobby_id, opponent_name, char1_name, char1_id, char2_name, char2_id):
    try:
        RPC.update(state='Playing vs ' + opponent_name, start=int(time.time()), details='Public Room #%s' % lobby_id, large_image='char_' + str(char1_id), large_text=char1_name, small_image='char_' + str(char2_id), small_text='char_' + str(char2_name), buttons=[{'label': 'Join Lobby', 'url': 'concerto://lobby/' + str(lobby_id)}])
    except:
        logging.warning('Concerto: DISCORD: PUBLIC LOBBY GAME %s' % sys.exc_info()[0])

def global_lobby_game(opponent_name, char1_name, char1_id, char2_name, char2_id):
    try:
        RPC.update(state='Playing vs ' + opponent_name, start=int(time.time()), details='Global Lobby', large_image='char_' + str(char1_id), large_text=char1_name, small_image='char_' + str(char2_id), small_text='char_' + str(char2_name), buttons=[{'label': 'Join Lobby', 'url': 'https://invite.meltyblood.club/MBAACC'}])
    except:
        logging.warning('Concerto: DISCORD: GLOBAL LOBBY GAME %s' % sys.exc_info()[0])

def broadcast_game(mode, char1_id, tooltip_1, char2_id, tooltip_2, lobby_id=None):
    try:
        if lobby_id:
            RPC.update(start=int(time.time()), state=mode, large_image='char_' + str(char1_id), large_text=tooltip_1, small_image='char_' + str(char2_id), small_text=tooltip_2, details="Public Lobby #%s" % lobby_id, buttons=[{'label': 'Join Lobby', 'url': 'concerto://lobby/' + str(lobby_id)}])
        else:
            RPC.update(start=int(time.time()), state=mode, large_image='char_' + str(char1_id), large_text=tooltip_1, small_image='char_' + str(char2_id), small_text=tooltip_2)
    except:
        logging.warning('Concerto: DISCORD: BROADCAST GAME %s' % sys.exc_info()[0])

def offline_game(gamemode, char1_name, char1_id, char2_name, char2_id, lobby_id=None):
    try:
        if lobby_id:
            RPC.update(start=int(time.time()), state=gamemode, large_image='char_' + str(char1_id), large_text=char1_name, small_image='char_' + str(char2_id), small_text=char2_name, details="Public Lobby #%s" % lobby_id, buttons=[{'label': 'Join Lobby', 'url': 'concerto://lobby/' + str(lobby_id)}])
        else:
            RPC.update(start=int(time.time()), state=gamemode, large_image='char_' + str(char1_id), large_text=char1_name, small_image='char_' + str(char2_id), small_text=char2_name)
    except:
        logging.warning('Concerto: DISCORD: OFFLINE GAME %s' % sys.exc_info()[0])

def single_game(mode,char_name, char_id, moon_id, lobby_id=None):
    try:
        if lobby_id:
            RPC.update(start=int(time.time()), state=mode, large_image='char_' + str(char_id), large_text=char_name, small_image='moon_' + str(moon_id), details="Public Lobby #%s" % lobby_id, buttons=[{'label': 'Join Lobby', 'url': 'concerto://lobby/' + str(lobby_id)}])
        else:
            RPC.update(start=int(time.time()), state=mode, large_image='char_' + str(char_id), large_text=char_name, small_image='moon_' + str(moon_id))
    except:
        logging.warning('Concerto: DISCORD: SINGLE GAME %s' % sys.exc_info()[0])
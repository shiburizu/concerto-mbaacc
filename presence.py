import time
import sys
from pypresence import Presence

APP_ID = "861722062674722867"
RPC = Presence(APP_ID)

def connect():
    RPC.connect()

def close():
    RPC.close()

def menu():
    RPC.update(state="Main Menu", start=int(time.time()), details="Melty Blood Actress Again Current Code", large_image="concertoicontest")

def public_lobby(id):
    RPC.update(state="In Public Lobby", start=int(time.time()), details="Melty Blood Actress Again Current Code", large_image="concertoicontest", buttons=[{"label": "Join", "url": "concerto://lobby:" + str(id)}])

def private_lobby():
    RPC.update(state="In Private Lobby", start=int(time.time()), details="Melty Blood Actress Again Current Code", large_image="concertoicontest")


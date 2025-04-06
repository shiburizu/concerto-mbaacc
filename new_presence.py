import time
import sys
import logging
import requests
from pypresence import Presence

APP_ID = '864412248310284289'

class DiscordManager():
    #this class consolidates Discord presence handling and ensures errors related to it do not interrupt user interactions.

    def __init__(self,CApp=None):
        self.app = CApp
        self.offline_state = None #set to mode being accessed i.e. "Training"
        self.screen_state = None #set to online mode i.e. "Menu" (none) "Private" "Public" "Global" "Direct"
        self.online_type = None #set to online connect mode i.e. "Host" "Join" "Spectate" "Broadcast"
        self.eval_thread = None #threading object to use
        self.rpc = Presence(APP_ID)

    def init_rpc(self):
        self.rpc.connect()

    def close_rpc(self):
        self.rpc.close()

    def evaluate_thread(self):
        #step 1: evaluate stats: if the game is active pull the information we want from it. also signals to kill if win limit reached.
        #step 2: evaluate process: check if MBAA.exe is in use, kill anything not being used.
        #step 3: evaluate discord: pull info from the application to update the discord presence if needed.
        pass

    def evaluate_stats(self):
        #replacing the non-Discord portion of update_stats from mbaacc.py
        #this handles the win-limit and score file functions of update_stats
        pass

    def evaluate_process(self):
        #replacing CheckPop from Concerto.py
        pass

    def evaluate_discord(self):
        #replacing the Discord portion of update_stats from mbaacc.py
        pass

    def update_presence(self,start=int(time.time()),gamestate={},char1={},char2={},online={},lgtext=None,smtext=None):
        #gamestate tells us if we're in css, in-game, at retry, etc
        #char dicts tell us name, id, moon of each side
        #online tells us if we're in a lobby, direct, etc
        #lgtext and smtext are for overriding if needed.
        pass


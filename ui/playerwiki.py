from mbaacc import MOON
import time
import requests
import threading
import pyperclip
import subprocess
from functools import partial
from config import *
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from ui.modals import *
from ui.buttons import DummyBtn, PlayerRow
import presence
import logging
import webbrowser

CHARACTER_WIKI = {
    0 : "Sion_Eltnam_Atlasia",
    1 : "Arcueid_Brunestud",
    2 : "Ciel",
    3 : "Akiha_Tohno",
    4 : "Hisui_%26_Kohaku",
    5 : "Hisui",
    6 : "Kohaku",
    7 : "Shiki_Tohno",
    8 : "Miyako_Arima",
    9 : "Warachia",
    10 : "Nero_Chaos",
    11 : "Sion_TATARI",
    12 : "Red_Arcueid",
    13 : "Akiha_Vermillion",
    14 : "Mech-Hisui",
    15 : "Shiki_Nanaya",
    17 : "Satsuki_Yumiduka",
    18 : "Len",
    19 : "Powerd_Ciel",
    20 : "Neco-Arc",
    22 : "Aoko_Aozaki",
    23 : "White_Len",
    25 : "Neco-Arc_Chaos",
    28 : "Kouma_Kishima",
    29 : "Akiha_Tohno_(Seifuku)",
    30 : "Riesbyfe_Stridberg",
    31 : "Roa",
    32 : "Dust of Osiris", # TODO "Is it neccesary if boss characters are never selectable? Why only Dust and not every other boss then?
    33 : "Shiki_Ryougi",
    34 : "Neco_%26_Mech",
    35 : "Koha_%26_Mech",
    51 : "Archetype:_Earth"
}

MOON_WIKI = {
    0 : 'Crescent_Moon',
    1 : 'Full_Moon',
    2 : 'Half_Moon'
}

def fill_wiki_button(self):
    self.active_pop.p1_char_guide.text = 'P1 Guide'
    self.active_pop.p1_char_guide.bind(on_release=partial(
        self.open_char_wiki, "p1"))
    
    self.active_pop.p2_char_guide.text = 'P2 Guide'
    self.active_pop.p2_char_guide.bind(on_release=partial(
        self.open_char_wiki, "p2"))
    
def open_char_wiki(self, *args):
    url_wiki = 'https://wiki.gbl.gg/w/Melty_Blood/MBAACC'
    val = url_wiki 
    try:
        if(self.app.game.stats and args[1]):
            
            if args[1] == 'p1':
                try:
                    char_key = self.app.game.stats["p1char"]
                    char = CHARACTER_WIKI.get(char_key)
                    moon_key = self.app.game.stats["p1moon"]
                    moon  = MOON_WIKI.get(moon_key)
                except:
                    webbrowser.open(val)
                
            if args[1] == 'p2':
                try:
                    char_key = self.app.game.stats["p2char"]
                    char = CHARACTER_WIKI.get(char_key)
                    moon_key = self.app.game.stats["p2moon"]
                    moon  = MOON_WIKI.get(moon_key)
                except:
                    webbrowser.open(val)
            if( char and char != "Dust of Osiris"):
                val = val + '/' + char 
                if  moon :
                    val = val +  '/' + moon
            webbrowser.open(val)
        else:
            webbrowser.open(val)
    except:
        webbrowser.open(val)

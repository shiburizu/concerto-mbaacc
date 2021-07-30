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

    
def fill_wiki_button(self,popup):
    logging.warning("Here's the content of self and its type" + str(self) + str(type(self)))

    logging.warning("Here's the content of popup and its type" + str(popup) + str(type(popup)))
    
    popup.p1_char_guide.text = 'P1 Guide'
    popup.p1_char_guide.bind(on_release=partial(
        open_char_wiki, self,"p1"))
    
    popup.p2_char_guide.text = 'P2 Guide'
    popup.p2_char_guide.bind(on_release=partial(
        open_char_wiki, self,"p2"))
    return popup
    
def open_char_wiki(self, *args):
    url_wiki = 'https://wiki.gbl.gg/w/Melty_Blood/MBAACC'
    val = url_wiki 
    logging.warning("Inside open_char_wiki, current val = " + val)
    try:
        if(self.app.game.stats):
            logging.warning("Passed the first if" + str(self.app.game.stats) + "|| Argument/PLayer "+ str(args))
            if args.count('p1') >= 1 :
                logging.warning("INside If args p1 " + str(self.app.game.stats) + "|| Argument/PLayer "+ str(args))
                char_key = self.app.game.stats['p1char']
                char = CHARACTER_WIKI.get(char_key)
                logging.warning("Char key of p1 : " + str(char_key) +"Char of p1 : " + str(char) )
                moon_key = self.app.game.stats['p1moon']
                moon  = MOON_WIKI.get(moon_key)
                logging.warning("Moob key of p1 : " + str(moon_key) +"Moon of p2 : "+ str(moon))                    
                logging.warning("Passed the memory checks of p1" + str(self.app.game.stats) + "\n || char key : " + str(char_key) + "|| char: " + str(char) + "|| moon_key:" + str(moon_key) + "|| moon: " + str(moon))
            if args.count('p2') >= 1:
                logging.warning("INside If args p2 " + str(self.app.game.stats) + "|| Argument/PLayer "+ str(args))                    
                char_key = self.app.game.stats['p2char']
                char = CHARACTER_WIKI.get(char_key)
                logging.warning("Char key of p2 : " + str(char_key) +"Char of p2 : "+ str(char))
                moon_key = self.app.game.stats['p2moon']
                moon  = MOON_WIKI.get(moon_key)
                logging.warning("Moon key of p2 : " + str(moon_key) +"Moon of p2 : "+ str(moon))                    
                logging.warning("Passed the memory checks p2" + str(self.app.game.stats) + "\n || char key : "+ str(char_key) + "|| char: " + str(char) + "|| moon_key:" + str(moon_key) + "|| moon: " + str(moon))
                
            logging.warning("Passed the memory checks of both players" + str(self.app.game.stats) + "|| char key : "+ str(char_key) + "|| char: " + str(char) + "|| moon_key:" + str(moon_key) + "|| moon: " + str(moon))
            
            val = str(val) + '/' + str(char) +  '/' + str(moon)
            logging.warning("Everything worked!" + str(self.app.game.stats) + " || URL Link in val:  "+ str(val))
            webbrowser.open(str(val))
        else:
            webbrowser.open(val)
    except:
        webbrowser.open(val)
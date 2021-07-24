from kivy.uix.screenmanager import Screen
from ui.modals import GameModal
from functools import partial
import threading
import webbrowser
import logging


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

class OfflineScreen(Screen):
    active_pop = None #active popup on the screen

    def __init__(self,CApp,**kwargs):
        super(OfflineScreen, self).__init__(**kwargs)
        self.app = CApp

    def training(self, *args):
        self.offline_pop("Training")
        caster = threading.Thread(target=self.app.game.training,args=[self],daemon=True)
        caster.start()

    def replays(self, *args):
        self.offline_pop("Replay Theater")
        caster = threading.Thread(target=self.app.game.replays,args=[self],daemon=True)
        caster.start()

    def local(self, *args):
        self.offline_pop("Local VS")
        caster = threading.Thread(target=self.app.game.local,args=[self],daemon=True)
        caster.start()

    def tournament(self, *args):
        self.offline_pop("Tournament VS")
        caster = threading.Thread(target=self.app.game.tournament,args=[self],daemon=True)
        caster.start()

    def standalone(self, *args):
        self.offline_pop("Standalone")
        caster = threading.Thread(target=self.app.game.standalone,args=[self],daemon=True)
        caster.start()

    def offline_pop(self, mode):
        popup = GameModal()
        popup.modal_txt.text = 'Starting %s mode...' % mode
        popup.close_btn.text = "Stand by..."
        popup.close_btn.disabled = True

        popup.p1_char_guide.text = 'P1 Guide'
        popup.p1_char_guide.bind(on_release=partial(
            self.open_char_wiki, "p1"))
        popup.p1_char_guide.visible = True

        popup.p2_char_guide.text = 'P2 Guide'
        popup.p2_char_guide.bind(on_release=partial(
            self.open_char_wiki, "p2"))
        popup.p2_char_guide.visible = True

        popup.open()
        self.app.offline_mode = mode
        # self.fill_wiki_button()     #TODO Fill popup with the buttons for the wiki here?
        self.active_pop = popup
    
    def error_message(self,e):
        if self.active_pop != None:
            self.active_pop.modal_txt.text = ""
            for i in e:
                self.active_pop.modal_txt.text += i + '\n'
            self.active_pop.close_btn.disabled = False
            self.active_pop.close_btn.bind(on_release=self.active_pop.dismiss)
            self.active_pop.close_btn.text = "Close"
        else:
            popup = GameModal()
            for i in e:
                popup.modal_txt.text += i + '\n'
            popup.close_btn.bind(on_release=popup.dismiss)
            popup.close_btn.text = "Close"
            popup.open()

        
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
        logging.warning("Inside open_char_wiki, current val = " + val)
        try:
            if(self.app.game.stats):
                logging.warning("Passed the first if" + str(self.app.game.stats) + "|| Argument/PLayer "+ str(args[1]))
                if args[1] == 'p1' or args[0] == 'p1':
                    logging.warning("INside If args p1 " + str(self.app.game.stats) + "|| Argument/PLayer "+ str(args[1]))
                    char_key = self.app.game.stats['p1char']
                    char = CHARACTER_WIKI.get(char_key)
                    logging.warning("Char key of p1 : " + str(char_key) +"Char of p1 : " + str(char) )
                    moon_key = self.app.game.stats['p1moon']
                    moon  = MOON_WIKI.get(moon_key)
                    logging.warning("Moob key of p1 : " + str(moon_key) +"Moon of p2 : "+ str(moon))                    
                    logging.warning("Passed the memory checks of p1" + str(self.app.game.stats) + "\n || char key : " + str(char_key) + "|| char: " + str(char) + "|| moon_key:" + str(moon_key) + "|| moon: " + str(moon))
                if args[1] == 'p2' or args[0] == 'p2':
                    logging.warning("INside If args p2 " + str(self.app.game.stats) + "|| Argument/PLayer "+ str(args[1]))                    
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
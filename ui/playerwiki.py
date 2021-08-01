from functools import partial
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
    popup.p1_char_guide.disabled = False
    popup.p1_char_guide.opacity = 1

    popup.p2_char_guide.text = 'P2 Guide'
    popup.p2_char_guide.bind(on_release=partial(
        open_char_wiki, self,"p2"))
    popup.p2_char_guide.disabled = False
    popup.p2_char_guide.opacity = 1
    
    return popup
    
def open_char_wiki(self, *args):
    url_wiki = 'https://wiki.gbl.gg/w/Melty_Blood/MBAACC'
    val = url_wiki 
    player = " Player "
    try:
        if(self.app.game.stats):
            if args.count('p1') >= 1 :
                char_key = self.app.game.stats['p1char']
                char = CHARACTER_WIKI.get(char_key)
                player = player + "1 " + char

            if args.count('p2') >= 1:
                char_key = self.app.game.stats['p2char']
                char = CHARACTER_WIKI.get(char_key)
                player = player + "2 , character: " + char

            val = str(val) + '/' + str(char)

            #If a player is still on character select, having an general guide/overview of the character and all of its moons is more useful
            # than the specific guide of Crescent Moon that they didn't choose 2/3 of the time.
            if(self.app.game.stats['state'] != 20):
                if args.count('p1') >= 1 :
                    moon_key = self.app.game.stats['p1moon']
                    moon  = MOON_WIKI.get(moon_key)
                if args.count('p2') >= 1:
                    moon_key = self.app.game.stats['p2moon']
                    moon  = MOON_WIKI.get(moon_key)
                val = str(val) + '/' + str(moon)

            logging.warning("Player wanted to check the guide of " + player  + " ! || \n" + str(self.app.game.stats) + " \n || URL Link in val:  "+ str(val))
            webbrowser.open(str(val))
        else:
            webbrowser.open(val)
    except:
        webbrowser.open(val)
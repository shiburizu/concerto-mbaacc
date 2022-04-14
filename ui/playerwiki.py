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
    #32 : "Dust of Osiris", # "Is it neccesary if boss characters are never selectable? Why only Dust and not every other boss then?
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
    popup.p1_char_guide.text = 'P1 Wiki'
    popup.p1_char_guide.bind(on_release=partial(
        open_char_wiki, self,"p1"))
    popup.p1_char_guide.disabled = False
    popup.p1_char_guide.opacity = 1

    popup.p2_char_guide.text = 'P2 Wiki'
    popup.p2_char_guide.bind(on_release=partial(
        open_char_wiki, self,"p2"))
    popup.p2_char_guide.disabled = False
    popup.p2_char_guide.opacity = 1

    return popup

def open_char_wiki(self, *args):
    url_wiki = 'https://wiki.gbl.gg/w/Melty_Blood/MBAACC'
    url_player_wiki = url_wiki

    #not_active_game_modes = [65535 , 3, 2, 13, 11, 25]
    #STARTUP / OPENING  / TITLE / LOADING_DEMO / HIGH_SCORES / MAIN

    active_game_modes = [8 , 1 , 5]
    #LOADING / IN_GAME / RETRY
    character_select = 20
    try:
        char='char'
        moon='moon'

        if (args.count('p1') >= 1 ):
            player_char='p1' + char
            player_moon='p1' + moon
            player = " Player  1 "
        if (args.count('p2') >= 1):
            player_char='p2' + char
            player_moon='p2' + moon
            player = " Player 2 "

        if player:
            if(self.app.game.stats and player_char):
                state = self.app.game.stats['state']
                if state :
                    if(state == character_select or active_game_modes.count(state) >= 1):
                        char_key = self.app.game.stats[player_char]
                        char = CHARACTER_WIKI.get(char_key)

                        if char:
                            link_add = '/' + str(char) #Adds the character link to the url_player_wiki, so if was openned now it would direct to the Characters general page
                            player = str(player) + " || character " + str(char)

                            # IF a players IS on an ''active'' game mode(Playing, Loading up to play, Play Again screen), opening the specific Char/Moon combination is the more valuable alternative.
                            # BUT, IF a player IS NOT on an active game mode(like Character Select), having an general guide/overview of the character and all of their moons is the more useful alternative.
                            if(active_game_modes.count(state) >= 1):
                                moon_key = self.app.game.stats[player_moon]
                                moon  = MOON_WIKI.get(moon_key)
                                if moon:
                                    link_add = str(link_add) + '/' + str(moon) 
                                    player = str(player) + " || moon " + str(moon)

                            url_player_wiki = str(url_player_wiki) + str(link_add) #
        webbrowser.open(str(url_player_wiki))# Opens whatever the current link is.
    except:
        logging.warning("Some error occurred while trying to open the Wiki page of one of the Players Character/Moon combination.")
        webbrowser.open(str(url_wiki))#When any unexpected error occurs, just opens the default main page of the wiki
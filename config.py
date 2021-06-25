from kivy.config import Config
from kivy.lang import Builder
import configparser
import logging
import os
import sys
from kivy.resources import resource_add_path
if hasattr(sys, '_MEIPASS'):
    resource_add_path(os.path.join(sys._MEIPASS))
os.environ["KIVY_AUDIO"] = "sdl2"
logging.basicConfig(filename='concerto.log', level=logging.DEBUG)
Builder.load_file("ConcertoLobby.kv")  # .kv defines UI
# Kivy app configs
Config.set('graphics', 'width', '600')
Config.set('graphics', 'height', '400')
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'multisamples', 0)
Config.set(
    "kivy",
    "default_font",
    [
        "Tex Gyre",
        "res/texgyreheros-bolditalic.otf",
    ],
)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('kivy', 'window_icon', 'concertoicon.ico')
Config.write()

# load caster .ini
with open('cccaster/config.ini', 'r') as f:
    config_string = '[settings]\n' + f.read()
caster_config = configparser.ConfigParser()
caster_config.read_string(config_string)

LOBBYURL = "https://concerto-mbaacc.herokuapp.com/l"
VERSIONURL = "https://concerto-mbaacc.herokuapp.com/v"
CURRENT_VERSION = '6-22-2021'

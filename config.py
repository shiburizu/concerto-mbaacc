import os
import sys
import logging
if getattr(sys,'frozen', False): #frozen exe
    PATH = os.path.dirname(sys.argv[0]) + '\\'
    logging.basicConfig(filename= os.path.dirname(sys.argv[0]) + '\concerto.log', level=logging.DEBUG)
else: #not frozen
    PATH = os.path.dirname(os.path.abspath(__file__)) + '\\'
    logging.basicConfig(filename= os.path.dirname(os.path.abspath(__file__)) + '\concerto.log', level=logging.DEBUG)
logging.warning('Concerto: old CWD is %s' % os.getcwd()) 
os.chdir(PATH)
logging.warning('Concerto: new CWD is %s' % os.getcwd())
import configparser
from kivy.config import Config
from kivy.resources import resource_add_path
if hasattr(sys, '_MEIPASS'):
    resource_add_path(os.path.join(sys._MEIPASS))
os.environ["KIVY_AUDIO"] = "sdl2"
# Kivy app configs
Config.set('graphics', 'width', '600')
Config.set('graphics', 'height', '400')
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'multisamples', 0)
Config.set('kivy', 'desktop', 1)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('kivy', 'window_icon', 'concertoicon.ico')
Config.set(
    "kivy",
    "default_font",
    [
        "Roboto",
        'data/fonts/Roboto-Regular.ttf', 
        'data/fonts/Roboto-Italic.ttf',
        'data/fonts/Roboto-Bold.ttf', 
        'data/fonts/Roboto-BoldItalic.ttf'
    ],
)
Config.write()
#CCCaster ini default settings
if os.path.exists(PATH + 'cccaster\config.ini'):
    with open(PATH + 'cccaster\config.ini', 'r') as f:
        config_string = f.read()
else:
    with open(PATH + 'cccaster\config.ini', 'w') as f:
        f.write('alertOnConnect=3\n\n')
        f.write('alertWavFile=SystemDefault\n\n')
        f.write('autoCheckUpdates=1\n\n')
        f.write('defaultRollback=4\n\n')
        f.write('displayName=Concerto Player\n\n')
        f.write('fullCharacterName=0\n\n')
        f.write('heldStartDuration=1.5\n\n')
        f.write('highCpuPriority=1\n\n')
        f.write('lastMainMenuPosition=-1\n\n')
        f.write('lastOfflineMenuPosition=-1\n\n')
        f.write('lastUsedPort=-1\n\n')
        f.write('maxRealDelay=254\n\n')
        f.write('replayRollbackOn=1\n\n')
        f.write('updateChannel=1\n\n')
        f.write('versusWinCount=2')
        f.close()
    with open(PATH + 'cccaster\config.ini', 'r') as f:
        config_string = f.read()
caster_config = configparser.ConfigParser()
caster_config.read_string('[settings]\n' + config_string)
#Concerto ini default settings
if os.path.exists(PATH + 'concerto.ini'):
    opt = [
        'netplay_port',
        'mute_alerts',
        'mute_bgm',
        'discord'
    ]
    with open(PATH + 'concerto.ini') as f:
        for i in f.readlines():
            for x in opt:
                if x in i:
                    opt.remove(x)
    if len(opt) != 0:
        with open(PATH + 'concerto.ini','a') as f:
            for i in opt:
                f.write('\n%s=0\n' % i)
            f.close()
    with open(PATH + 'concerto.ini') as f:
        config_string = f.read()
else:
    with open(PATH + 'concerto.ini', 'w') as f:
        f.write('[settings]')
        f.write('\nnetplay_port = 0\n')
        f.write('\nmute_alerts = 0\n')
        f.write('\nmute_bgm = 0\n')
        f.write('\ndiscord = 0\n')
        f.close()
    with open(PATH + 'concerto.ini','r') as f:
        config_string = f.read()
app_config = configparser.ConfigParser()
app_config.read_string(config_string)

LOBBYURL = "https://concerto-mbaacc.herokuapp.com/l"
VERSIONURL = "https://concerto-mbaacc.herokuapp.com/v"
CURRENT_VERSION = '7-23-2021'
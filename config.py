import os
import sys
import logging
if getattr(sys,'frozen', False): #frozen exe
    PATH = os.path.dirname(sys.argv[0]) + '\\'
    logging.basicConfig(filename= os.path.dirname(sys.argv[0]) + '\\concerto.log', level=logging.DEBUG)
else: #not frozen
    PATH = os.path.dirname(os.path.abspath(__file__)) + '\\'
    logging.basicConfig(filename= os.path.dirname(os.path.abspath(__file__)) + '\\concerto.log', level=logging.DEBUG)
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
Config.set('graphics', 'fullscreen', 0)
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
caster_config = None
caster_opt = {
        'alertOnConnect' : '3',
        'alertWavFile' : 'SystemDefault',
        'autoCheckUpdates' : '1',
        'defaultRollback' : '4',
        'displayName' : 'Concerto Player',
        'fullCharacterName' : '0',
        'heldStartDuration' : '1.5',
        'highCpuPriority' : '0',
        'lastMainMenuPosition' : '-1',
        'lastOfflineMenuPosition' : '-1',
        'lastUsedPort' : '-1',
        'maxRealDelay' : '254',
        'replayRollbackOn' : '1',
        'updateChannel' : '1',
        'versusWinCount' : '2',
        'autoReplaySave' : '1',
        'matchmakingRegion': 'NA West'
}
if os.path.exists(PATH + 'cccaster\\config.ini'):
    clean = []
    with open(PATH + 'cccaster\\config.ini') as f:
        for i in f.readlines():
            for x in caster_opt:
                if x in i:
                    clean.append(x)
    for i in clean:
        try:
            del caster_opt[i]
        except KeyError:
            pass
    if len(caster_opt) != 0:
        with open(PATH + 'cccaster\\config.ini','a') as f:
            for k,v in caster_opt.items():
                f.write('\n%s=%s' % (k,v))
            f.close()
    with open(PATH + 'cccaster\\config.ini', 'r') as f:
            config_string = f.read()
    caster_config = configparser.ConfigParser()
    caster_config.read_string('[settings]\n' + config_string)
else:
    if os.path.isdir(PATH + 'cccaster'):
        with open(PATH + 'cccaster\\config.ini', 'w') as f:
            for k,v in caster_opt.items():
                    f.write('\n%s=%s' % (k,v))
            f.close()
        with open(PATH + 'cccaster\\config.ini', 'r') as f:
            config_string = f.read()
        caster_config = configparser.ConfigParser()
        caster_config.read_string('[settings]\n' + config_string)

#Concerto ini default settings
opt = [
        'netplay_port',
        'mute_alerts',
        'mute_bgm',
        'discord',
        'write_scores',
        'caster_exe',
        'bgm_track'
]
if os.path.exists(PATH + 'concerto.ini'):
    with open(PATH + 'concerto.ini') as f:
        for i in f.readlines():
            for x in opt:
                if x in i:
                    opt.remove(x)
    if len(opt) != 0:
        with open(PATH + 'concerto.ini','a') as f:
            for i in opt:
                if i == 'caster_exe':
                    f.write('\ncaster_exe=cccaster.v3.1.exe\n')
                elif i == 'bgm_track':
                    f.write('\nbgm_track=walkway\n')
                else:
                    f.write('\n%s=0\n' % i)
            f.close()
else:
    with open(PATH + 'concerto.ini', 'w') as f:
        f.write('[settings]')
        for i in opt:
            if i == 'caster_exe':
                f.write('\ncaster_exe=cccaster.v3.1.exe\n')
            elif i == 'bgm_track':  
                f.write('\nbgm_track=walkway\n')
            else:
                f.write('\n%s=0\n' % i)
        f.close()
with open(PATH + 'concerto.ini','r') as f:
    config_string = f.read()
app_config = configparser.ConfigParser()
app_config.read_string(config_string)

# apparently fresh DVD installations are missing this file.
system_config = None
if not os.path.exists(PATH + 'System\\_App.ini'):
    with open(PATH + 'System\\_App.ini','w') as f:
        f.write('[System]\n')
        f.write('PosX= 1\n')
        f.write('PosY= 1\n')
        f.write('AspectRatio= 0\n')
        f.write('NoVsMovie= 1\n')
        f.write('Windowed= 1\n')
        f.write('ScreenW= 640\n')
        f.write('ScreenH= 480\n')
        f.write('Bpp= 32\n')
        f.close()
        
with open(PATH + 'System\\_App.ini','r') as f:
    config_string = f.read()
system_config = configparser.ConfigParser()
system_config.read_string(config_string)

LOBBYURL = "https://concerto-mbaacc.shib.live/l"
VERSIONURL = "https://concerto-mbaacc.shib.live/v"
CURRENT_VERSION = '1.04'
DEBUG_VERSION = '1.05-rc' # set to '' if not in use. This string is printed to logging to track specific test builds.
def find_img(file):
    if os.path.exists(file):
        return PATH + file
    else:
        return 'res/%s' % file

def img_credit(file,txt):
    if os.path.exists(file):
        return ''
    else:
        return txt
    
resolutions = [
    "640x480",
    "720x480",
    "720x576",
    "800x600",
    "1024x768",
    "1152x864",
    "1280x720",
    "1280x768",
    "1280x800",
    "1280x960",
    "1280x1024",
    "1360x768",
    "1366x768",
    "1440x1080",
    "1600x900",
    "1600x1024",
    "1680x1050",
    "1920x1080"
]
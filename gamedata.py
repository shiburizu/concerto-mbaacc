import os
import struct

from config import PATH, caster_config


# Loads Melty Blood's _AAGameData.dat into a list of integer values, 'game_config'
# These are the indices of the values in game_config that we care about.
# https://wiki.gbl.gg/w/Melty_Blood/MBAACC/Internals#System/_AAGameData.dat
class indexes:
    REPLAY_SAVE = 10  # 0x28
    BGM_VOL = 81  # 0x144
    SFX_VOL = 82  # 0x148
    CHARACTER_FILTER = 88  # 0x160
    VIEW_FPS = 90  # 0x168
    SCREEN_FILTER = 93  # 0x174
    ASPECT_RATIO = 94  # 0x178


game_config = None

if os.path.exists(PATH + 'system\_AAGameData.dat'):
    with open(PATH + 'system\_AAGameData.dat', mode='rb') as f:
        game_data_file = f.read()
        game_config_tuple = struct.unpack("i" * (len(game_data_file) // 4),
                                          game_data_file)  # Load as sequential 4 byte integers
        game_config = list(game_config_tuple)
        f.close()

# Fix for invisibly failing to save replays
if not os.path.exists(PATH + 'ReplayVS'):
    os.mkdir(PATH + 'ReplayVS')


# Writes the current contents of gameData back to the file.
# Ideally call this before running the game so the replay save option is correct.
def save_config():
    if game_config is not None:
        with open(PATH + 'system\_AAGameData.dat', mode='wb') as f:
            game_data_file = struct.pack("i" * len(game_config), *game_config)
            f.write(game_data_file)
            f.close()

try:
    if caster_config['settings']['autoReplaySave'] == '1':
        game_config[indexes.REPLAY_SAVE] = 1
    else:
        game_config[indexes.REPLAY_SAVE] = 0
except KeyError:
    try:
        if caster_config['settings']['replayRollbackOn'] == '1':
            try:
                caster_config['settings']['autoReplaySave'] = '1'
            except:
                pass
            game_config[indexes.REPLAY_SAVE] = 1
        else:
            game_config[indexes.REPLAY_SAVE] = 0
    except:
        pass
except TypeError:
    pass #probably some other issue preventing caster_config from populating
save_config()

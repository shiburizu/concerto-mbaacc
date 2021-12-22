from kivy.uix.screenmanager import Screen

from gamedata import *
from config import *
from ui.modals import GameModal


class OptionScreen(Screen):

    def __init__(self, CApp, **kwargs):
        super(OptionScreen, self).__init__(**kwargs)
        self.app = CApp
    
    def load(self):
        try:
            self.ids['netplay_port'].text = app_config['settings']['netplay_port']
            self.ids['caster_exe'].text = app_config['settings']['caster_exe']
            self.ids['mute_alerts'].active = app_config['settings']['mute_alerts'] == '1'
            self.ids['mute_bgm'].active = app_config['settings']['mute_bgm'] == '1'
            self.ids['discord'].active = app_config['settings']['discord'] == '1'
            self.ids['display_name'].text = caster_config['settings']['displayName']
            self.ids['display_name'].disabled = self.ids['lobbyAnchor'].children != []
            self.ids['max_delay'].text = caster_config['settings']['maxRealDelay']
            self.ids['default_rollback'].text = caster_config['settings']['defaultRollback']
            self.ids['held_start'].text = caster_config['settings']['heldStartDuration']
            self.ids['matchmaking_region'].text = caster_config['settings']['matchmakingRegion']
            self.ids['versus_count'].value = int(caster_config['settings']['versusWinCount'])
            self.ids['alert_connect'].active = caster_config['settings']['alertOnConnect'] == '2' or caster_config['settings']['alertOnConnect'] == '3'
            self.ids['full_names'].active = caster_config['settings']['fullCharacterName'] == '1'
            self.ids['replay_rollback'].active = caster_config['settings']['replayRollbackOn'] == '1'
            self.ids['cpu_priority'].active = caster_config['settings']['highCpuPriority'] == '1'
            self.ids['caster_updates'].active = caster_config['settings']['autoCheckUpdates'] == '1'
            self.ids['bgm_vol'].value = max(0, 20 - game_config[indexes.BGM_VOL])
            self.ids['sfx_vol'].value = max(0, 20 - game_config[indexes.SFX_VOL])
            self.ids['aspect_ratio'].text = self.ids['aspect_ratio'].values[game_config[indexes.ASPECT_RATIO]]
            if app_config['settings']['bgm_track'] == "walkway":
                self.ids['bgm_track'].text = "Soubrette's Walkway"
            elif app_config['settings']['bgm_track'] == "fuzzy":
                self.ids['bgm_track'].text = "Fuzzy"
            self.ids['character_filter'].text = self.ids['character_filter'].values[game_config[indexes.CHARACTER_FILTER]]
            self.ids['screen_filter'].active = game_config[indexes.SCREEN_FILTER] == 1
            self.ids['view_fps'].active = game_config[indexes.VIEW_FPS] == 1
            self.app.sm.current = 'Options'
        except KeyError:
            self.app.MainScreen.error_message(['Invalid config files. Please back up your settings, delete cccaster/config.ini and concerto.ini and restart Concerto.'])

    def save(self):
        error_check = []
        change_sound = False
        try:
            if int(self.ids['netplay_port'].text) > 65536:
                error_check.append("Online port must be less than 65536.")     
        except ValueError:
            error_check.append("Online port must be a whole number.")
        if not os.path.isfile(self.ids['caster_exe'].text.strip()):
            error_check.append("CCCaster file specified not found.")
        try:
            int(self.ids['max_delay'].text)
        except ValueError:
            error_check.append("Max delay is not a whole number.")
        try:
            int(self.ids['default_rollback'].text)
        except ValueError:
            error_check.append("Default rollback frames is not a whole number.")
        try:
            float(self.ids['held_start'].text)
        except ValueError:
            error_check.append("Held start duration is not in seconds.")
        if self.ids['display_name'].text.strip() == '':
            error_check.append('Display name cannot be empty.')
        if error_check == []:
            with open(PATH + 'cccaster\config.ini', 'r') as f:
                config_file = f.readlines()
                n = 0
                for i in config_file:
                    if "displayName" in i:
                        config_file[n] = "displayName=%s\n" % self.ids['display_name'].text.strip()
                        self.app.player_name = self.ids['display_name'].text.strip()
                    elif "maxRealDelay" in i:
                        config_file[n] = "maxRealDelay=%s\n" % self.ids['max_delay'].text
                    elif "defaultRollback" in i:
                        config_file[n] = "defaultRollback=%s\n" % self.ids['default_rollback'].text
                    elif "heldStartDuration" in i:
                        config_file[n] = "heldStartDuration=%s\n" % self.ids['held_start'].text
                    elif "matchmakingRegion" in i:
                        config_file[n] = "matchmakingRegion=%s\n" % self.ids['matchmaking_region'].text
                    elif "versusWinCount" in i:
                        config_file[n] = "versusWinCount=%s\n" % self.ids['versus_count'].value
                    elif "alertOnConnect" in i:
                        if self.ids['alert_connect'].active is True:
                            config_file[n] = "alertOnConnect=3\n"
                        else:
                            config_file[n] = "alertOnConnect=0\n"
                    elif "fullCharacterName" in i:
                        if self.ids['full_names'].active is True:
                            config_file[n] = "fullCharacterName=1\n"
                        else:
                            config_file[n] = "fullCharacterName=0\n"
                    elif "autoReplaySave" in i:
                        if self.ids['replay_rollback'].active is True:
                            config_file[n] = "autoReplaySave=1\n"
                            game_config[indexes.REPLAY_SAVE] = 1
                        else:
                            config_file[n] = "autoReplaySave=0\n"
                            game_config[indexes.REPLAY_SAVE] = 0
                    elif "highCpuPriority" in i:
                        if self.ids['cpu_priority'].active is True:
                            config_file[n] = "highCpuPriority=1\n"
                        else:
                            config_file[n] = "highCpuPriority=0\n"
                    elif "autoCheckUpdates" in i:
                        if self.ids['caster_updates'].active is True:
                            config_file[n] = "autoCheckUpdates=1\n"
                        else:
                            config_file[n] = "autoCheckUpdates=0\n"
                    n += 1
                out = open(PATH + 'cccaster\config.ini','w')
                out.writelines(config_file)
                out.close()
                f.close()
            with open(PATH + 'cccaster\config.ini', 'r') as f:
                config_string = '[settings]\n' + f.read()
            caster_config.read_string(config_string)

            with open(PATH + 'concerto.ini', 'r') as f:
                config_file = f.readlines()
                n = 0
                for i in config_file:
                    if "netplay_port" in i:
                        config_file[n] = "netplay_port=%s\n" % self.ids['netplay_port'].text
                    elif "mute_alerts" in i:
                        if self.ids['mute_alerts'].active is True:
                            config_file[n] = "mute_alerts=1\n"
                            self.app.sound.mute_alerts = True
                        else:
                            config_file[n] = "mute_alerts=0\n"   
                            self.app.sound.mute_alerts = False                          
                    elif "mute_bgm" in i:
                        if self.ids['mute_bgm'].active is True:
                            config_file[n] = "mute_bgm=1\n"
                            if self.app.sound.muted is False:
                                if self.app.sound.bgm.state == 'play':
                                    self.app.sound.cut_bgm() 
                                self.app.sound.muted = True 
                        else:
                            config_file[n] = "mute_bgm=0\n"
                            self.app.sound.muted = False
                            if self.app.sound.bgm.state == 'stop':
                                    self.app.sound.cut_bgm() 
                    elif "bgm_track" in i:
                        if self.ids['bgm_track'].text == "Soubrette's Walkway":
                            config_file[n] = "bgm_track=walkway\n"
                            choice = "walkway"
                        elif self.ids['bgm_track'].text == "Fuzzy":
                            config_file[n] = "bgm_track=fuzzy\n"
                            choice = "fuzzy"
                        if app_config["settings"]["bgm_track"] != choice:
                            change_sound = True
                    elif "discord" in i:
                        if self.ids['discord'].active is True:
                            config_file[n] = "discord=1\n"
                        else:
                            config_file[n] = "discord=0\n"
                    elif "caster_exe" in i:
                        config_file[n] = "caster_exe=%s\n" % self.ids['caster_exe'].text
                    n += 1
                out = open(PATH + 'concerto.ini','w')
                out.writelines(config_file)
                out.close()
                f.close()
            with open(PATH + 'concerto.ini', 'r') as f:
                config_string = f.read()
            app_config.read_string(config_string)
            # Reload BGM if it changed
            if change_sound == True:
                self.app.sound.switch()
            # Save bg/sfx volume, 21 is off, not 20.
            game_config[indexes.BGM_VOL] = 20 - int(self.ids['bgm_vol'].value)
            game_config[indexes.SFX_VOL] = 20 - int(self.ids['sfx_vol'].value)
            if game_config[indexes.BGM_VOL] == 20:
                game_config[indexes.BGM_VOL] = 21
            if game_config[indexes.SFX_VOL] == 20:
                game_config[indexes.SFX_VOL] = 21
            game_config[indexes.ASPECT_RATIO] = \
                self.ids['aspect_ratio'].values.index(self.ids['aspect_ratio'].text)
            game_config[indexes.CHARACTER_FILTER] = \
                self.ids['character_filter'].values.index(self.ids['character_filter'].text)
            game_config[indexes.SCREEN_FILTER] = int(self.ids['screen_filter'].active)
            game_config[indexes.VIEW_FPS] = int(self.ids['view_fps'].active)
            save_config()
        else:
            p = GameModal()
            p.modal_txt.text = "Correct the following options:\n"
            for i in error_check:
                p.modal_txt.text += '%s\n' % i
            p.close_btn.text = 'Dismiss'
            p.close_btn.bind(on_release=p.dismiss)
            p.open()

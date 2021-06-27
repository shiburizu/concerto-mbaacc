from kivy.uix.screenmanager import Screen
from config import *
from ui.modals import GameModal

class OptionScreen(Screen):
    
    def load(self):
        self.ids['display_name'].text = caster_config['settings']['displayName']
        self.ids['max_delay'].text = caster_config['settings']['maxRealDelay']
        self.ids['default_rollback'].text = caster_config['settings']['defaultRollback']
        self.ids['held_start'].text = caster_config['settings']['heldStartDuration']
        self.ids['versus_count'].value = int(caster_config['settings']['versusWinCount'])
        
        if caster_config['settings']['alertOnConnect'] == '2' or caster_config['settings']['alertOnConnect'] == '3':
            self.ids['alert_connect'].active = True
        else:
            self.ids['alert_connect'].active = False

        if caster_config['settings']['fullCharacterName'] == '1':
            self.ids['full_names'].active = True
        else:
            self.ids['full_names'].active = False

        if caster_config['settings']['replayRollbackOn'] == '1':
            self.ids['replay_rollback'].active = True
        else:
            self.ids['replay_rollback'].active = False
        
        if caster_config['settings']['highCpuPriority'] == '1':
            self.ids['cpu_priority'].active = True
        else:
            self.ids['cpu_priority'].active = False

        if caster_config['settings']['autoCheckUpdates'] == '1':
            self.ids['caster_updates'].active = True
        else:
            self.ids['caster_updates'].active = False

    def save(self):
        error_check = []
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
        if error_check == []:
            with open('cccaster/config.ini', 'r') as f:
                config_file = f.readlines()
                out = open('cccaster/config.ini','w')
                n = 0
                for i in config_file:
                    if "displayName" in i:
                        config_file[n] = "displayName=%s\n" % self.ids['display_name'].text
                    elif "maxRealDelay" in i:
                        config_file[n] = "maxRealDelay=%s\n" % self.ids['max_delay'].text
                    elif "defaultRollback" in i:
                        config_file[n] = "defaultRollback=%s\n" % self.ids['default_rollback'].text
                    elif "heldStartDuration" in i:
                        config_file[n] = "heldStartDuration=%s\n" % self.ids['held_start'].text
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
                    elif "replayRollbackOn" in i:
                        if self.ids['replay_rollback'].active is True:
                            config_file[n] = "replayRollbackOn=1\n"
                        else:
                            config_file[n] = "replayRollbackOn=0\n"
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
                out.writelines(config_file)
                out.close()
                f.close()
            with open('cccaster/config.ini', 'r') as f:
                config_string = '[settings]\n' + f.read()
            caster_config.read_string(config_string)
        else:
            p = GameModal()
            p.modal_txt.text = "Correct the following options:\n"
            for i in error_check:
                p.modal_txt.text += '%s\n' % i
            p.close_btn.text = 'Dismiss'
            p.close_btn.bind(on_release=p.dismiss)
            p.open()
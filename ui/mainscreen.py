from kivy.uix.screenmanager import Screen
import config

class MainScreen(Screen):

    def __init__(self,**kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.ids['version'].text = "Version %s" % config.CURRENT_VERSION
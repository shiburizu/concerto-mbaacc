from kivy.uix.screenmanager import Screen
from kivy.resources import resource_find
import webbrowser
import config

class AboutScreen(Screen):

    def __init__(self,**kwargs):
        super(AboutScreen, self).__init__(**kwargs)
        with open(resource_find('res/about.txt')) as f:
            c = f.read()
            self.ids['about'].text = c
        self.ids['about'].bind(on_ref_press=self.get_link)
        self.ids['version'].text = "Version %s" % config.CURRENT_VERSION

    def get_link(self,obj,val):
        webbrowser.open(val)
from kivy.uix.screenmanager import Screen
import config
from ui.modals import GameModal
class MainScreen(Screen):

    def __init__(self,CApp,**kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.app = CApp
        self.ids['version'].text = "Version %s" % config.CURRENT_VERSION

    def error_message(self,e):
        popup = GameModal()
        for i in e:
            popup.modal_txt.text += i + '\n'
        popup.close_btn.bind(on_release=self.app.stop)
        popup.close_btn.text = "Exit Concerto"
        popup.open()
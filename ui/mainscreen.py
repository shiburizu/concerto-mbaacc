from ui.concertoscreen import ConcertoScreen
import config

class MainScreen(ConcertoScreen):

    def __init__(self,CApp):
        super().__init__(CApp)
        self.ids['version'].text = "v%s" % config.CURRENT_VERSION
        if config.DEBUG_VERSION != "":
            self.ids['version'].text += " - %s" % config.DEBUG_VERSION
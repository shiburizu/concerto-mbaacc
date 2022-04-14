from ui.concertoscreen import ConcertoScreen
import config

class MainScreen(ConcertoScreen):

    def __init__(self,CApp):
        super().__init__(CApp)
        self.ids['version'].text = "Version %s" % config.CURRENT_VERSION
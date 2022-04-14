from ui.concertoscreen import ConcertoScreen

class HowtoScreen(ConcertoScreen):
    
    def __init__(self,CApp):
        super().__init__(CApp)
        for v in self.ids.values():
            try:
                v.colors['paragraph'] = 'ffffffff'
                v.colors['title'] = 'ffffffff'
                v.colors['bullet'] = 'ffffffff'
                v.colors['link'] = '00b7ffff'
            except AttributeError:
                pass
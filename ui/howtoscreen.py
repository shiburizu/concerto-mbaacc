from kivy.uix.screenmanager import Screen

class HowtoScreen(Screen):
    
    def __init__(self,**kwargs):
        super(HowtoScreen, self).__init__(**kwargs)
        for v in self.ids.values():
            try:
                v.colors['paragraph'] = 'ffffffff'
                v.colors['title'] = 'ffffffff'
                v.colors['bullet'] = 'ffffffff'
                v.colors['link'] = '00b7ffff'
            except AttributeError:
                pass
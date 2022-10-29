from kivy.uix.button import Button
from kivy.uix.anchorlayout import AnchorLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color,Rectangle

import ui.lang

class MenuBtn(Button):
    def __init__(self, **kwargs):
        if ui.lang.current_lang == "JA":
            #set fallback for non-Roman language
            self.font_name = 'res/JKG-M_3.ttf'
        else:
            self.font_name = 'res/texgyreheros-bolditalic.otf'
        super(MenuBtn, self).__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)
        self.hover = False
        

    def on_mouse_pos(self, *args):
        # Determine whether the control is in root In root control
        if not self.get_root_window():
            return
        # Get mouse position data
        pos = args[1]
        # Check whether the mouse position is in the control
        if self.collide_point(*pos):
            Clock.schedule_once(self.mouse_enter_css, 0)
        else:
            Clock.schedule_once(self.mouse_leave_css, 0)

    def mouse_leave_css(self, *args):
        if self.hover:
            self.canvas.before.clear()
            with self.canvas.before:
                Color(rgba=(0, 0, 0, 0))
                Rectangle(size=self.size,pos=self.pos)
            self.hover = False
        
    def mouse_enter_css(self, *args): 
        if not self.hover:
            self.canvas.before.clear()
            with self.canvas.before:
                Color(rgba=(255, 0, 0, 0.5))
                Rectangle(size=self.size,pos=self.pos)
            self.hover = True


class DummyBtn(Button):
    pass


class LobbyBtn(Button):
    pass


class PlayerRow(AnchorLayout):
    pass
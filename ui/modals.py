from kivy.uix.modalview import ModalView
from kivy.properties import ObjectProperty

class GameModal(ModalView):
    modal_txt = ObjectProperty(None)
    close_btn = ObjectProperty(None)
    p1_char_guide = ObjectProperty(None)
    p2_char_guide = ObjectProperty(None)

    def __init__(self,msg='',btntext='Dismiss',btnaction=None):
        super().__init__()
        self.modal_txt.text=msg
        self.close_btn.text=btntext
        if btnaction:
            self.close_btn.bind(on_release=btnaction)
        else:
            self.close_btn.bind(on_release=self.dismiss)

    def bind_btn(self,btnaction=None):
        if btnaction:
            self.close_btn.bind(on_release=btnaction)

class ProgressModal(ModalView):
    modal_txt = ObjectProperty(None)
    prog_bar = ObjectProperty(None)


class ChoiceModal(ModalView):
    modal_txt = ObjectProperty(None)
    btn_1 = ObjectProperty(None)
    btn_2 = ObjectProperty(None)

    def __init__(self,msg='',btn1txt='Option 1',btn1action=None,btn2txt='Option 2',btn2action=None):
        super().__init__()
        self.modal_txt.text=msg
        self.btn_1.text=btn1txt
        self.btn_2.text=btn2txt
        if btn1action != None:
            self.btn_1.bind(on_release=btn1action)
        if btn2action != None:
            self.btn_2.bind(on_release=btn2action)


class DirectModal(ModalView):
    join_ip = ObjectProperty(None)
    watch_ip = ObjectProperty(None)
    mode_type = ObjectProperty(None)
    screen = None


class FrameModal(ModalView):
    frame_txt = ObjectProperty(None)
    r_input = ObjectProperty(None)
    d_input = ObjectProperty(None)
    start_btn = ObjectProperty(None)
    close_btn = ObjectProperty(None)


class BroadcastModal(ModalView):
    game_type = ObjectProperty(None)
    screen = None
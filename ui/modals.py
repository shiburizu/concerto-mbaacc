from kivy.uix.modalview import ModalView
from kivy.properties import ObjectProperty


class GameModal(ModalView):
    modal_txt = ObjectProperty(None)
    close_btn = ObjectProperty(None)


class ProgressModal(ModalView):
    modal_txt = ObjectProperty(None)
    prog_bar = ObjectProperty(None)


class ChoiceModal(ModalView):
    modal_txt = ObjectProperty(None)
    btn_1 = ObjectProperty(None)
    btn_2 = ObjectProperty(None)


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
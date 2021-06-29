from kivy.uix.modalview import ModalView
from kivy.properties import ObjectProperty


class GameModal(ModalView):
    modal_txt = ObjectProperty(None)
    close_btn = ObjectProperty(None)


class DirectModal(ModalView):
    join_ip = ObjectProperty(None)
    watch_ip = ObjectProperty(None)
    screen = None


class FrameModal(ModalView):
    frame_txt = ObjectProperty(None)
    r_input = ObjectProperty(None)
    d_input = ObjectProperty(None)
    start_btn = ObjectProperty(None)
    close_btn = ObjectProperty(None)

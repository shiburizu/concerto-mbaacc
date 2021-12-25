from kivy.uix.screenmanager import Screen
from requests.models import HTTPError
import config
from ui.modals import GameModal, ProgressModal, ChoiceModal
import requests
import urllib3
import os
import subprocess
import threading
from functools import partial

class MainScreen(Screen):

    def __init__(self,CApp,**kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.app = CApp
        self.ids['version'].text = "Version %s" % config.CURRENT_VERSION
        self.active_pop = None

    def error_message(self,e,passive=False):
        if self.active_pop:
            self.active_pop.dismiss()
            self.active_pop = None
        popup = GameModal()
        for i in e:
            popup.modal_txt.text += i + '\n'
        if passive:
            popup.close_btn.bind(on_release=popup.dismiss)
            popup.close_btn.text = "Dismiss"
        else:
            popup.close_btn.bind(on_release=self.app.stop)
            popup.close_btn.text = "Exit Concerto"
        popup.open()

    def update(self):
        choice = ChoiceModal()
        self.active_pop = choice
        choice.modal_txt.text = "Checking for update..."
        choice.btn_1.text = "Close"
        choice.btn_2.text = "Confirm"
        choice.btn_1.disabled = True
        choice.btn_2.disabled = True
        choice.btn_1.bind(on_release=choice.dismiss)
        choice.open()
        update = self.check_update()
        if update is None:
            self.error_message(['No update found!'],passive=True)
        else:
            choice.modal_txt.text = "An update is available. Would you like to download? Concerto will restart automatically after completion."
            choice.btn_2.disabled = False
            choice.btn_1.disabled = False
            choice.btn_2.bind(on_release=partial(self.start_updater,update = update))

    def start_updater(self,obj,update,*args):
        if self.active_pop:
            self.active_pop.dismiss()
            self.active_pop = None
        popup = ProgressModal()
        popup.prog_bar.max = 100
        popup.open()
        threading.Thread(target=self.download_update,args=[update,popup],daemon=True).start()
            
    def check_update(self):
        #returns None if no update needed
        release_url = 'https://api.github.com/repos/shiburizu/concerto-mbaacc/releases/latest'
        try:
            latest_release_req = requests.get(release_url,timeout=5)
            latest_release_req.raise_for_status()
        except requests.exceptions.RequestException:
            return None
        latest_release_data = latest_release_req.json()
        latest_release_tag = latest_release_data['tag_name']
        if config.CURRENT_VERSION == latest_release_tag:
            return None
        else:
            return latest_release_data

    def download_update(self,update,popup):
        popup.modal_txt.text = "Starting update download..."
        latest_concerto_url = None
        for asset in update['assets']:
            asset_url = asset['browser_download_url']
            if 'Concerto.exe' in asset_url:
                latest_concerto_url = asset_url
        if latest_concerto_url == None:
            return None
        # Taken and modified for Python3 from https://gist.github.com/gesquive/8363131
        http = urllib3.PoolManager()
        app_path = config.PATH + 'Concerto.exe'
        dl_path = app_path + ".new"
        backup_path = app_path + ".old"
        try:
            dl_file = open(dl_path, 'wb')
            http_stream = http.request('GET', latest_concerto_url, preload_content=False)
            total_size = None
            bytes_so_far = 0
            chunk_size = 8192
            try:
                total_size = int(http_stream.headers['Content-Length'].strip())
            except:
                # The header is improper or missing Content-Length, just download
                dl_file.write(http_stream.read())
                popup.modal_txt.text = "Unable to confirm download size. Still downloading..."
                popup.prog_bar.value = 100
            while total_size:
                chunk = http_stream.read(chunk_size)
                dl_file.write(chunk)
                bytes_so_far += len(chunk)
                if not chunk:
                    break
                percent = float(bytes_so_far) / total_size
                percent = round(percent*100, 2)
                popup.modal_txt.text = "Downloaded %d of %d bytes (%0.2f%%)" % (bytes_so_far, total_size, percent)
                popup.prog_bar.value = percent
            http_stream.close()
            dl_file.close()
        except (IOError, urllib3.exceptions.HTTPError):
            self.error_message("Failed to download.",passive=True)
            return None
        update_script = open('update.bat', 'w')
        update_script.writelines([
            'taskkill /f /im Concerto.exe'
            'COPY "%s" "%s"\n' % (app_path, backup_path),
            'COPY "%s" "%s" /Y\n' % (dl_path, app_path), 
            'DEL "%s"\n' % dl_path, 
            'DEL "%s"\n' % backup_path,
            'START "" "%s"\n' % app_path,
            'DEL "%~f0"'])
        update_script.close()
        subprocess.Popen(os.getcwd() + '\\update.bat', shell=True)
        self.app.stop()
from kivy.uix.screenmanager import Screen
import config
from ui.modals import GameModal
import requests
import urllib3
import sys
import os
import subprocess

class MainScreen(Screen):

    def __init__(self,CApp,**kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.app = CApp
        self.ids['version'].text = "Version %s" % config.CURRENT_VERSION
        self.active_pop = None

    def error_message(self,e):
        popup = GameModal()
        for i in e:
            popup.modal_txt.text += i + '\n'
        popup.close_btn.bind(on_release=self.app.stop)
        popup.close_btn.text = "Exit Concerto"
        popup.open()
        
    def check_update(self):
        #returns None if no update needed
        release_url = 'https://api.github.com/repos/shiburizu/concerto-mbaacc/releases/latest'
        
        latest_release_req = requests.get(release_url)
        latest_release_data = latest_release_req.json()
        
        latest_release_tag = latest_release_data['tag_name']

        if config.CURRENT_VERSION == latest_release_tag:
            return None
        else:
            return latest_release_data

    def auto_update(self):
        update = self.check_update()
        if not update:
            return None

        latest_concerto_url = None

        for asset in update['assets']:
            asset_url = asset['browser_download_url']
            if 'Concerto.exe' in asset_url:
                latest_concerto_url = asset_url

        if latest_concerto_url == None:
            return None

        # Taken and modified for Python3 from https://gist.github.com/gesquive/8363131
        http = urllib3.PoolManager()

        app_path = os.getcwd() + '\\Concerto.exe'
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

            while total_size:
                chunk = http_stream.read(chunk_size)
                dl_file.write(chunk)
                bytes_so_far += len(chunk)

                if not chunk:
                    break

                percent = float(bytes_so_far) / total_size
                percent = round(percent*100, 2)
                sys.stdout.write("Downloaded %d of %d bytes (%0.2f%%)\r" %
                    (bytes_so_far, total_size, percent))

                if bytes_so_far >= total_size:
                    sys.stdout.write('\n')

            http_stream.close()
            dl_file.close()
        except IOError:
            print("Download failed")
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
        sys.exit()
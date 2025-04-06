from winpty import PtyProcess  # pywinpty
from datetime import datetime
import re
import time
import subprocess
import threading
from config import *
#stats
import ctypes
from ctypes.wintypes import *
import presence
import sys
import os, os.path
from functools import partial

from kivy.clock import Clock

from ui.lang import *

#stats constants
STRLEN = 1
PROCESS_VM_READ = 0x0010
k32 = ctypes.WinDLL('kernel32')
k32.OpenProcess.argtypes = DWORD, BOOL, DWORD
k32.OpenProcess.restype = HANDLE
k32.ReadProcessMemory.argtypes = HANDLE,LPVOID,LPVOID,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t)
k32.ReadProcessMemory.restype = BOOL
buf = ctypes.create_string_buffer(STRLEN)
s = ctypes.c_size_t()

# Character associations
CHARACTER = {
    0 : "Sion",
    1 : "Arcueid",
    2 : "Ciel",
    3 : "Akiha",
    4 : "Maids",
    5 : "Hisui",
    6 : "Kohaku",
    7 : "Tohno",
    8 : "Miyako",
    9 : "Warakia",
    10 : "Nero",
    11 : "V.Sion",
    12 : "Red Arcueid",
    13 : "V.Akiha",
    14 : "Mech-Hisui",
    15 : "Nanaya",
    17 : "Satsuki",
    18 : "Len",
    19 : "Powerd Ciel",
    20 : "Neco Arc",
    22 : "Aoko",
    23 : "White Len",
    25 : "NAC",
    28 : "Kouma",
    29 : "Seifuku",
    30 : "Riesbyfe",
    31 : "Roa",
    32 : "Dust of Osiris",
    33 : "Ryougi",
    34 : "Neco-Mech",
    35 : "Koha-Mech",
    51 : "Hime"
}

MOON = {
    0 : 'C',
    1 : 'F',
    2 : 'H'
}

#error messages
error_strings = [
    'Internal error!',
    'Cannot find host', #get host missing
    'Cannot initialize networking!',
    'Network error!',
    'already being used!',
    'Too many duplicate joysticks',
    'Failed to initialize controllers!',
    'Failed to check controllers!',
    'Port must be less than 65536!',
    'Invalid IP address and/or port!',
    'Failed to start game!',
    'Failed to communicate with', #with?
    'Unhandled game mode!',
    'Host sent invalid configuration!',
    'Delay must be less than 255!',
    'Rollback must be less than', #need to find out what the error message here is
    'Rollback data is corrupted!',
    'Missing relay_list.txt!',
    'Missing lobby_list.txt!',
    'Couldn\'t find MBAA.exe!',
    'Timed out!',
    'Network delay greater than limit',
    'Incompatible cccaster\hook.dll!',
    'Latest version is',
    'Update?',
    'Incompatible host version',
    'Disconnected!',
    'Another client is currently connecting!'
]

ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
caster_button = re.compile(r'\[[0-9]\]')

regex_spec_names = r'Spectating\s+(versus|training)\s+mode\s+\((\d+)\s+delay,\s+(\d+)\s+(?:rolback|rollback)\)\s+(.+)\s+(\(.+\))\s+vs\s+(.+)\s+(\(.+\))\s+\(Tap\s+the\s+spacebar\s+to\s+toggle\s+fast-forward\)'
regex_network_delay = r'Network\s+delay:\s+(\d+)' #1: network delay
regex_ping = r'Ping:\s+(\d+.\d+)\s+ms' #1 ping value
regex_game_mode = r'\s+(Versus)\s+mode,\s+each\s+game\s+is\s+(\d+)\s+rounds|(Training)\s+mode' #1: mode, #2: rounds
regex_connected_to_player = r'(?:Connected|Conected)\s+to\s+(.+)(?:Versus|Training)' #1: player name (host)
regex_player_connected = r'(.+)\s+(?:connected|conected)\s+(?:Versus|Training)' #1: player name (guest)
regex_rollback_frames = r'Enter\s+max\s+frames\s+of\s+(?:rolback|rollback):\s+(\d+)' #1: rollback frames

TUI_JUNK = ["\x08", "*", "0;", "19G", "\x1b[", "0;30;8m", "38m", "CCCaster 3.1", "[1] Lobby","[2] Matchmaking","[0] Cancel","[1] Netplay", "[2] Spectate", "[3] Broadcast", "[4] Offline", "[5] Server", "[6] Controls", "[7] Settings", "[8] Update", "[9] Results", "[0] Quit"]

def clean_output(read,tui=False):
    dirty_read = re.sub(ansi_escape,'', read)
    if tui == True:
        for j in TUI_JUNK:
            dirty_read = dirty_read.replace(j,'')
    clean_read = ""
    for i in dirty_read.split():
        bit = i.replace('*','').strip()
        if bit != '':
            clean_read += bit + " "
    return clean_read.strip()

def pick_last(pattern,read):
    res = re.findall(pattern,read)
    if res != [] and res != None:
        if isinstance(res[-1],tuple):
            return [i for i in res[-1] if i != '']
        else:
            if isinstance(res[-1],str):
                return res[-1].strip()
            else:   
                return res[-1]
    else:
        return []

def get_session_info(read,spectator=False):
    e = []
    for i in error_strings:
        if i in read:
            if i == 'Latest version is' or i == 'Update?': #update prompt
                e.append("A new version of CCCaster is available. Please update by opening CCCaster.exe manually or downloading manually from concerto.shib.live.")
            else:
                e.append(i)
            logger.write('\n%s\n' % e)
    if e != []:
        return {'role': 'error','errors': e}
    # insert error message checking HERE so that we can make this all-in-one
    if spectator == False:
        session_info = {
            'role' : 'waiting',
            'delay' : pick_last(regex_network_delay,read),
            'ping' : pick_last(regex_ping,read),
            'mode' : pick_last(regex_game_mode,read),
            'rollback': pick_last(regex_rollback_frames,read)
        }
        host = pick_last(regex_player_connected,read)
        if host != []:
            session_info['role'] = 'host'
            session_info['opponent'] = host
        else:
            guest = pick_last(regex_connected_to_player,read)
            if guest != []:
                session_info['role'] = 'guest'
                session_info['opponent'] = guest
            else:
                session_info['role'] = 'unknown'
        for i in list(session_info.keys()):
            if session_info[i] == []:
                return { 'role' : 'waiting' } #force empty return if any empty keys
        print(session_info)
        return session_info             
    else:
        spec_info = pick_last(regex_spec_names,read)
        if spec_info != [] and spec_info != None:
            session_info = {
                'role' : 'spectator',
                'mode' : spec_info[0],
                'delay' : spec_info[1],
                'rollback' : spec_info[2],
                'player1' : spec_info[3],
                'char1' : spec_info[4],
                'player2' : spec_info[5],
                'char2' : spec_info[6]
            }
            print(session_info)
            return session_info
        else:
            return { 'role' : 'waiting' }

class loghelper():
    dateTimeObj = datetime.now()
    timestampStr = 'Concerto_' + \
        dateTimeObj.strftime("%d-%b-%Y-%H-%M-%S") + '.txt'

    def write(self, s):
        if not os.path.isdir(PATH + 'concerto-logs'):
            os.mkdir(PATH + 'concerto-logs')
        with open(PATH + 'concerto-logs\\' + self.timestampStr, encoding='utf-8', mode='a') as log:
            log.write(s)

logger = loghelper()

# Write player name to a file.  Called when spectate mode begins.
def write_name_to_file(player_num: int, name: str):
    with open(f'p{player_num}name.txt', encoding='utf-8', mode='w') as file:
        file.write(name)
        file.close()

# Write a score of 0.  Called when spectate mode begins.
def reset_score_file(player_num: int):
    with open(f'p{player_num}score.txt', encoding='utf-8', mode='w') as file:
        file.write('0')
        file.close()

# Read the value in the file and increment it.  It can be manually reset by the user this way.
def increment_score_file(player_num: int):
    with open(f'p{player_num}score.txt', mode='r+') as file:
        try:
            score = int(file.readline())
        except ValueError:
            score = 0
        score = score+1
        file.seek(0)
        file.truncate()
        file.write(str(score))
        file.close()

class Caster():

    def __init__(self, CApp):
        self.app = CApp
        self.adr = None #our IP when hosting, needed to trigger UI actions
        self.playing = False #True when netplay begins via input to CCCaster
        self.rs = -1 # Caster's suggested rollback frames. Sent to UI.
        self.ds = -1 # delay suggestion
        self.aproc = None # active caster Thread object to check for isalive()
        self.tproc = None # caster Thread object created to enter Training mode during host
        self.offline = False #True when an offline mode has been started
        self.broadcasting = False #True when Broadcasting offline has been started
        self.startup = False #True when waiting for MBAA.exe to start in offline
        self.stats = {} #dict of information we can read from memory
        self.pid = None #PID of MBAA.exe

    def validate_read(self, con):
        if "rollback:" in con or "rolback:" in con:
            conlst = con.split() # split string into list
            r = 0 #count all items before "rollback:" in list
            for i in reversed(conlst):
                if i != 'rollback:' and i != 'rolback:':
                    r += 1
                else:
                    break
            if r > 0: #if the list of items after "rollback:" > 0...
                rlst = re.sub("[^0-9]", "", ''.join(conlst[-r:])) # ...find all numbers in the list
                if len(rlst) > 0:  # ...if there's at least one number, proceed (rollback suggested frames)
                    #sanitize list: remove floats, floats with %, and whole with %s
                    con = re.sub('\d+\.\d+', '', con)
                    con = re.sub('\d+\.\d+%','',con)
                    con = re.sub('\d+%','',con)
                    conlst = con.split()
                    n = [i for i in re.findall(
                        '[0-9]+', ' '.join(conlst)) if int(i) < 15] #now find all whole numbers
                    if len(n) >= 2: #at least 2 numbers need to be in our filtered list
                        logger.write('\nrblst: %s\n' % rlst) #logger stuff
                        logger.write('\nn: %s\n' % n)
                        logger.write('\nVALID READ:\n%s\n' % con.split())
                        return n #return list
        return False

    def matchmaking(self, sc, wins=0): #sc is a Screen for UI triggers
        self.kill_caster()
        self.app.offline_mode = None
        try:
            self.aproc = PtyProcess.spawn(app_config['settings']['caster_exe'].strip())
        except FileNotFoundError:
            sc.error_message('%s not found.' % app_config['settings']['caster_exe'].strip())
            return None 
        time.sleep(0.5) #UI trigger
        dialog = sc.active_pop.modal_txt.text
        # Stats
        while self.aproc.isalive():
            con = self.aproc.read()
            logger.write('\n%s\n' % con.split())
            if self.find_button(con.split(),'Server',self.aproc):
                self.aproc.write('2')
                break
            else:
                if self.check_msg(con) != []:
                    sc.error_message(self.check_msg(con))
                    break
        
        threading.Thread(target=self.update_stats,args=[wins],daemon=True).start()

        cur_con = ""
        last_con = ""
        con = ""

        logger.write('\n== Matchmaking ==\n')
        while self.aproc != None and self.aproc.isalive():
            
            cur_con = ansi_escape.sub('', str(self.aproc.read()))
            cur_con_clean = ""
            for i in cur_con.split():
                if i.replace('*','').strip() != '':
                    cur_con_clean += " " + i #this removes ***** junk from caster output
            if cur_con_clean not in last_con: #we compare against the last fragment to check for dup output
                con += last_con + cur_con_clean #con is what we send to validate_read
            elif last_con in cur_con_clean:
                con += cur_con_clean

            logger.write('\n=================================\n' + str(con.split()))

            if self.playing == False and self.ds == -1 and self.rs == -1:
                session_info = get_session_info(clean_output(con))
                if session_info['role'] == 'error':
                    sc.error_message(session_info['errors'])
                    self.kill_caster()
                    break
                elif session_info['role'] != 'waiting':
                    if int(session_info['delay']) - int(session_info['rollback']) < 0:
                        self.ds = 0
                    else:
                        self.ds = int(session_info['delay']) - int(session_info['rollback'])
                    self.rs = int(session_info['rollback'])
                    if session_info['mode'][0] == 'Training':
                        session_info['mode'].append('0')

                    if app_config['settings']['write_scores'] == '1':
                        write_name_to_file(1, 'NETPLAY P1')
                        write_name_to_file(2, 'NETPLAY P2')
                        reset_score_file(1)
                        reset_score_file(2)
                    Clock.schedule_once(partial(self.ui_set_frames,sc,session_info['opponent'],session_info['delay'],session_info['ping'],session_info['mode'][0],session_info['mode'][1]))
                else:
                    if last_con != cur_con:
                        last_con = cur_con
                    if "Hosting at server" in cur_con:
                        sc.active_pop.modal_txt.text = dialog + "\n(Hosting, waiting for connection...)"
                    elif "Waiting for opponent" in cur_con:
                        sc.active_pop.modal_txt.text = dialog + "\n(Waiting for opponent...)"
                    elif "Trying connection (UDP" in cur_con:
                        sc.active_pop.modal_txt.text = dialog + "\n(Trying connection (UDP Tunnel)...)"
                    elif "Trying connection" in cur_con:
                        sc.active_pop.modal_txt.text = dialog + "\n(Trying connection...)"
                    continue
            else:
                break

    def host(self, sc, port='0', mode="Versus",t=None, wins=0): #sc is a Screen for UI triggers
        self.kill_caster()
        self.app.offline_mode = None
        try:
            self.aproc = PtyProcess.spawn('%s -n %s %s' % (app_config['settings']['caster_exe'].strip(),"-t" if mode == "Training" else "",port))
        except FileNotFoundError:
            sc.error_message('%s not found.' % app_config['settings']['caster_exe'].strip())
            return None       

        # Stats
        threading.Thread(target=self.update_stats,args=[wins],daemon=True).start()

        logger.write('\n== Host ==\n')
        while self.aproc.isalive(): # find IP and port combo for host
            read = self.aproc.read()
            ip = re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{,5}', read)
            if ip != []:
                self.adr = str(ip[0])
                sc.set_ip(self.adr) #tell UI we have the IP address
                break
            elif self.check_msg(read) != []:
                sc.error_message(self.check_msg(read))
                return None
        logger.write('Host IP: %s\n' % self.adr)

        cur_con = "" #current Caster read
        last_con = "" #last Caster read
        con = "" #cumulative string of all cur_con reads

        while self.aproc.isalive():

            cur_con = ansi_escape.sub('', str(self.aproc.read()))
            cur_con_clean = ""
            for i in cur_con.split():
                if i.replace('*','').strip() != '':
                    cur_con_clean += " " + i #this removes ***** junk from caster output
            if cur_con_clean not in last_con: #we compare against the last fragment to check for dup output
                con += last_con + cur_con_clean #con is what we send to validate_read
            elif last_con in cur_con_clean:
                con += cur_con_clean

            logger.write('\n=================================\n' + str(con.split()))

            if self.playing == False and self.ds == -1 and self.rs == -1:
                session_info = get_session_info(clean_output(con))
                if session_info['role'] == 'error':
                    sc.error_message(session_info['errors'])
                    self.kill_caster()
                    break
                elif session_info['role'] != 'waiting':
                    if int(session_info['delay']) - int(session_info['rollback']) < 0:
                        self.ds = 0
                    else:
                        self.ds = int(session_info['delay']) - int(session_info['rollback'])
                    self.rs = int(session_info['rollback'])
                    if session_info['mode'][0] == 'Training':
                        session_info['mode'].append('0')

                    if app_config['settings']['write_scores'] == '1':
                        write_name_to_file(1, 'NETPLAY P1')
                        write_name_to_file(2, 'NETPLAY P2')
                        reset_score_file(1)
                        reset_score_file(2)
                    Clock.schedule_once(partial(self.ui_set_frames,sc,session_info['opponent'],session_info['delay'],session_info['ping'],session_info['mode'][0],session_info['mode'][1],t))
                else:
                    if last_con != cur_con:
                        last_con = cur_con
                    continue
            else:
                break

    def join(self, ip, sc, t=None, wins=0, *args): #sc is a Screen for UI triggers
        self.kill_caster()
        self.app.offline_mode = None
        try:
            self.aproc = PtyProcess.spawn('%s -n %s' % (app_config['settings']['caster_exe'].strip(),ip)) 
        except FileNotFoundError:
            sc.error_message('%s not found.' % app_config['settings']['caster_exe'].strip())
            return None  

        # Stats
        threading.Thread(target=self.update_stats,args=[wins],daemon=True).start()

        logger.write('\n== Join ==\n')

        cur_con = "" #current Caster read
        last_con = "" #last Caster read
        con = "" #cumulative string of all cur_con reads

        while self.aproc.isalive():

            cur_con = ansi_escape.sub('', str(self.aproc.read()))
            cur_con_clean = ""
            for i in cur_con.split():
                if i.replace('*','').strip() != '':
                    cur_con_clean += " " + i #this removes ***** junk from caster output
            if cur_con_clean not in last_con: #we compare against the last fragment to check for dup output
                con += last_con + cur_con_clean #con is what we send to validate_read
            elif last_con in cur_con_clean:
                con += cur_con_clean

            logger.write('\n=================================\n' + str(con.split()))

            if self.playing == False and self.ds == -1 and self.rs == -1:
                session_info = get_session_info(clean_output(con))        
                if session_info['role'] == 'error':
                    sc.error_message(session_info['errors'])
                    self.kill_caster()
                    break
                elif session_info['role'] != 'waiting':
                    if int(session_info['delay']) - int(session_info['rollback']) < 0:
                        self.ds = 0
                    else:
                        self.ds = int(session_info['delay']) - int(session_info['rollback'])
                    self.rs = int(session_info['rollback'])
                    if session_info['mode'][0] == 'Training':
                        session_info['mode'].append('0')

                    if app_config['settings']['write_scores'] == '1':
                        write_name_to_file(1, 'NETPLAY P1')
                        write_name_to_file(2, 'NETPLAY P2')
                        reset_score_file(1)
                        reset_score_file(2)
                    Clock.schedule_once(partial(self.ui_set_frames,sc,session_info['opponent'],session_info['delay'],session_info['ping'],session_info['mode'][0],session_info['mode'][1],t))
                else:
                    if "Calculating delay" in clean_output(con):
                        sc.calculating_delay()
                    if last_con != cur_con:
                        last_con = cur_con
                    continue
            else:
                break

    def ui_set_frames(self,sc,opponent_name,delay,ping,m=None,rd=None,t=None,*args):
        sc.set_frames(opponent_name,delay,ping,mode=m,rounds=rd,target=t)

    def confirm_frames(self,rf,df,*args):
        self.kill_host_training()
        if self.aproc:
            self.aproc.write(str(rf))
            self.aproc.write('\x0D')
            time.sleep(0.5)
            self.aproc.write(str(df))
            self.aproc.write('\x0D')
            self.playing = True

    def watch(self, ip, sc, *args):
        self.kill_caster()
        try:
            self.aproc = PtyProcess.spawn('%s -n -s %s' % (app_config['settings']['caster_exe'].strip(),ip))
        except FileNotFoundError:
            sc.error_message('%s not found.' % app_config['settings']['caster_exe'].strip())
            return None

        threading.Thread(target=self.update_stats,daemon=True).start()

        logger.write('\n== Watch %s ==\n' % ip)
        cur_con = ""
        last_con = ""
        con = ""
        self.broadcasting = True

        while self.aproc.isalive():

            cur_con = ansi_escape.sub('', str(self.aproc.read()))
            cur_con_clean = ""
            for i in cur_con.split():
                if i.replace('*','').strip() != '':
                    cur_con_clean += " " + i #this removes ***** junk from caster output
            if cur_con_clean not in last_con: #we compare against the last fragment to check for dup output
                con += last_con + cur_con_clean #con is what we send to validate_read
            elif last_con in cur_con_clean:
                con += cur_con_clean
            
            logger.write('\n=================================\n' + str(con.split()))

            session_info = get_session_info(clean_output(con),spectator=True)

            if session_info['role'] == 'error':
                sc.error_message(session_info['errors'])
                self.kill_caster()
                break
            elif session_info['role'] == 'spectator':
                logger.write('\n=================================\n')
                logger.write(str(con.split()))
                self.aproc.write('1')
                if app_config['settings']['write_scores'] == '1':
                    write_name_to_file(1, session_info['player1'])
                    write_name_to_file(2, session_info['player2'])
                    reset_score_file(1)
                    reset_score_file(2)
                sc.active_pop.modal_txt.text = "Spectating %s mode (%s delay, %s rollback)\n%s %s vs %s %s\n(Tap the spacebar to toggle fast-forward)" % (
                    session_info['mode'],session_info['delay'],session_info['rollback'],session_info['player1'],session_info['char1'],
                    session_info['player2'],session_info['char2'])
                break

    def broadcast(self, sc, port='0', mode="Versus"): #sc is a Screen for UI triggers
        self.kill_caster()
        if app_config['settings']['write_scores'] == '1':
            write_name_to_file(1, 'LOCAL P1')
            write_name_to_file(2, 'LOCAL P2')
            reset_score_file(1)
            reset_score_file(2)
        try:
            if mode == "Training":
                self.aproc = PtyProcess.spawn('%s -n -b -t %s' % (app_config['settings']['caster_exe'].strip(),port)) 
            else:
                self.aproc = PtyProcess.spawn('%s -n -b %s' % (app_config['settings']['caster_exe'].strip(),port))
        except FileNotFoundError:
            sc.error_message('%s not found.' % app_config['settings']['caster_exe'].strip())
            return None
        logger.write('\n== Broadcast %s ==\n' % mode)
        self.broadcasting = True
        threading.Thread(target=self.update_stats,daemon=True).start()
        while self.aproc.isalive(): # find IP and port combo for host
            t = self.aproc.read()
            ip = re.findall(
                r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{,5}', t)
            if ip != []:
                self.adr = str(ip[0])
                sc.set_ip(self.adr)
                break
            elif self.check_msg(t) != []:
                sc.error_message(self.check_msg(t))
                return None

    def training(self,sc):
        self.kill_caster()
        self.startup = True
        try:
            proc = PtyProcess.spawn(app_config['settings']['caster_exe'].strip())
        except FileNotFoundError:
            sc.error_message('%s not found.' % app_config['settings']['caster_exe'].strip())
            return None
        self.aproc = proc
        logger.write('\n== Training ==\n')
        while self.aproc.isalive():
            con = self.aproc.read()
            logger.write('\n%s\n' % con.split())
            if self.find_button(con.split(),'Offline',self.aproc) or self.find_button(con.split(),'Ofline',self.aproc):
                self.aproc.write('1')
                self.flag_offline(sc)
                break
            else:
                if self.check_msg(con) != []:
                    sc.error_message(self.check_msg(con))
                    break

    def host_training(self,sc,*args):
        self.startup = True
        try:
            proc = PtyProcess.spawn(app_config['settings']['caster_exe'].strip())
        except FileNotFoundError:
            sc.error_message('%s not found.' % app_config['settings']['caster_exe'].strip())
            return None
        self.tproc = proc
        logger.write('\n== Host Training ==\n')
        while self.tproc.isalive():
            con = self.tproc.read()
            logger.write('\n%s\n' % con.split())
            if self.find_button(con.split(),'Offline',self.tproc) or self.find_button(con.split(),'Ofline',self.tproc):
                self.tproc.write('1')
                break
            else:
                if self.check_msg(con) != []:
                    sc.error_message(self.check_msg(con))
                    break 

    def local(self,sc):
        self.kill_caster()
        self.startup = True
        if app_config['settings']['write_scores'] == '1':
            write_name_to_file(1, 'LOCAL P1')
            write_name_to_file(2, 'LOCAL P2')
            reset_score_file(1)
            reset_score_file(2)
        try:
            proc = PtyProcess.spawn(app_config['settings']['caster_exe'].strip())
        except FileNotFoundError:
            sc.error_message('%s not found.' % app_config['settings']['caster_exe'].strip())
            return None
        self.aproc = proc
        while self.aproc.isalive():
            con = self.aproc.read()
            if self.find_button(con.split(),'Offline',self.aproc) or self.find_button(con.split(),'Ofline',self.aproc):
                self.aproc.write('2')
                self.flag_offline(sc)
                break
            else:
                if self.check_msg(con) != []:
                    sc.error_message(self.check_msg(con))
                    break

    def cpu(self,sc):
        self.kill_caster()
        self.startup = True
        try:
            proc = PtyProcess.spawn(app_config['settings']['caster_exe'].strip())
        except FileNotFoundError:
            sc.error_message('%s not found.' % app_config['settings']['caster_exe'].strip())
            return None
        self.aproc = proc
        while self.aproc.isalive():
            con = self.aproc.read()
            if self.find_button(con.split(),'Offline',self.aproc) or self.find_button(con.split(),'Ofline',self.aproc):
                self.aproc.write('3')
                self.flag_offline(sc)
                break
            else:
                if self.check_msg(con) != []:
                    sc.error_message(self.check_msg(con))
                    break

    def trials(self,sc):
        self.kill_caster()
        self.startup = True
        try:
            proc = PtyProcess.spawn(app_config['settings']['caster_exe'].strip())
        except FileNotFoundError:
            sc.error_message('%s not found.' % app_config['settings']['caster_exe'].strip())
            return None
        self.aproc = proc
        while self.aproc.isalive():
            con = self.aproc.read()
            if self.find_button(con.split(),'Offline',self.aproc) or self.find_button(con.split(),'Ofline',self.aproc):
                self.aproc.write('6')
                self.flag_offline(sc)
                break
            else:
                if self.check_msg(con) != []:
                    sc.error_message(self.check_msg(con))
                    break

    def tournament(self,sc):
        self.kill_caster()
        self.startup = True
        if app_config['settings']['write_scores'] == '1':
            write_name_to_file(1, 'LOCAL P1')
            write_name_to_file(2, 'LOCAL P2')
            reset_score_file(1)
            reset_score_file(2)
        try:
            proc = PtyProcess.spawn(app_config['settings']['caster_exe'].strip())
        except FileNotFoundError:
            sc.error_message('%s not found.' % app_config['settings']['caster_exe'].strip())
            return None
        self.aproc = proc
        while self.aproc.isalive():
            con = self.aproc.read()
            if self.find_button(con.split(),'Offline',self.aproc) or self.find_button(con.split(),'Ofline',self.aproc):
                self.aproc.write('4')
                self.flag_offline(sc)
                break
            else:
                if self.check_msg(con) != []:
                    sc.error_message(self.check_msg(con))
                    break

    def replays(self,sc):
        self.kill_caster()
        self.startup = True
        if app_config['settings']['write_scores'] == '1':
            write_name_to_file(1, 'REPLAY P1')
            write_name_to_file(2, 'REPLAY P2')
            reset_score_file(1)
            reset_score_file(2)
        try:
            proc = PtyProcess.spawn(app_config['settings']['caster_exe'].strip())
        except FileNotFoundError:
            sc.error_message('%s not found.' % app_config['settings']['caster_exe'].strip())
            return None
        self.aproc = proc
        while self.aproc.isalive():
            con = self.aproc.read()
            if self.find_button(con.split(),'Offline',self.aproc) or self.find_button(con.split(),'Ofline',self.aproc):
                self.aproc.write('5')
                self.flag_offline(sc)
                break
            else:
                if self.check_msg(con) != []:
                    sc.error_message(self.check_msg(con))
                    break
    
    def standalone(self,sc):
        self.kill_caster()
        try:
            self.aproc = PtyProcess.spawn('MBAA.exe')
            self.flag_offline(sc,stats=False)
        except FileNotFoundError:
            sc.error_message('MBAA.exe not found.')
            return None

    def find_button(self,read,term,proc):
        current_btn = None
        if term in read:
            for i in read:
                if i == term and current_btn != None:
                    proc.write(current_btn)
                    time.sleep(0.1)
                    return True
                else:
                    btn = re.findall(caster_button,i)
                    if len(btn) != 0:
                        current_btn = btn[0].replace('[','')
                        current_btn = current_btn.replace(']','') 
            return False
        else:
            return False

    def flag_offline(self,sc,stats=True): #stats tells us whether or not to pull info from the game
        while True:
            cmd = f"""tasklist /FI "IMAGENAME eq mbaa.exe" /FO CSV /NH"""
            task_data = subprocess.check_output(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL).decode("UTF8","ignore")
            try:
                task_data.replace("\"", "").split(",")[1]
            except IndexError:
                pass
            else:
                if self.offline is False:
                    self.startup = False
                    self.offline = True
                    if stats is True:
                        threading.Thread(target=self.update_stats,daemon=True).start()
                    break
            if self.aproc != None:
                if self.aproc.isalive() is False:
                    break
            else:
                break
        sc.dismiss_active_pop()

    def find_pid(self):
        if self.pid == None:
            cmd = f"""tasklist /FI "IMAGENAME eq mbaa.exe" /FO CSV /NH"""
            task_data = subprocess.check_output(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL).decode("UTF8","ignore")
            try:
                pid = task_data.replace("\"", "").split(",")[1]
            except IndexError:
                return False
            else:
                try:
                    self.pid = k32.OpenProcess(PROCESS_VM_READ, 0, int(pid))
                except ValueError:
                    return False
                else:
                    return True 
        else:
            return True
    
    def update_stats(self,once=False,wins=0):
        # Used to update presence only on state change 
        state = None
        p1wins = 0
        p2wins = 0
        p1_set_wins = 0
        p2_set_wins = 0
        replay_count = len(os.listdir(os.getcwd() + '\ReplayVS')) #to check for set limit conditions
        menu_value = None #set to menucount addr when entering retry screen 
        while True:
            if self.aproc is None:
                break
            if self.find_pid():
                self.stats = {
                    "state": self.read_memory(0x54EEE8),
                    "p1char": self.read_memory(0x74D8FC),
                    "p1moon": self.read_memory(0x74D900),
                    "p1color": self.read_memory(0x74D904),
                    "p2char": self.read_memory(0x74D920),
                    "p2moon": self.read_memory(0x74D924),
                    "p2color": self.read_memory(0x74D928),
                    "p1wins": self.read_memory(0x559550),
                    "p2wins": self.read_memory(0x559580),
                    "towin": self.read_memory(0x553FDC),
                    "menucount" : self.read_memory(0x767440)
                }
                if self.app.discord is True:
                # Check if in game once
                    if self.stats["state"] == 1 and self.stats["state"] != state:
                        p1_char = "%s-" % MOON[self.stats["p1moon"]] + CHARACTER[self.stats["p1char"]]
                        p2_char = "%s-" % MOON[self.stats["p2moon"]] + CHARACTER[self.stats["p2char"]]
                        if self.broadcasting:
                            mode = self.app.offline_mode
                            if mode.lower() == 'spectating':
                                mode = "Spectating %s vs %s" % (p1_char, p2_char)
                            if self.app.mode.lower() == 'public lobby':
                                presence.broadcast_game(mode, self.stats["p1char"], p1_char, self.stats["p2char"], p2_char, lobby_id=self.app.LobbyScreen.code)
                            else:
                                presence.broadcast_game(mode, self.stats["p1char"], p1_char, self.stats["p2char"], p2_char)
                        else:
                            if self.app.mode.lower() == 'public lobby':
                                if self.app.offline_mode != None:
                                    if self.app.offline_mode.lower() == 'training' or self.app.offline_mode.lower() == 'replay theater':
                                        presence.single_game(self.app.offline_mode, p1_char, self.stats["p1char"], self.stats["p1moon"],lobby_id=self.app.LobbyScreen.code)
                                    else:
                                        presence.offline_game(self.app.offline_mode, p1_char, self.stats["p1char"], p2_char, self.stats["p2char"],lobby_id=self.app.LobbyScreen.code)
                                else:
                                    if self.app.LobbyScreen.global_lobby is True:
                                        presence.global_lobby_game(self.app.LobbyScreen.opponent, char1_name=p1_char, char1_id=self.stats["p1char"], char2_name=p2_char, char2_id=self.stats["p2char"])     
                                    else:
                                        presence.public_lobby_game(self.app.LobbyScreen.code, self.app.LobbyScreen.opponent, char1_name=p1_char, char1_id=self.stats["p1char"], char2_name=p2_char, char2_id=self.stats["p2char"])     
                            else:
                                if self.app.offline_mode != None:
                                    if self.app.offline_mode.lower() == 'training' or self.app.offline_mode.lower() == 'replay theater':
                                        presence.single_game(self.app.offline_mode, p1_char, self.stats["p1char"], self.stats["p1moon"])
                                    else:
                                        presence.offline_game(self.app.offline_mode, p1_char, self.stats["p1char"], p2_char, self.stats["p2char"])
                                else:
                                    if self.app.mode.lower() == 'private lobby':
                                        presence.online_game(self.app.mode, self.app.LobbyScreen.opponent, char1_name=p1_char, char1_id=self.stats["p1char"], char2_name=p2_char, char2_id=self.stats["p2char"])
                                    else:
                                        if self.tproc == None:
                                            presence.online_game(self.app.mode, self.app.OnlineScreen.opponent, char1_name=p1_char, char1_id=self.stats["p1char"], char2_name=p2_char, char2_id=self.stats["p2char"])
                                        elif not self.tproc.isalive():
                                            presence.online_game(self.app.mode, self.app.OnlineScreen.opponent, char1_name=p1_char, char1_id=self.stats["p1char"], char2_name=p2_char, char2_id=self.stats["p2char"])
                        state = self.stats["state"]
                    # Check if in character select once
                    elif self.stats["state"] == 20 and self.stats["state"] != state:
                        if self.app.mode.lower() == 'public lobby':
                            presence.character_select(self.app.mode,lobby_id=self.app.LobbyScreen.code)
                        else:
                            presence.character_select(self.app.mode)
                        state = self.stats["state"]
                if app_config['settings']['write_scores'] == '1':
                    mode = self.app.offline_mode
                    if self.app.mode.lower() == 'direct match' or mode.lower() == 'spectating' or mode.lower() == 'tournament vs' or mode.lower() == 'local vs' or mode.lower() == 'replay theater':
                        try:
                            if self.stats["p1wins"] > p1wins and self.stats["p1wins"] == self.stats["towin"]:
                                increment_score_file(1)
                                p1_set_wins += 1
                            if self.stats["p2wins"] > p2wins and self.stats["p2wins"] == self.stats["towin"]:
                                increment_score_file(2)
                                p2_set_wins += 1
                            p1wins = self.stats["p1wins"]
                            p2wins = self.stats["p2wins"]
                        except TypeError:
                            pass
                #this is for set limit reaching, not implemented in UI yet
                if self.stats['state'] == 5 and wins != 0 and (p1_set_wins >= wins or p2_set_wins >= wins):
                    #menustate diff is <2 if replay save is on, <1 if off
                    #we also check if the replay folder item count has incremented just to be sure
                    if menu_value == None:
                        menu_value = self.stats['menucount']
                    else:
                        diff = self.stats['menucount'] - menu_value
                        if (diff >= 2 or diff >= -1) and caster_config['settings']['autoReplaySave'] == '1' and len(os.listdir(os.getcwd() + '\ReplayVS')) > replay_count:
                            #print("Set limit reached, auto replay save found. Killing in 3...")
                            time.sleep(3)
                            self.kill_caster()
                        elif (diff >= 1 or diff >= -1) and caster_config['settings']['autoReplaySave'] == '0':
                            #print("Set Limit reached, no auto replay save. Killing in 5...")
                            time.sleep(5)
                            self.kill_caster()
                    
                    #if caster_config['settings']['autoReplaySave'] == '1':
                    #    if len(os.listdir(os.getcwd() + '\ReplayVS')) > replay_count:
                    #        
                    #    else:
                    #        print("Set limit reached, auto replay save. Waiting...")
                    #else:
            if once:
                break
            else:
                time.sleep(0.5)

    def read_memory(self,addr):
        try:
            if self.find_pid():
                if k32.ReadProcessMemory(self.pid, addr, buf, STRLEN, ctypes.byref(s)):
                    return int.from_bytes(buf.raw, "big")
            else:
                return None
        except:
            logging.warning('READ MEMORY: %s' % sys.exc_info()[0])
            return None
        
    def kill_host_training(self):
        subprocess.run('taskkill /f /im MBAA.exe', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        #if self.tproc != None:
        #    del self.tproc
        self.tproc = None

    def kill_caster(self):
        self.adr = None
        self.rs = -1
        self.ds = -1
        killed = False
        if self.aproc != None:
            subprocess.run('taskkill /f /im %s' % app_config['settings']['caster_exe'].strip(), shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            killed = True
        self.aproc = None
        self.startup = False
        self.offline = False
        self.broadcasting = False
        self.playing = False
        self.pid = None
        if self.app.discord is True:
            if self.app.LobbyScreen.type != None:
                if self.app.LobbyScreen.type.lower() == 'public':
                    self.app.mode = 'Public Lobby'
                    if self.app.LobbyScreen.global_lobby is True:
                        presence.global_lobby()
                    else:
                        presence.public_lobby(self.app.LobbyScreen.code)
                elif self.app.LobbyScreen.type.lower() == 'private':
                    self.app.mode = 'Private Lobby'
                    presence.private_lobby()
            else:
                if killed:
                    self.app.mode = 'Menu'
                    presence.menu()

    def check_msg(self,s):
        e = []
        for i in error_strings:
            if i in s:
                if i == 'Latest version is' or i == 'Update?': #update prompt
                    e.append(localize("ERR_UPDATE_CCCASTER"))
                else:
                    e.append(i)
                logger.write('\n%s\n' % e)
        if e != []:
            self.kill_caster()
        return e

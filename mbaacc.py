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
    'Cannot find host',
    'Cannot initialize networking!',
    'Network error!',
    'already being used!',
    'Too many duplicate joysticks',
    'Failed to initialize controllers!',
    'Failed to check controllers!',
    'Port must be less than 65536!',
    'Invalid IP address and/or port!',
    'Failed to start game!',
    'Failed to communicate with',
    'Unhandled game mode!',
    'Host sent invalid configuration!',
    'Delay must be less than 255!',
    'Rollback must be less than',
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
]

ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?    ]*[ -\/]*[@-~]')
caster_button = re.compile(r'\[[0-9]\]')
player_name_host_mm = re.compile(r'')
player_name_join_mm = re.compile(r'\w* connected')

class loghelper():
    dateTimeObj = datetime.now()
    timestampStr = 'Concerto_' + \
        dateTimeObj.strftime("%d-%b-%Y-%H-%M-%S") + '.txt'

    def write(self, s):
        if not os.path.isdir(PATH + 'concerto-logs'):
            os.mkdir(PATH + 'concerto-logs')
        with open(PATH + 'concerto-logs\\' + self.timestampStr, 'a') as log:
            log.write(s)

logger = loghelper()

class Caster():

    def __init__(self, CApp):
        self.app = CApp
        self.adr = None #our IP when hosting, needed to trigger UI actions
        self.playing = False #True when netplay begins via input to CCCaster
        self.rs = -1 # Caster's suggested rollback frames. Sent to UI.
        self.ds = -1 # delay suggestion
        self.aproc = None # active caster Thread object to check for isalive()
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

    def matchmaking(self,sc):
        self.kill_caster()
        self.app.offline_mode = None
        dialog = sc.active_pop.modal_txt.text
        try:
            self.aproc = PtyProcess.spawn(app_config['settings']['caster_exe'].strip())
        except FileNotFoundError:
            sc.error_message(['%s not found.' % app_config['settings']['caster_exe'].strip()])
            return None
        while self.aproc.isalive():
            con = self.aproc.read()
            logger.write('\n%s\n' % con.split())
            if self.find_button(con.split(),'Server'):
                self.aproc.write('2')
                break
            else:
                if self.check_msg(con) != []:
                    sc.error_message(self.check_msg(con))
                    break
        # Stats
        threading.Thread(target=self.update_stats,daemon=True).start()
        cur_con = ""
        last_con = ""
        con = ""
        
        #Matchmaking cannot be launched headless, so we need to clean extra outputs (thankfully these seem to be predictable)
        junk = ["*", "0;", "19G", "\x1b[", "0;30;8m", "38m", "CCCaster 3.1", "[1] Lobby","[2] Matchmaking","[0] Cancel","[1] Netplay", "[2] Spectate", "[3] Broadcast", "[4] Offline", "[5] Server", "[6] Controls", "[7] Settings", "[8] Update", "[9] Results", "[0] Quit"]

        logger.write('\n== Matchmaking ==\n')
        while self.aproc != None and self.aproc.isalive():
            cur_con = ansi_escape.sub('', str(self.aproc.read()))
            for i in junk:
                cur_con = cur_con.replace(i,"")
            con += last_con + cur_con
            logger.write('\n=================================\n')
            logger.write(str(con.split()))
            if self.playing == False and self.rs == -1 and self.ds == -1:
                n = self.validate_read(con)
                if n != False:
                    logger.write('\n=================================\n')
                    logger.write(str(con.split()))
                    if int(n[-2]) - int(n[-1]) < 0:
                        self.ds = 0
                    else:
                        self.ds = int(n[-2]) - int(n[-1])
                    self.rs = int(n[-1])
                    opponent_name = ""
                    if "Connected to" in con:
                        r = re.findall('Connected to\s*([^\n\r]*)',con)
                    elif "connected" in con:
                        r = re.findall('([^\n\r]*) connected',con)
                    if r != []:
                        opponent_name = r[-1].strip()
                    #Regex for Ping
                    p = re.findall('Ping: \d+\.\d+ ms', con)
                    ping = p[-1].replace('Ping:','')
                    ping = ping.replace('ms','')
                    ping = ping.strip()
                    #Network Delay
                    delay = n[-2]
                    #Mode and rounds
                    m = ""
                    rd = 2
                    if "Versus" in con:
                        m = "Versus"
                        rd = n[-3]
                    elif "Training" in con:
                        m = "Training"
                        rd = 0
                    #Name
                    sc.set_frames(opponent_name,delay,ping,mode=m,rounds=rd) #trigger frame delay settings in UI
                    break
                else:
                    if self.check_msg(con) != []:
                        sc.error_message(self.check_msg(con))
                        break
                    elif last_con != cur_con:
                        last_con = cur_con
                    if "Hosting at server" in cur_con:
                        sc.active_pop.modal_txt.text = dialog + "\n(Hosting, waiting for connection...)"
                    if "Waiting for opponent" in cur_con:
                        sc.active_pop.modal_txt.text = dialog + "\n(Waiting for opponent...)"
                    if "Trying connection (UDP" in cur_con:
                        sc.active_pop.modal_txt.text = dialog + "\n(Trying connection (UDP Tunnel)...)"
                    if "Trying connection" in cur_con:
                        sc.active_pop.modal_txt.text = dialog + "\n(Trying connection...)"
            else:
                break

    def host(self, sc, port='0', mode="Versus",t=None): #sc is a Screen for UI triggers
        self.kill_caster()
        self.app.offline_mode = None
        try:
            if mode == "Training":
                self.aproc = PtyProcess.spawn('%s -n -t %s' % (app_config['settings']['caster_exe'].strip(),port))
            else:
                self.aproc = PtyProcess.spawn('%s -n %s' % (app_config['settings']['caster_exe'].strip(),port)) 
        except FileNotFoundError:
            sc.error_message(['%s not found.' % app_config['settings']['caster_exe'].strip()])
            return None
        # Stats
        threading.Thread(target=self.update_stats,daemon=True).start()
        logger.write('\n== Host ==\n')
        while self.aproc.isalive(): # find IP and port combo for host
            txt = self.aproc.read()
            ip = re.findall(
                r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{,5}', txt)
            if ip != []:
                self.adr = str(ip[0])
                sc.set_ip(self.adr) #tell UI we have the IP address
                break
            elif self.check_msg(txt) != []:
                sc.error_message(self.check_msg(txt))
                return None
        logger.write('IP: %s\n' % self.adr)
        cur_con = "" #current Caster read
        last_con = "" #last Caster read
        con = "" #cumulative string of all cur_con reads
        while self.aproc.isalive():
            cur_con = ansi_escape.sub('', str(self.aproc.read()))
            con += last_con + cur_con #con is what we send to validate_read
            logger.write('\n=================================\n')
            logger.write(str(con.split()))
            if self.playing == False and self.rs == -1 and self.ds == -1: #break self.playing is True
                n = self.validate_read(con)
                if n != False:
                    logger.write('\n=================================\n')
                    logger.write(str(con.split()))
                    if int(n[-2]) - int(n[-1]) < 0: # last item should be rollback frames, 2nd to last is network delay
                        self.ds = 0
                    else:
                        self.ds = int(n[-2]) - int(n[-1])
                    self.rs = int(n[-1])
                    r = []
                    name = False  # try to read names from caster output
                    for x in reversed(con.split()):
                        if name == False and (x == "connected" or x == "conected"):
                            name = True
                        elif name == True and x == '*':
                            break
                        elif name == True and x.replace('*', '') != '':
                            r.insert(0, x)
                    #Regex for Ping
                    p = re.findall('Ping: \d+\.\d+ ms', con)
                    ping = p[-1].replace('Ping:','')
                    ping = ping.replace('ms','')
                    ping = ping.strip()
                    #Network Delay
                    delay = n[-2]
                    #Mode and rounds
                    m = ""
                    rd = 2
                    if "Versus" in con:
                        m = "Versus"
                        rd = n[-3]
                    elif "Training" in con:
                        m = "Training"
                        rd = 0
                    #Name
                    opponent_name = ' '.join(r)
                    sc.set_frames(opponent_name,delay,ping,mode=m,rounds=rd,target=t) #trigger frame delay settings in UI
                    break
                else:
                    if self.check_msg(con) != []:
                        sc.error_message(self.check_msg(con))
                        self.aproc = None
                        break
                    elif last_con != cur_con:
                        last_con = cur_con
                        continue
            else:
                break

    def join(self, ip, sc, t=None, *args): #t is required by the Lobby screen to send an "accept" request later
        self.kill_caster()
        self.app.offline_mode = None
        try:
            self.aproc = PtyProcess.spawn('%s -n %s' % (app_config['settings']['caster_exe'].strip(),ip)) 
        except FileNotFoundError:
            sc.error_message(['%s not found.' % app_config['settings']['caster_exe'].strip()])
            return None
        # Stats
        threading.Thread(target=self.update_stats,daemon=True).start()
        cur_con = ""
        last_con = ""
        con = ""
        logger.write('\n== Join %s ==\n' % ip)
        while self.aproc.isalive():
            cur_con = ansi_escape.sub('', str(self.aproc.read()))
            con += last_con + cur_con
            logger.write('\n=================================\n')
            logger.write(str(con.split()))
            if self.playing == False and self.rs == -1 and self.ds == -1:
                n = self.validate_read(con)
                if n != False:
                    logger.write('\n=================================\n')
                    logger.write(str(con.split()))
                    if int(n[-2]) - int(n[-1]) < 0:
                        self.ds = 0
                    else:
                        self.ds = int(n[-2]) - int(n[-1])
                    self.rs = int(n[-1])
                    r = []
                    name = False 
                    for x in con.split():
                        if x == "to" and name == False:
                            name= True
                        elif x == '*' and name == True:
                            break
                        elif name == True and x.replace('*', '') != '':
                            r.append(x)
                    #Regex for Ping
                    p = re.findall('Ping: \d+\.\d+ ms', con)
                    ping = p[-1].replace('Ping:','')
                    ping = ping.replace('ms','')
                    ping = ping.strip()
                    #Network Delay
                    delay = n[-2]
                    #Mode and rounds
                    m = ""
                    rd = 2
                    if "Versus" in con:
                        m = "Versus"
                        rd = n[-3]
                    elif "Training" in con:
                        m = "Training"
                        rd = 0
                    #Name
                    opponent_name = ' '.join(r)
                    sc.set_frames(opponent_name,delay,ping,mode=m,rounds=rd,target=t) #trigger frame delay settings in UI
                    break
                else:
                    if self.check_msg(con) != []:
                        sc.error_message(self.check_msg(con))
                        break
                    elif 'Spectating versus mode' in con:
                        sc.error_message(['Host is already in a game!'])
                        break
                    elif last_con != cur_con:
                        last_con = cur_con
                        continue
            else:
                break

    def confirm_frames(self,rf,df):
        if self.aproc:
            self.aproc.write('\x08')
            self.aproc.write('\x08')
            self.aproc.write(str(rf))
            self.aproc.write('\x0D')
            time.sleep(0.1)
            self.aproc.write('\x08')
            self.aproc.write('\x08')
            self.aproc.write(str(df))
            self.aproc.write('\x0D')
            self.playing = True

    def watch(self, ip, sc, *args):
        self.kill_caster()
        try:
            self.aproc = PtyProcess.spawn('%s -n -s %s' % (app_config['settings']['caster_exe'].strip(),ip))
        except FileNotFoundError:
            sc.error_message(['%s not found.' % app_config['settings']['caster_exe'].strip()])
            return None
        cur_con = ""
        last_con = ""
        con = ""
        logger.write('\n== Watch %s ==\n' % ip)
        self.broadcasting = True
        threading.Thread(target=self.update_stats,daemon=True).start()
        while self.aproc.isalive():
            cur_con = ansi_escape.sub('', str(self.aproc.read()))
            con += last_con + cur_con
            logger.write('\n=================================\n')
            logger.write(str(con.split()))
            if "fast-forward)" in con:
                logger.write('\n=================================\n')
                logger.write(str(con.split()))
                self.aproc.write('1')  # start spectating, find names after
                r = []
                startWrite = False
                for x in reversed(con.split()):
                    if startWrite is False and "fast-forward" not in x:
                        pass
                    elif "fast-forward)" in x:
                        startWrite = True
                        r.insert(0, x)
                    elif x == '*' and len(r) > 0:
                        if r[0] == "Spectating":
                            break
                    elif x != '*' and x.replace('*', '') != '':
                        r.insert(0, x)
                sc.active_pop.modal_txt.text = ' '.join(r)
                # replace connecting text with match name in caster
                break
            else:
                if self.check_msg(con) != []:
                    sc.error_message(self.check_msg(con))
                    break
                elif last_con != cur_con:
                    last_con = cur_con
                    continue

    def broadcast(self, sc, port='0', mode="Versus"): #sc is a Screen for UI triggers
        self.kill_caster()
        try:
            if mode == "Training":
                self.aproc = PtyProcess.spawn('%s -n -b -t %s' % (app_config['settings']['caster_exe'].strip(),port)) 
            else:
                self.aproc = PtyProcess.spawn('%s -n -b %s' % (app_config['settings']['caster_exe'].strip(),port))
        except FileNotFoundError:
            sc.error_message(['%s not found.' % app_config['settings']['caster_exe'].strip()])
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
            sc.error_message(['%s not found.' % app_config['settings']['caster_exe'].strip()])
            return None
        self.aproc = proc
        logger.write('\n== Training ==\n')
        while self.aproc.isalive():
            con = self.aproc.read()
            logger.write('\n%s\n' % con.split())
            if self.find_button(con.split(),'Offline') or self.find_button(con.split(),'Ofline'):
                self.aproc.write('1')
                self.flag_offline(sc)
                break
            else:
                if self.check_msg(con) != []:
                    sc.error_message(self.check_msg(con))
                    break

    def local(self,sc):
        self.kill_caster()
        self.startup = True
        try:
            proc = PtyProcess.spawn(app_config['settings']['caster_exe'].strip())
        except FileNotFoundError:
            sc.error_message(['%s not found.' % app_config['settings']['caster_exe'].strip()])
            return None
        self.aproc = proc
        while self.aproc.isalive():
            con = self.aproc.read()
            if self.find_button(con.split(),'Offline') or self.find_button(con.split(),'Ofline'):
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
            sc.error_message(['%s not found.' % app_config['settings']['caster_exe'].strip()])
            return None
        self.aproc = proc
        while self.aproc.isalive():
            con = self.aproc.read()
            if self.find_button(con.split(),'Offline') or self.find_button(con.split(),'Ofline'):
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
            sc.error_message(['%s not found.' % app_config['settings']['caster_exe'].strip()])
            return None
        self.aproc = proc
        while self.aproc.isalive():
            con = self.aproc.read()
            if self.find_button(con.split(),'Offline') or self.find_button(con.split(),'Ofline'):
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
        try:
            proc = PtyProcess.spawn(app_config['settings']['caster_exe'].strip())
        except FileNotFoundError:
            sc.error_message(['%s not found.' % app_config['settings']['caster_exe'].strip()])
            return None
        self.aproc = proc
        while self.aproc.isalive():
            con = self.aproc.read()
            if self.find_button(con.split(),'Offline') or self.find_button(con.split(),'Ofline'):
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
        try:
            proc = PtyProcess.spawn(app_config['settings']['caster_exe'].strip())
        except FileNotFoundError:
            sc.error_message(['%s not found.' % app_config['settings']['caster_exe'].strip()])
            return None
        self.aproc = proc
        while self.aproc.isalive():
            con = self.aproc.read()
            if self.find_button(con.split(),'Offline') or self.find_button(con.split(),'Ofline'):
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
            sc.error_message(['MBAA.exe not found.'])
            return None

    def find_button(self,read,term):
        current_btn = None
        if term in read:
            for i in read:
                if i == term and current_btn != None:
                    self.aproc.write(current_btn)
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
        sc.active_pop.dismiss()

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
    
    def update_stats(self,once=False):
        # Used to update presence only on state change 
        state = None
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
                    "towin": self.read_memory(0x553FDC)
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
                                        presence.online_game(self.app.mode, self.app.OnlineScreen.opponent, char1_name=p1_char, char1_id=self.stats["p1char"], char2_name=p2_char, char2_id=self.stats["p2char"])
                        state = self.stats["state"]
                    # Check if in character select once
                    elif self.stats["state"] == 20 and self.stats["state"] != state:
                        if self.app.mode.lower() == 'public lobby':
                            presence.character_select(self.app.mode,lobby_id=self.app.LobbyScreen.code)
                        else:
                            presence.character_select(self.app.mode)
                        state = self.stats["state"]
            if once:
                break
            else:
                time.sleep(2)

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

    def kill_caster(self):
        self.adr = None
        self.rs = -1
        self.ds = -1
        if self.aproc != None:
            subprocess.run('taskkill /f /im %s' % app_config['settings']['caster_exe'].strip(), shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
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
                    presence.public_lobby(self.app.LobbyScreen.code)
                elif self.app.LobbyScreen.type.lower() == 'private':
                    self.app.mode = 'Private Lobby'
                    presence.private_lobby()
            else:
                self.app.mode = 'Menu'
                presence.menu()

    def check_msg(self,s):
        e = []
        for i in error_strings:
            if i in s:
                if i == 'Latest version is' or i == 'Update?': #update prompt
                    e.append("A new version of CCCaster is available. Please update by opening CCCaster.exe manually or downloading manually from concerto.shib.live.")
                else:
                    e.append(i)
                logger.write('\n%s\n' % e)
        if e != []:
            self.kill_caster()
        return e

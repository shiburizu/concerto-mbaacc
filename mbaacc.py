from logging import error
from winpty import PtyProcess  # pywinpty
from datetime import datetime
import re
import time
import subprocess
CREATE_NO_WINDOW = 0x08000000 #subprocess flag

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
    'Couldn\'t find MBAA.exe!',
    'Timed out!',
    'Network delay greater than limit:'
]

ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')


class loghelper():
    dateTimeObj = datetime.now()
    timestampStr = 'Concerto_' + \
        dateTimeObj.strftime("%d-%b-%Y-%H-%M-%S") + '.txt'

    def write(self, s):
        with open(self.timestampStr, 'a') as log:
            log.write(s)


logger = loghelper()


class Caster():

    def __init__(self, CApp):
        self.app = CApp
        self.adr = None #our IP when hosting, needed to trigger UI actions
        self.playing = False #True when netplay begins via input to CCCaster
        self.rf = -1 # user's choice of rollback frames. Provided by UI to Caster
        self.df = -1 # delay choice
        self.rs = -1 # Caster's suggested rollback frames. Sent to UI.
        self.ds = -1 # delay suggestion
        self.aproc = None # active caster Thread object to check for isalive()
        self.offline = False #True when an offline mode has been started
        self.startup = False #True when waiting for MBAA.exe to start in offline

    def validate_read(self, con):
        if "rollback:" in con:
            conlst = con.split() # split string into list
            r = 0 #count all items before "rollback:" in list
            for i in reversed(conlst):
                if i != 'rollback:':
                    r += 1
                elif i == 'rollback:':
                    break
            if r > 0: #if the list of items after "rollback:" > 0...
                rlst = re.sub("[^0-9]", "", ''.join(conlst[-r:])) # ...find all numbers in the list
                if len(rlst) > 0:  # ...if there's at least one number, proceed (rollback suggested frames)
                    p = re.findall('\d+\.\d+', con) #find the ping number and delete it so it doesnt false positive
                    for i in p:
                        if i in conlst:
                            conlst.remove(i)
                    n = [i for i in re.findall(
                        '[0-9]+', ' '.join(conlst)) if int(i) < 15] #now find all whole numbers
                    if len(n) >= 2: #at least 2 numbers need to be in our filtered list
                        logger.write('\nrblst: %s\n' % rlst) #logger stuff
                        logger.write('\nn: %s\n' % n)
                        logger.write('\nVALID READ:\n%s\n' % con.split())
                        return n #return list
        return False

    def host(self, sc): #sc is a Screen for UI triggers
        self.kill_existing()
        self.aproc = PtyProcess.spawn('cccaster.v3.0.exe -n 0')
        logger.write('\n== Host ==\n')
        while self.aproc.isalive(): # find IP and port combo for host
            t = self.aproc.read()
            print(t.split())
            ip = re.findall(
                r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{,5}', t)
            if ip != []:
                self.adr = str(ip[0])
                break
            elif self.check_msg(t) != []:
                sc.error_message(self.check_msg(t))
                self.kill_caster()
                self.aproc = None
                return None
        print('continue')
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
                        if name == False and x == "connected":
                            name = True
                        elif name == True and x == '*':
                            break
                        elif name == True and x.replace('*', '') != '':
                            r.insert(0, x)
                    # find all floats in caster output and use the last one [-1] to make sure we get caster text
                    p = re.findall('\d+\.\d+', con)
                    sc.set_frames(' '.join(r), n[-2], p[-1]) #trigger frame delay settings in UI
                    while True:  # todo optimize set_frames stutter by making this a thread
                        if self.rf != -1 and self.df != -1:
                            # two backspace keys for edge case of >9 frames
                            self.aproc.write('\x08')
                            self.aproc.write('\x08')
                            self.aproc.write(str(self.rf))
                            self.aproc.write('\x0D')
                            # slight delay to let caster refresh screen
                            time.sleep(0.1)
                            self.aproc.write('\x08')
                            self.aproc.write('\x08')
                            self.aproc.write(str(self.df))
                            self.aproc.write('\x0D')
                            self.playing = True  # set netplaying to avoid more reads
                            break
                    break
                else:
                    if self.check_msg(con) != []:
                        sc.error_message(self.check_msg(con))
                        self.kill_caster()
                        self.aproc = None
                        break
                    elif last_con != cur_con:
                        last_con = cur_con
                        continue
            else:
                break

    def join(self, ip, sc, t=None, *args): #t is required by the Lobby screen to send an "accept" request later
        self.kill_existing()
        self.aproc = PtyProcess.spawn('cccaster.v3.0.exe -n %s' % ip)
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
                    p = re.findall('\d+\.\d+', con)
                    sc.set_frames(' '.join(r), n[-2], p[-1], t) #send t for Accept network request
                    while True: 
                        if self.rf != -1 and self.df != -1:
                            self.aproc.write('\x08')
                            self.aproc.write('\x08')
                            self.aproc.write(str(self.rf))
                            self.aproc.write('\x0D')
                            time.sleep(0.1)
                            self.aproc.write('\x08')
                            self.aproc.write('\x08')
                            self.aproc.write(str(self.df))
                            self.aproc.write('\x0D')
                            self.playing = True
                            break
                    break
                else:
                    if self.check_msg(con) != []:
                        sc.error_message(self.check_msg(con))
                        self.kill_caster()
                        self.aproc = None
                        break
                    elif 'Spectating versus mode' in con:
                        sc.error_message(['Host is already in a game!'])
                        self.kill_caster()
                        self.aproc = None
                        break
                    elif last_con != cur_con:
                        last_con = cur_con
                        continue
            else:
                break

    def watch(self, ip, sc, *args): #modal is kivy label to update
        self.kill_existing()
        self.aproc = PtyProcess.spawn('cccaster.v3.0.exe -n -s %s' % ip)
        cur_con = ""
        last_con = ""
        con = ""
        logger.write('\n== Watch %s ==\n' % ip)
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
                    self.kill_caster()
                    self.aproc = None
                    break
                elif last_con != cur_con:
                    last_con = cur_con
                    continue

    def training(self,sc):
        self.kill_existing()
        self.startup = True
        proc = PtyProcess.spawn('cccaster.v3.0.exe')
        self.aproc = proc
        logger.write('\n== Training ==\n')
        while self.aproc.isalive():
            con = self.aproc.read()
            logger.write('\n%s\n' % con.split())
            if "Offline" in con:
                self.aproc.write('4')  # 4 is offline
                time.sleep(0.1)
                self.aproc.write('1')
                self.flag_offline()
                break
            else:
                if self.check_msg(con) != []:
                    sc.error_message(self.check_msg(con))
                    self.startup = False
                    self.kill_caster()
                    self.aproc = None
                    break

    def local(self,sc):
        self.kill_existing()
        self.startup = True
        proc = PtyProcess.spawn('cccaster.v3.0.exe')
        self.aproc = proc
        while self.aproc.isalive():
            con = self.aproc.read()
            if "Offline" in con:
                self.aproc.write('4')
                time.sleep(0.1)
                self.aproc.write('2')
                self.flag_offline()
                break
            else:
                if self.check_msg(con) != []:
                    sc.error_message(self.check_msg(con))
                    self.startup = False
                    self.kill_caster()
                    self.aproc = None
                    break

    def tournament(self,sc):
        self.kill_existing()
        self.startup = True
        proc = PtyProcess.spawn('cccaster.v3.0.exe')
        self.aproc = proc
        while self.aproc.isalive():
            con = self.aproc.read()
            if "Offline" in con:
                self.aproc.write('4')
                time.sleep(0.1)
                self.aproc.write('4')
                self.flag_offline()
                break
            else:
                if self.check_msg(con) != []:
                    sc.error_message(self.check_msg(con))
                    self.startup = False
                    self.kill_caster()
                    self.aproc = None
                    break

    def replays(self,sc):
        self.kill_existing()
        self.startup = True
        proc = PtyProcess.spawn('cccaster.v3.0.exe')
        self.aproc = proc
        while self.aproc.isalive():
            con = self.aproc.read()
            if "Offline" in con:
                self.aproc.write('4')
                time.sleep(0.1)
                self.aproc.write('5')
                self.flag_offline()
                break
            else:
                if self.check_msg(con) != []:
                    sc.error_message(self.check_msg(con))
                    self.startup = False
                    self.kill_caster()
                    self.aproc = None
                    break

    def flag_offline(self):
        while True:
            w = subprocess.run('qprocess mbaa.exe', stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, creationflags=CREATE_NO_WINDOW)
            #q = [p.info['name'] for p in psutil.process_iter(['name'])]
            if b'No Process exists for mbaa.exe\r\n' not in w.stderr and self.offline is False:
                self.startup = False
                self.offline = True
                break

            if self.aproc != None:
                if self.aproc.isalive() is False:
                    break
            else:
                break

    def kill_existing(self):
        if self.aproc != None:
            self.kill_caster()
            self.aproc = None
            self.offline = False
            self.startup = False
        
    def kill_caster(self):
        subprocess.run('taskkill /f /im cccaster.v3.0.exe', creationflags=CREATE_NO_WINDOW)

    def check_msg(self,s):
        e = []
        for i in error_strings:
            if i in s:
                e.append(i)
                logger.write('\n%s\n' % e)
        return e
        
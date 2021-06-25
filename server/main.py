from flask import Flask, request
import random,time,os
app = Flask(__name__)

lobby_list = {}

def gen_resp(msg,status):
    resp = {
        'status' : status,
        'msg' : msg
    }
    return resp

class Player():

    def __init__(self,new_name,new_id):
        self.id = new_id
        self.name = new_name
        self.last_ping = time.monotonic()
        self.status = "idle"
        self.ip = None
        self.target = None

class Lobby():

    def __init__(self,new_id,new_player,type):
        self.secret = random.randint(1000,9999) #secret required for lobby actions
        self.player_list = {}
        self.id = new_id
        self.host = new_player
        self.player_list.update({1:Player(new_player,1)})
        if type:
            self.type = type
        else:
            self.type = 'Private'
    
    def join(self,new_player):
        n = 1
        while True:
            if n in self.player_list:
                n += 1
            else:
                break
        self.player_list.update({n:Player(new_player,n)})
        return n

    def response(self,player_id,msg='OK'):
        if player_id in self.player_list:
            self.player_list.get(player_id).last_ping = time.monotonic()
            resp = {
                'id' : self.id,
                'status' : 'OK',
                'msg'    : msg,
                'idle'   : self.idle(),
                'playing': self.playing(),
                'challenges': self.challenges(player_id)
            }
            print(resp)
            self.prune_members()
            return resp
        else:
            resp = {
                'id' : self.id,
                'status' : 'OK',
                'msg'    : msg,
                'users'  : [[i.name,i.id,i.status,i.target,i.ip,i.last_ping] for i in self.player_list.values()]
            }
            print(resp)
            self.prune_members()
            return resp
    
    def idle(self): #iterate over items to get player info as a list
        return [[i.name,i.id] for i in self.player_list.values() if i.status == "idle"]
    
    def playing(self):
        found_ids = []
        resp = []
        for i in self.player_list.values():
            if i.status == "playing" and i.id not in found_ids and i.target not in found_ids and i.ip is not None:
                resp.append([i.name,self.find_name_by_id(i.target),i.id,i.target,i.ip])
                found_ids.append(i.id)
                found_ids.append(i.target)
        return resp

    def challenges(self,player_id):
        resp = []
        for i in self.player_list.values():
            if i.target == player_id and i.status != 'playing':
                resp.append([i.name,i.id,i.ip])
        return resp

    def find_name_by_id(self,id):
        if id in self.player_list:
            return self.player_list.get(id).name
        else:
            return None
    
    def prune_members(self):
        now = time.monotonic() 
        d = []
        for k,v in self.player_list.items():
            diff = now - v.last_ping
            if diff > 6:
                d.append(k)
        for i in d:
            self.player_list.pop(i)
            print("Pruned %s" % i)
    
    def send_challenge(self,id,target,ip):
        p = self.player_list.get(id)
        p.target = target
        p.ip = ip
        return gen_resp('OK','OK')

    def accept_challenge(self,id,target):
        p1 = self.player_list.get(target)
        p2 = self.player_list.get(id)
        p1.status = "playing"
        p2.status = "playing"
        p2.target = target #so we know who they are playing in lobby state
        return gen_resp('OK','OK')

    def end(self,id): #reset both players on a single end, since it represents a disconnect anyway. None for spectator
        p2 = self.player_list.get(id)

        if p2.target:
            if p2.target in self.player_list:
                p1 = self.player_list.get(p2.target)
                p1.status = "idle"
                p1.target = None
                p1.ip = None
        
        p2.status = "idle"
        p2.target = None
        p2.ip = None
            
        return gen_resp('OK','OK')

    def leave(self,id):
        if id in self.player_list:
            if self.player_list.get(id).target != None:
                if self.player_list.get(id).target in self.player_list:
                    t = self.player_list.get(id).target
                    self.player_list.get(t).status = "idle"
                    self.player_list.get(t).target = None
                    self.player_list.get(t).ip = None
            self.player_list.pop(id)
        self.prune_members()
        return gen_resp('OK','OK')

CURRENT_VERSION = '6-22-2021'

@app.route('/v')
def version_check():
    if request.args.get('action') == 'check':
        if request.args.get('version') == CURRENT_VERSION:
            return gen_resp('OK','OK')
        else:
            return gen_resp('A newer version is available. Visit concerto.shib.live to update.','FAIL')

@app.route('/l') #lobby functions
def lobby_server():
    action = request.args.get('action')
    lobby_id = request.args.get('id')
    player_name = request.args.get('name')
    player_id = request.args.get('p')
    target_id = request.args.get('t')
    player_ip = request.args.get('ip')
    secret = request.args.get('secret')
    type = request.args.get('type')
    #lobby create/list, ID is not needed from client and lobbyExists not needed
    if action == "create": #create lobby, provide name
        if player_name:
            new_id = random.randint(1000,9999)
            while True:
                if new_id in lobby_list:
                    new_id = random.randint(1000,9999)
                else:
                    break
            new_room = Lobby(new_id,player_name,type)
            lobby_list[new_id] = new_room
            r = new_room.response(1,msg=1)
            r['secret'] = new_room.secret
            return r
        else:
            return gen_resp('Create action failed','FAIL')
    elif action == "list": #get all public lobbies
        clean = []
        lobbies = []
        for k,v in lobby_list.items():
            v.prune_members()
            if len(v.player_list) > 0:
                if v.type == 'Public':
                    lobbies.append([k,len(v.player_list)])
                else:
                    pass
            else:
                clean.append(k)
        for i in clean: #cleanup empty servers
            lobby_list.pop(i)
        resp = {
            'msg':'OK',
            'status':'OK',
            'lobbies': [[k,len(v.player_list)] for k,v in lobby_list.items() if len(v.player_list) > 0 and v.type == 'Public']
        }
        print(resp['lobbies'])
        return resp
    if action == "join" and lobby_id is not None:
        if player_name is not None and int(lobby_id) in lobby_list:
            p = lobby_list[int(lobby_id)].join(player_name) 
            r = lobby_list[int(lobby_id)].response(p,msg=p)
            r['secret'] = lobby_list[int(lobby_id)].secret
            return  r
        return gen_resp('Join action failed','FAIL')
    #lobby functions, ID is needed from client
    if lobby_id is not None and secret is not None:
        if int(lobby_id) in lobby_list and lobby_list[int(lobby_id)].secret == int(secret):
            #lobby exists and secret is correct, read
            if action == "challenge": #send challenge, set IP from host and target to ID
                return lobby_list[int(lobby_id)].send_challenge(int(player_id),int(target_id),player_ip)
            elif action == "accept": #accept challenge, tell server to update players to "playing"
                return lobby_list[int(lobby_id)].accept_challenge(int(player_id),int(target_id))
            elif action == "end": #game or spectate ended for player
                return lobby_list[int(lobby_id)].end(int(player_id))
            elif action == "leave": #leave lobby
                return lobby_list[int(lobby_id)].leave(int(player_id))
            elif action == "status": #get update on the lobby
                return lobby_list[int(lobby_id)].response(int(player_id))
            return gen_resp('lobby_id Action failed','FAIL')
        else:
            print(lobby_id)
            print(action)
            return gen_resp('No Lobby found','FAIL')
    #no action at all
    return gen_resp('No action match','FAIL')

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port, debug=False)
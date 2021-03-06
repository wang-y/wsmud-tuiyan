#edit by knva
#tool VSCODE
#time 2018-8-2 10:12:27
import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import time
import json
import re
from websocket import create_connection
class wsgamePlayer:
    userlist = []
    roles=[]
    static = True
    def __init__(self, serverip, acctoken):
        self.serverip = serverip
        self.acctoken=acctoken

    def convet_json(self,json_str):
        json_obj = eval(json_str, type('Dummy', (dict,), dict(__getitem__=lambda s,n:n))())
        return json_obj


    def start(self):
        ws = create_connection(self.serverip)
        print("Sending Login Token")
        ws.send(self.acctoken)
        print("Sent")
        print("Receiving...")
        result = ws.recv()
        pobj = self.convet_json(result)
        if(pobj['type']=='roles'):
            self.roles=pobj['roles']
            for item in pobj['roles']:
                self.userlist.append(item['id'])
            self.static=False
        ws.close()
    def getList(self):
        return self.userlist
    def getRoles(self):
            return self.roles
    def getStatic(self):
        return self.static
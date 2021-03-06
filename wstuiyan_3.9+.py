# edit by knva
# tool VSCODE
# time 2018-8-2 10:12:27
import threading
import websocket

from wsgameLogin import  GetLoginInfo
from wsgamePlayer import wsgamePlayer
try:
    import thread
except ImportError:
    import _thread as thread
import time
import json
import re

class wsinfer:
    serverip = ''
    acctoken = ''
    player = ''
    myname = ''
    book = ''
    bookid = ''
    position = ''
    attributes = []
    continuation = True
    total = 0
    step = 0
    curTotal = 0
    overFlag = False
    curAttrCount=0
    haveBingxin=False
    feiyiId=""
    bingxinId=""
    curFeiyiStatus=False
    curBingxinStatus=False
    addr = {"住房-练功房": "jh fam 0 start;go west;go west;go north;go enter;go west"}
    attrs_re= {
        "冷却百分比": r'绝招冷却时间：-(.+)%',
        "冷却时间": r'绝招冷却时间：-(.+)秒',
        "破防": r'忽视对方防御：\+(.+)%',
        "终伤": r'最终伤害：\+(.+)%',
        "臂力": r'臂力：\+(\d+)',
        "暴击": r'暴击：\+(.+)%',
        "暴击伤害": r'暴击伤害：\+(.+)%',
        "命中": r'命中：\+(\d+)',
        "命中百分比": r'命中：\+(.+)%',
        "攻击": r'攻击：\+(\d+)',
        "攻击百分比": r'攻击：\+(.+)%',
        "剑心": r'当你命中敌人后\(攻击频率\)会额外攻击敌人(.+)次\(剑心\)',
        "不灭": r'当你的气血降低到(.+)%时候会恢复(.+)%气血，并短时间无视伤害，冷却(.+)分钟\(混沌\)',
        "战神": r'每次攻击附加你最大内力(.+)%的伤害，当你空手时附加的内力加倍，并吸收(.+)%伤害',
        "移花": r'招架成功后顺势反击敌人，对敌人造成(.+)%伤害\(移花\)',
    }
    def __init__(self, userInfo):
        self.serverip = userInfo["serverip"]
        self.acctoken = userInfo["acctoken"]
        self.player = userInfo["player"]
        self.book = userInfo["book"]
        self.position = userInfo["position"]
        self.attributes = userInfo["attributes"]
        self.continuation = userInfo["continuation"]
        self.total = userInfo["total"]
        self.step = userInfo["step"]
        self.feiyiId=userInfo["feiyiId"]
        self.haveBingxin=userInfo["haveBingxin"]

    def sendcmd(self, cmd):
        cmd = cmd.split(";")
        for i in cmd:
            if '$' in i:
                i.replace('$', '')
                parg = i.split(" ")[1]
                if 'wait' in i:
                    time.sleep(int(parg) / 1000)
            else:
                self.ws.send(i)

    def convet_json(self, json_str):
        json_obj = eval(json_str, type('Dummy', (dict,), dict(__getitem__=lambda s, n: n))())
        return json_obj

    def logCat(self, msg):
        print("{0}: {1}: {2}".format(time.strftime('%H:%M:%S',time.localtime(time.time())), self.myname, msg))

    def go(self, addr):
        if self.addr[addr] is not None:
            self.sendcmd( self.addr[addr])

    def login(self):
        self.logCat(self.acctoken)
        self.sendcmd(self.acctoken)
        self.sendcmd("login " + self.player)
        time.sleep(1)
        self.sendcmd("tm 推演;")
        time.sleep(1)
        self.sendcmd('pack')
        time.sleep(1)
        if self.myname == '':
            self.logCat("登录失败,重新登录")
            time.sleep(5)
            self.login()
        else:
            self.logCat("登录成功,开始推演...")
            self.sendcmd('stopstate')
            if self.feiyiId:
                time.sleep(1)
                self.sendcmd('use ' + self.feiyiId)
            if self.haveBingxin:
                time.sleep(1)
                self.sendcmd('use '+ self.bingxinId)
            time.sleep(1)
            self.sendcmd('zc typelv {0}'.format(self.position))

    def getmyname(self, e):
        if e['ch'] == 'tm' and e['uid'] == self.player:
            self.myname = e['name']

    def getbookid(self, items):
        for item in items:
            if self.book in item['name']:
                self.bookid=item['id']
                break

    def getBingxinId(self, items):
        for item in items:
            if "冰心丹" in item['name']:
                self.bingxinId=item['id']
                break

    def infer(self):
        self.curTotal=self.curTotal+1
        self.logCat("当前跳数为 {0}， 还剩下 {1} 跳".format(str(self.curTotal),str(self.total-self.curTotal)))
        if self.total-self.curTotal == 0:
            self.sendcmd("stopstate")
            self.overFlag = True
        elif self.continuation == False:
            if self.curTotal%self.step == 0:
                self.logCat("中断推演，然后继续推演")
                self.sendcmd("stopstate")

    def stopOrContinue(self):
        if self.overFlag == True and (self.curAttrCount == 1 or self.curAttrCount == 0):
            time.sleep(1)
            self.logCat("推演结束，修炼")
            self.sendcmd("xiulian")
            time.sleep(1)
            self.ws.close()
        else:
            if self.feiyiId and self.curFeiyiStatus == False:
                time.sleep(1)
                self.sendcmd('use ' + self.feiyiId) 
            self.logCat("推演未结束，继续")
            self.sendcmd('zc typelv {0}'.format(self.position))

    def dealAttributes(self,msg):
        m=re.search(r'(你本次提升获得\d*个新的.*属性)',msg)
        if m:
            m1=re.search(r'(\d{1,})',m.group(0))
            self.curAttrCount=int(m1.group(0))
        else:
            m=re.search(r'(你还有\d*个新的.*属性可使用)',msg)
            m1=re.search(r'(\d{1,})',m.group(0))
            self.curAttrCount=int(m1.group(0))
        self.logCat("还剩下 {0} 个属性可选".format(str(self.curAttrCount)))
        # 添加或放弃属性
        banFlag=True
        x=re.search(r'<cyn>(.*)</cyn>', msg)
        if x:
            for i in self.attributes:
                if re.search(self.attrs_re[i],x.group(0)):
                    self.logCat("ADD {0}".format(x.group(0)))
                    self.sendcmd('zc prop {0} add'.format(self.position))
                    banFlag=False
                    break
            if banFlag:
                self.logCat("BAN {0}".format(x.group(0)))
                self.sendcmd('zc prop {0} ban'.format(self.position))
        self.stopOrContinue()

    # {type:"status","action":"add",id:"t3tl4ef988e",sid:"food","name":"玄灵丹","duration":300000}
    # {type:"status","action":"remove",id:"t3tl4ef988e",sid:"food"}
    def on_message(self,ws, message):
        if "{" and "}" in message:
            e = self.convet_json(message)
            if e['type'] == "msg":
                self.getmyname(e)
            if e['type'] == "status":
                if e['action'] == "add":
                    if e['sid'] == "food":
                        self.curBingxinStatus=True
                    elif e['sid']=="fy":
                        self.logCat("激活飞翼")
                        self.curFeiyiStatus=True
                elif e['action'] == "remove":
                    if e['sid'] == "food":
                        self.curBingxinStatus=False
                    elif e['sid']=="fy":
                        self.logCat("飞翼结束")
                        self.curFeiyiStatus=False
            if e['type'] =="dialog":
                if e['dialog'] == "pack":
                    self.getbookid(e['items'])
                    if self.haveBingxin:
                        self.getBingxinId(e['items'])
        else:
            if self.book in message and "有了更深入的理解" in message:
                self.infer()
            elif "没有实质提升(本次消耗会累计到下次使用)" in message:
                self.stopOrContinue()
            elif "本次提升获得" in message:
                self.dealAttributes(message)
            elif "属性可使用" in message:
                self.dealAttributes(message)
            elif "你还有未使用的" in message:
                self.dealAttributes(message)
            elif "属性获得提升" in message:
                self.stopOrContinue()



    def on_error(self,ws, error):
        self.logCat(error)

    def on_close(self,ws):
        self.logCat("### 断开连接 ###")

    def on_open(self,ws):
        def run(*args):
            time.sleep(1)
            self.login()
        thread.start_new_thread(run, ())

    def start(self):
        websocket.enableTrace(False)
        self.ws = websocket.WebSocketApp(self.serverip,
                              on_open = self.on_open,
                              on_message = self.on_message,
                              on_error = self.on_error,
                              on_close = self.on_close)
        self.ws.run_forever()
# <cyn>当你的气血降低到10%时候会恢复10%气血，并短时间无视伤害，冷却10分钟(混沌)</cyn>
if __name__ == '__main__':
    userInfo={
         "account":"",          # 帐号
         "password":"",      # 密码
         "zone":"2",                   # 区服
         "player":"",             # 角色名
         "book":'',             # 自创秘籍名称
         "position":'force',               # 推演位置 : force unarmed dodge staff throwing parry sword blade club whip
         "attributes":["暴击伤害","移花"],             # 想要附加的属性或词条，目前支持 ：冷却百分比 冷却时间 破防 终伤 臂力 暴击 暴击伤害 命中 命中百分比 攻击 攻击百分比 剑心 不灭 战神  移花
         "continuation": False,        # 是否连续跳到指定的总次数 True：连续跳，不中断， False： 根据配置的step中断
         "total": 10,               # 总次数
         "step":1,                     # 每step次中断一次，continuation=False 时可用
         "feiyiId": "",            #有没有飞翼剑   False 无   True 有
         "haveBingxin": False          #有没有冰心丹   False 无   True 有
    }
    c = GetLoginInfo(userInfo["account"], userInfo["password"])
    c.getServer()
    utoken = c.getCookie()
    serverurl = c.getServerUrl(userInfo["zone"])
    userInfo["acctoken"]=utoken
    userInfo["serverip"]=serverurl
    wsp = wsgamePlayer(serverurl, utoken)
    wsp.start()
    while (wsp.getStatic()):
        time.sleep(1)
    userlist = wsp.getRoles()
    for role in userlist:
        if userInfo["player"] == role["name"]:
            userInfo["player"]=role["id"]
            break
    wsg = wsinfer(userInfo)
    wsg.start()




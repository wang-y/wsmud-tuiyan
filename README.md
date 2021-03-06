# wsmud-tuiyan   推演py脚本

编辑wstuiyan.py 243行的一下信息
```
 userInfo={
         "account":"",          # 帐号
         "password":"",      # 密码
         "zone":"2",                   # 区服
         "player":"",             # 角色名
         "book":'',             # 自创秘籍名称
         "position":'parry',               # 推演位置 : force unarmed dodge staff throwing parry sword blade club whip
         "attributes":["暴击伤害","移花"],             # 想要附加的属性或词条，目前支持 ：冷却百分比 冷却时间 破防 终伤 臂力 暴击 暴击伤害 命中 命中百分比 攻击 攻击百分比 剑心 不灭 战神  移花
         "continuation": False,        # 是否连续跳到指定的总次数 True：连续跳，不中断， False： 根据配置的step中断
         "total": 1000,               # 总次数
         "step":1,                     # 每step次中断一次，continuation=False 时可用
         "feiyiId": "",            #有没有飞翼剑   False 无   True 有
         "haveBingxin": False          #有没有冰心丹   False 无   True 有
    }
```

执行
```
python -u wstuiyan.py > tuiyan.log
```
即可

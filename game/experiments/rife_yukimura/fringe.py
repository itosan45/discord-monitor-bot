import sys;sys.path.insert(0,'/home/user/discord-monitor-bot/game/sprites')
import numpy as np
from PIL import Image
from mk import keyim
OUT='/tmp/claude-0/rife/out8'
A='/home/user/discord-monitor-bot/assets/sprites/'
def cells(p,n):
    s=Image.open(p).convert('RGB');w=s.size[0]//n;return [s.crop((i*w,0,(i+1)*w,s.size[1])) for i in range(n)]
def stats(im):
    k=keyim(im);a=k[...,3];rgb=k[...,:3].astype(int)
    edge=(a>0)&(a<250)
    pink=((np.minimum(rgb[...,0],rgb[...,2])-rgb[...,1])>50)&(a>20)
    fgp=(a>40).sum()
    return pink.sum()/max(fgp,1)*100,int(edge.sum()),int(fgp)
for name,orig,new in [('armed',A+'真田幸村_歩き_8コマ_依頼仕様版.png',OUT+'/yuki_armed_walk16_retimed.png'),('unarmed',A+'真田幸村_手ぶら_歩き_8コマ_v2.png',OUT+'/yuki_unarmed_walk16_retimed.png')]:
    o=[stats(c) for c in cells(orig,8)];r=[stats(c) for c in cells(new,16)]
    print(name,'元 ピンク残り%% 平均=%.2f 最大=%.2f'%(np.mean([x[0] for x in o]),max(x[0] for x in o)),'| 補間版 平均=%.2f 最大=%.2f'%(np.mean([x[0] for x in r]),max(x[0] for x in r)))
    print(name,'前景面積 元',[x[2] for x in o],'補間',[x[2] for x in r])

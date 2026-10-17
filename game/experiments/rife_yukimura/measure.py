import sys,os
sys.path.insert(0,os.path.dirname(__file__))
import numpy as np
from PIL import Image
import rife_core as R
sheet=np.array(Image.open('/home/user/discord-monitor-bot/assets/sprites/真田幸村_歩き_6コマ.png').convert('RGB'))
fr=[sheet[:,i*256:(i+1)*256] for i in range(6)]
net=R.load('/tmp/claude-0/rife/models/flownet_v4.25.pkl',1.0)
def fg(f):
    f=f.astype(int);return ~(((f[...,0]+f[...,2])/2-f[...,1])>120)
res=[]
for i in range(6):
    a,b=fr[i],fr[(i+1)%6]
    _,fl=R.interp_with_flow(net,a,b,0.5)
    # flow[0:2]: 中間→a、flow[2:4]: 中間→b。a→bの変位 ≈ 2*|flow|(t=0.5)
    mag=np.hypot(fl[0],fl[1])+np.hypot(fl[2],fl[3])  # = a→b 変位の大きさ
    m=(fg(a)|fg(b))
    legs=m.copy();legs[:130]=False
    body=m.copy();body[130:]=False
    res.append((float(mag[legs].mean()),float(mag[body].mean()),float(np.percentile(mag[legs],90))))
    print(i,'->',(i+1)%6,'脚の平均変位 %.2fpx / 上半身 %.2fpx / 脚上位10%% %.1fpx'%res[-1])
np.save('/tmp/claude-0/rife/out/legmotion.npy',np.array(res))

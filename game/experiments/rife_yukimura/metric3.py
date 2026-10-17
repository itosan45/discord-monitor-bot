import numpy as np
from PIL import Image
OUT='/tmp/claude-0/rife/out'
def fg(f):
    f=f.astype(int);return ~(((f[...,0]+f[...,2])/2-f[...,1])>120)
def feet(f):
    m=fg(f);rows=m[205:245]   # 足元の行だけ
    cols=np.where(rows.any(0))[0]
    # 2つの足: 列を連続区間に分け、左端の足の中心と右端の足の中心
    segs=[];s=cols[0];p=cols[0]
    for c in cols[1:]:
        if c-p>3: segs.append((s,p));s=c
        p=c
    segs.append((s,p))
    segs=[g for g in segs if g[1]-g[0]>=6]
    xs=[(a+b)/2 for a,b in segs]
    return min(xs),max(xs)
def seqs(path,n):
    s=np.array(Image.open(path).convert('RGB'));return [s[:,i*256:(i+1)*256] for i in range(n)]
for name,path,n in [('元6','/home/user/discord-monitor-bot/assets/sprites/真田幸村_歩き_6コマ.png',6),('等間隔12',OUT+'/yuki_walk12_v4.25_s1.png',12),('再配分12',OUT+'/yuki_walk12_retimed2.png',12)]:
    fr=seqs(path,n);F=[feet(f) for f in fr]
    print(name,'後ろ足x',[round(a) for a,b in F]);print(name,'前足x ',[round(b) for a,b in F]);
    print(name,'足の間隔',[round(b-a) for a,b in F])

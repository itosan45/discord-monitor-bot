import sys,os,json
sys.path.insert(0,os.path.dirname(__file__));sys.path.insert(0,'/home/user/discord-monitor-bot/game/sprites')
import numpy as np
from PIL import Image,ImageFilter
import rife_core as R
exec(open(os.path.join(os.path.dirname(__file__),'retime8.py')).read().split("fineA,segA=")[0].split("net=R.load")[0])  # 共通の定義(SHEETS,n,G)
net=R.load('/tmp/claude-0/rife/models/flownet_v4.25.pkl',1.0)
def load(p):
    s=np.array(Image.open(p).convert('RGB'));return [s[:,i*256:(i+1)*256] for i in range(n)]
def feat(f):
    f=f.astype(int);m=(~(((f[...,0]+f[...,2])/2-f[...,1])>120)).astype(np.uint8)*255;m[:130]=0
    im=Image.fromarray(m).filter(ImageFilter.GaussianBlur(5)).resize((128,128),Image.BILINEAR);return np.asarray(im,dtype=np.float32)/255
def dist(a,b):return float(np.sqrt(((feat(a)-feat(b))**2).sum()))
def plan_for(frames,N):
    fine=[]
    for i in range(n):
        for g in range(G):fine.append((i,g/G,frames[i] if g==0 else R.interp(net,frames[i],frames[(i+1)%n],g/G)))
    F=[feat(x[2]) for x in fine];seg=[float(np.sqrt(((F[k]-F[(k+1)%len(F)])**2).sum())) for k in range(len(F))]
    cum=np.concatenate([[0],np.cumsum(seg)]);M=cum[-1];plan=[]
    for k in range(N):
        s=k*M/N;kk=min(int(np.searchsorted(cum,s,side='right')-1),len(fine)-1);i,t,_=fine[kk]
        frac=(s-cum[kk])/max(seg[kk],1e-6);tt=t+frac/G
        plan.append((i,0.0) if (t==0 and frac<0.03) else (i,float(min(tt,0.999))))
    return plan,[round(sum(seg[i*G:(i+1)*G]),1) for i in range(n)]
def render(frames,plan):return [frames[i] if t<0.03 else R.interp(net,frames[i],frames[(i+1)%n],t) for i,t in plan]
OUT='/tmp/claude-0/rife/out8'
res={}
for name,p in SHEETS.items():
    fr=load(p);N=16;plan,pl=plan_for(fr,N);seq=render(fr,plan)
    eq=[];
    for i in range(n):eq+=[fr[i],R.interp(net,fr[i],fr[(i+1)%n],0.5)]
    Image.fromarray(np.concatenate(seq,axis=1)).save(f'{OUT}/yuki_{name}_walk16_retimed.png')
    Image.fromarray(np.concatenate(eq,axis=1)).save(f'{OUT}/yuki_{name}_walk16_even.png')
    st=lambda s:[dist(s[k],s[(k+1)%len(s)]) for k in range(len(s))]
    # 元8(2倍時間で比較するため各ステップ値は2倍して表示)
    res[name]={'orig8':[x for x in st(fr)],'even16':st(eq),'retimed16':st(seq),'plan':plan,'pathlen':pl}
    for k in('orig8','even16','retimed16'):
        v=np.array(res[name][k]);print(name,k,'CV=%.2f 最大/最小=%.2f'%(np.std(v)/np.mean(v),v.max()/v.min()))
    print(name,'plan',[(i,round(t,2)) for i,t in plan])
json.dump({k:{kk:(vv if kk!='plan' else vv) for kk,vv in v.items()} for k,v in res.items()},open(OUT+'/res.json','w'))

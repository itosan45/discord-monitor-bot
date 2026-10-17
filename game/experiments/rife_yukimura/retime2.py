import sys,os
sys.path.insert(0,os.path.dirname(__file__))
import numpy as np
from PIL import Image,ImageFilter
import rife_core as R
OUT='/tmp/claude-0/rife/out'
sheet=np.array(Image.open('/home/user/discord-monitor-bot/assets/sprites/真田幸村_歩き_6コマ.png').convert('RGB'))
fr=[sheet[:,i*256:(i+1)*256] for i in range(6)]
net=R.load('/tmp/claude-0/rife/models/flownet_v4.25.pkl',1.0)
G=24  # 各組を24分割した細かい補間列を作り、画像空間の経路長を測る
def feat(f):
    f=f.astype(int);m=(~(((f[...,0]+f[...,2])/2-f[...,1])>120)).astype(np.uint8)*255
    m[:130]=0   # 脚だけ(上半身の揺れは除く)
    im=Image.fromarray(m).filter(ImageFilter.GaussianBlur(5)).resize((128,128),Image.BILINEAR)
    return np.asarray(im,dtype=np.float32)/255
fine=[]  # (pair i, t, image)
for i in range(6):
    for g in range(G):
        t=g/G
        fine.append((i,t,fr[i] if g==0 else R.interp(net,fr[i],fr[(i+1)%6],t)))
F=[feat(x[2]) for x in fine]
seg=[float(np.sqrt(((F[k]-F[(k+1)%len(F)])**2).sum())) for k in range(len(F))]
cum=np.concatenate([[0],np.cumsum(seg)]);M=cum[-1]
print('経路長(6組ごと)',[round(sum(seg[i*G:(i+1)*G]),1) for i in range(6)])
def pick(s):
    k=int(np.searchsorted(cum,s,side='right')-1);k=min(k,len(fine)-1)
    i,t,img=fine[k]
    # 細かい列の中でさらに線形に進める(次の細かい点との間はRIFEで補間)
    nxt=fine[(k+1)%len(fine)]
    frac=(s-cum[k])/max(seg[k],1e-6)
    tt=t+frac/G
    if frac<0.03: return img
    return R.interp(net,fr[i],fr[(i+1)%6],min(tt,0.999)) if tt<1 else fr[(i+1)%6]
for N in (12,16):
    seq=[pick(k*M/N) for k in range(N)]
    Image.fromarray(np.concatenate(seq,axis=1)).save(f'{OUT}/yuki_walk{N}_retimed2.png')
    steps=[float(np.sqrt(((feat(seq[k])-feat(seq[(k+1)%N]))**2).sum())) for k in range(N)]
    print(N,'隣のコマ間の脚の変化(画像空間)',[round(x,1) for x in steps],'最大/最小=%.2f'%(max(steps)/min(steps)))
# 比較用に元・等間隔の同指標
def steps_of(frames):
    n=len(frames);return [float(np.sqrt(((feat(frames[k])-feat(frames[(k+1)%n]))**2).sum())) for k in range(n)]
s6=steps_of(fr);print('元6',[round(x,1) for x in s6],'最大/最小=%.2f'%(max(s6)/min(s6)))
r12=np.array(Image.open(OUT+'/yuki_walk12_v4.25_s1.png'));u=[r12[:,i*256:(i+1)*256] for i in range(12)]
s12=steps_of(u);print('等間隔12',[round(x,1) for x in s12],'最大/最小=%.2f'%(max(s12)/min(s12)))

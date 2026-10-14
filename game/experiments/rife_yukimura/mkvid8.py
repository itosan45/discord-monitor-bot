import numpy as np, subprocess, os, json
from PIL import Image, ImageDraw
OUT='/tmp/claude-0/rife/out8';A='/home/user/discord-monitor-bot/assets/sprites/'
def seq(p,n):
    s=np.array(Image.open(p).convert('RGB'));return [s[:,i*256:(i+1)*256] for i in range(n)]
BG=np.array([92,78,62])
def key(f):
    f=f.astype(int);r,g,b=f[...,0],f[...,1],f[...,2];m=np.clip(((r+b)/2-g-60)/120,0,1);return (f*(1-m[...,None])+BG*m[...,None]).astype(np.uint8)
def panel(f,l):
    im=Image.fromarray(key(f)).resize((512,512),Image.LANCZOS);ImageDraw.Draw(im).text((8,8),l,fill=(255,255,255));return np.array(im)
for name,src in [('armed',A+'真田幸村_歩き_8コマ_依頼仕様版.png'),('unarmed',A+'真田幸村_手ぶら_歩き_8コマ_v2.png')]:
    o=seq(src,8);e=seq(f'{OUT}/yuki_{name}_walk16_even.png',16);r=seq(f'{OUT}/yuki_{name}_walk16_retimed.png',16)
    d=f'{OUT}/vid_{name}';os.makedirs(d,exist_ok=True)
    for t in range(80):  # 20fps x 4s = 5 cycles
        row=np.concatenate([panel(o[(t//2)%8],'A original 8 (10fps)'),panel(e[t%16],'B even x2 RIFE (20fps)'),panel(r[t%16],'C retimed RIFE (20fps)')],axis=1)
        Image.fromarray(row).save(f'{d}/f{t:03d}.png')
    subprocess.run(['ffmpeg','-y','-v','error','-framerate','20','-i',d+'/f%03d.png','-vf','loop=loop=2:size=80,format=yuv420p','-c:v','libx264','-crf','21',f'{OUT}/compare_{name}.mp4'],check=True)
# 速度の棒グラフ: 隣のコマ間の脚の変化(画像空間)。元8は2コマ=1/20秒分に換算して比較できるよう単位時間あたりに揃える
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
res=json.load(open(OUT+'/res.json'))
import matplotlib.font_manager as fm
jp=[f.name for f in fm.fontManager.ttflist if any(k in f.name for k in('Noto Sans CJK','IPAGothic','IPAexGothic','TakaoGothic','VL Gothic','Droid Sans Fallback'))]
if jp:plt.rcParams['font.family']=jp[0]
fig,ax=plt.subplots(2,1,figsize=(11,6.5))
for a,name in zip(ax,('armed','unarmed')):
    r=res[name];o=np.array(r['orig8'])/2   # 元は1コマ=0.1秒、補間版は1コマ=0.05秒→元を半分に換算
    a.plot(np.arange(8)*2,o,'o-',label='A 元8コマ(0.05秒あたりに換算)',color='gray')
    a.plot(np.arange(16),r['even16'],'s--',label='B 等間隔2倍',color='tab:orange')
    a.plot(np.arange(16),r['retimed16'],'^-',label='C 等速化',color='tab:green')
    a.set_title('歩き('+('武器あり' if name=='armed' else '素手')+') 隣のコマ間の脚の動きの大きさ(小さいほどゆっくり)');a.legend(fontsize=8);a.set_xlabel('コマ番号(1周=0.8秒)')
plt.tight_layout();plt.savefig(OUT+'/speed_chart.png',dpi=90)
print('ok',jp[:1])

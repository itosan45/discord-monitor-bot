import os,numpy as np,json,io,base64,sys
from PIL import Image
from scipy import ndimage as ndi
SRC=os.path.join(os.path.dirname(os.path.abspath(__file__)),'../../assets/sprites/')
HERO={'yuki':'真田幸村','kage':'上杉景勝','mitsu':'石田三成','nobu':'織田信長','shin':'武田信玄','musashi':'宮本武蔵'}
ANIM=[('idle','待機_4'),('walk','歩き_6'),('jump','ジャンプ_4'),('hit','被弾_2'),('down','ダウン_4'),('getup','起き上がり_4'),('dead','やられ_4'),('jatk','ジャンプ攻撃_4'),
 ('a1','通常1_5'),('a2','通常2_5'),('a3','通常3_%d'),('a4','通常4_%d'),('a5','通常5_7'),('dash','ダッシュ_5'),('spc','必殺_8'),('gstart','ガード構え_2'),('guard','ガード維持_4'),('ghit','ガード受け止め_2'),('gend','ガード解除_2'),('dodgeB','後退回避_4'),('dodgeF','前方回避_5'),('kspin','鎖鎌_分銅旋回_4'),('kthrow','鎖鎌_分銅投擲_6')]
import glob,os
BOSS={'boss1':'井伊直政','boss2':'最上義光','boss3':'徳川家康','boss4':'小早川秀秋','boss5':'徳川秀忠','boss7':'本多忠勝','boss8':'黒田長政','boss9':'福島正則'}
ANIMB=[('idle','待機_4'),('walk','歩き_6'),('hit','被弾_2'),('a1','通常攻撃_6'),('big','大技_8'),('dash','突進_6'),('dead','やられ_7')]
ENEMY={'spear':'敵_足軽槍','sword':'敵_足軽刀','archer':'敵_弓足軽','gun':'敵_鉄砲足軽','ninja':'敵_忍者'}
ANIME=[('idle','待機_4'),('walk','歩き_8'),('a1','攻撃_6'),('hit','被弾_2'),('down','ダウン_4'),('getup','起き上がり_4'),('dead','やられ_4')]
NAME=dict(HERO);NAME.update(BOSS);NAME.update(ENEMY)
def find(h,key):
    cand=[os.path.basename(f) for f in glob.glob(SRC+NAME[h]+'_*')]
    pre=NAME[h]+'_'+'_'.join(key.split('_')[:-1])+'_'
    c=[x for x in cand if x.startswith(pre)]
    for tag in ['_v3','追加v1','短刀修正版','再生成版','縮尺修正版','_v2','依頼仕様版','鉄砲主武器版','鉄砲明記版']:
        t=[x for x in c if tag in x]
        if t:return t[0]
    return c[0] if c else None
def keyim(im):
    a=np.array(im.convert('RGB')).astype(float);r,g,b=a[...,0],a[...,1],a[...,2]
    d=np.abs(r-255)+g+np.abs(b-255)
    al=np.clip((d-90)/(180-90),0,1)
    bgm=al<0.5
    edge=ndi.binary_dilation(bgm,iterations=3)&(al>0)
    ex=np.clip(np.minimum(r,b)-g,0,None)*0.85
    r2=np.where(edge,r-ex,r);b2=np.where(edge,b-ex,b)
    out=np.dstack([r2,g,b2,al*255]);return np.clip(out,0,255).astype('uint8')
def clean(c):
    m=c[...,3]>40
    if not m.any():return c
    lab,k=ndi.label(ndi.binary_dilation(m,iterations=10))
    sizes=ndi.sum(m,lab,range(1,k+1));main=1+int(np.argmax(sizes));keep=(lab==main)
    h,w=m.shape
    for i in range(1,k+1):
        if i==main:continue
        ys,xs=np.where((lab==i)&m)
        if len(xs)>250 and xs.min()>8 and xs.max()<w-9:keep|=(lab==i)
    keep=ndi.binary_dilation(keep,iterations=3)
    c=c.copy();c[...,3]=np.where(keep,c[...,3],0);return c

def split_strip(a,n):
    """Split a strip into n frames by connected parts (keeps spears that cross cell borders, drops cut-off neighbour scraps)."""
    H,Wt=a.shape[:2];cw=Wt//n;m=a[...,3]>40
    lab,k=ndi.label(ndi.binary_dilation(m,iterations=2));lab=np.where(m,lab,0)
    objs=ndi.find_objects(lab);size=ndi.sum(m,lab,range(1,k+1))
    mains=[]
    for i in range(n):
        sl=lab[:,i*cw:(i+1)*cw];ids,cnt=np.unique(sl[sl>0],return_counts=True)
        mains.append(int(ids[np.argmax(cnt)]) if len(ids) else None)
    out=[np.zeros((H,cw*2,4),np.uint8) for _ in range(n)]
    def put(i,ys,xs):
        tx=xs-i*cw+cw//2;ok=(tx>=0)&(tx<cw*2);out[i][ys[ok],tx[ok]]=a[ys[ok],xs[ok]]
    for j,ob in enumerate(objs,1):
        if ob is None or size[j-1]<25:continue
        cm=lab[ob]==j;ys,xs=np.where(cm);ys=ys+ob[0].start;xs=xs+ob[1].start
        own=[i for i in range(n) if mains[i]==j]
        if len(own)==1:put(own[0],ys,xs);continue
        if len(own)>1:
            cell=np.clip(xs//cw,0,n-1)
            for i in own:s=cell==i;put(i,ys[s],xs[s])
            continue
        xa,xb=ob[1].start,ob[1].stop-1
        rmin=np.array([r.nonzero()[0].min() for r in cm if r.any()]);rmax=np.array([r.nonzero()[0].max() for r in cm if r.any()])
        if (rmin==rmin.min()).sum()>=18 or (rmax==rmax.max()).sum()>=18:continue
        if any((abs(xa-b)<=3 or abs(xb-b-1)<=3) and not (xa<b-4 and xb>b+4) for b in range(cw,Wt,cw)):continue
        if xa<=3 or xb>=Wt-4:continue
        cx=xs.mean();best=None
        for i in range(n):
            if mains[i] is None:continue
            o=objs[mains[i]-1];d=0 if o[1].start<=cx<=o[1].stop else min(abs(cx-o[1].start),abs(cx-o[1].stop))
            if best is None or d<best[0]:best=(d,i)
        if best is None or best[0]>cw*0.3 or size[j-1]<60:continue
        put(best[1],ys,xs)
    return out,cw*2

def feather(c,w=16):
    """Soften straight vertical cut edges left by the source sheets."""
    al=c[...,3].astype(float);m=al>40
    if not m.any():return c
    rows=[r for r in range(m.shape[0]) if m[r].any()]
    xmin=np.array([m[r].nonzero()[0].min() for r in rows]);xmax=np.array([m[r].nonzero()[0].max() for r in rows])
    X=np.arange(m.shape[1])
    for side,arr in (('r',xmax),('l',xmin)):
        v=arr.max() if side=='r' else arr.min();hit=(arr==v).sum()
        if hit<22:continue
        ramp=np.clip((v-X)/w,0,1) if side=='r' else np.clip((X-v)/w,0,1)
        al=al*ramp[None,:]**0.8
    c=c.copy();c[...,3]=al.astype(np.uint8);return c

def descrap(c):
    """Drop pieces of neighbouring frames that ended up detached in this cell."""
    al=c[...,3];m=al>40
    lab,k=ndi.label(m,structure=np.ones((3,3)))
    if k<2:return c
    sz=ndi.sum(m,lab,range(1,k+1));big=1+int(np.argmax(sz));dist=ndi.distance_transform_edt(lab!=big)
    c=c.copy()
    for j in range(1,k+1):
        if j==big:continue
        comp=lab==j;ys,xs=np.where(comp)
        rows=np.unique(ys);lx=np.array([xs[ys==r].min() for r in rows]);rx=np.array([xs[ys==r].max() for r in rows])
        straight=max((lx==lx.min()).sum(),(rx==rx.max()).sum())>=6
        if (sz[j-1]<0.12*sz.max() and dist[comp].min()>6) or (sz[j-1]<0.15*sz.max() and straight and dist[comp].min()>1):
            mm=ndi.binary_dilation(lab==j,iterations=2);c[...,3][mm&(al<=255)&~ndi.binary_dilation(lab==big,iterations=1)]=0
    return c
DEMAG={('musashi','spc')}
CUTS={('yuki','a1',0):[(304,175,340,256)]}
SRCA={}
KFIX={('kage','kspin'):1.12,('mitsu','kspin'):0.85,('nobu','kspin'):1.19,('shin','kspin'):1.23,('musashi','kspin'):1.27,('shin','a4'):0.76,('shin','a1'):1.08,('yuki','a2'):0.86,('yuki','spc'):0.68,('mitsu','gstart'):0.68,('mitsu','guard'):0.68,('mitsu','ghit'):0.68,('mitsu','gend'):0.68,('mitsu','dodgeF'):0.72,('mitsu','dodgeB'):0.72,('nobu','dodgeF'):0.94,('nobu','dodgeB'):0.94,('nobu','a1'):0.9,('nobu','a4'):0.9,('kage','a4'):0.9,('yuki','dash'):0.84,('mitsu','jatk'):0.74,('mitsu','dash'):1.28,('nobu','jatk'):1.35,('kage','jatk'):1.2,('shin','a3'):0.85,('shin','jatk'):1.08}
REMAP={'yuki':{
 'a1':[('a1',0),('a1',1),('dash',2),('dash',2),('a1',1)],
 'a4':[('a4',0),('a4',0),('a1',0),('a3',0),('a3',0),('a3',1),('a3',5)],
 'dash':[('dash',0),('dash',1),('dash',2),('dash',2),('dash',1)]}}
import os
RK=json.load(open('regk.json')) if os.path.exists('regk.json') else {}
BM=json.load(open('bodymetrics.json')) if os.path.exists('bodymetrics.json') else {}
def strip_k(h,an):
    if h not in HERO or h not in BM:return 1.0
    ia=BM[h]['idle']['a'];a=BM[h].get(an,{}).get('a')
    if h not in RK or an not in RK[h]:
        return max(0.7,min(2.2,(ia/a)**0.5)) if a else 1.0
    iou,kI=RK[h][an]
    if not a:return kI
    kA=(ia/a)**0.5
    k=kA if iou<0.5 else (kI*kA)**0.5
    return max(0.7,min(2.2,k))
def build(h,Hg=190,q=52):
    frames={};names=[]
    for an,key in (ANIMB if h in BOSS else ANIME if h in ENEMY else ANIM):
        f=find(h,key)
        if not f:continue
        import re;n=int(re.search(r'_(\d+)コマ',f).group(1));im=Image.open(SRC+f)
        a=keyim(im);cw=im.size[0]//n
        if h in HERO or h in ENEMY:cells,CW=split_strip(a,n);cells=[descrap(feather(c)) for c in cells]
        else:
            cells=[clean(a[:,i*cw:(i+1)*cw]) for i in range(n)];CW=cw
        for (mh,ma,mi),boxes in CUTS.items():
            if mh==h and ma==an and mi<len(cells):
                cells[mi]=cells[mi].copy()
                for x0,y0,x1,y1 in boxes:cells[mi][y0:y1,x0:x1,3]=0
        if (h,an) in DEMAG:
            for i,c in enumerate(cells):
                c=cells[i]=c.copy();H0=c.shape[0];r,g,b=[c[...,k].astype(float) for k in range(3)]
                mg=(r>g+40)&(b>g+25)&(c[...,3]>0);mg[:int(H0*0.6)]=False
                L=(0.3*r+0.59*g+0.11*b)/110.0
                for k,v in enumerate((120,78,44)):c[...,k][mg]=np.clip(L[mg]*v,0,255).astype(np.uint8)
        frames[an]=cells
    for an,lst in REMAP.get(h,{}).items():
        src={k:list(v) for k,v in frames.items()}
        frames[an]=[src[k][i] for k,i in lst];SRCA.setdefault(h,{})[an]=[k for k,i in lst]
    if 'getup' in frames:
        for k in ('down','dead'):
            if k not in frames:frames[k]=frames['getup'][::-1]
    # reference scale from idle frame0 bbox height
    c0=frames['idle'][0];ys=np.where(c0[...,3]>40)[0];href=ys.max()-ys.min()+1
    if h in ENEMY:
        import norm as _n
        bh=np.median([_n.body(c)['h'] for c in frames['idle'] if _n.body(c)])
        href=bh;Hg=142
    s=Hg/href
    ground=int(np.median([np.where(c[...,3]>40)[0].max() for c in frames['idle']+frames.get('walk',[])]))
    CWc=CW/2
    items=[]
    for an,cells in frames.items():
        kk0=strip_k(h,an) if h in HERO else 1.0
        if h in HERO or h in ENEMY:
            gs=max(np.where(c[...,3]>40)[0].max() for c in cells if (c[...,3]>40).any())+1
        else:
            gs=ground
        for i,c in enumerate(cells):
            kk=kk0
            if h in SRCA and an in SRCA[h]:kk=strip_k(h,SRCA[h][an][i])
            if (h,(SRCA.get(h,{}).get(an) or [an]*99)[i]) in KFIX:kk*=KFIX[(h,(SRCA.get(h,{}).get(an) or [an]*99)[i])]
            ys,xs=np.where(c[...,3]>40)
            if len(xs)==0:items.append((an,i,None));continue
            x0,x1,y0,y1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
            im=Image.fromarray(c[y0:y1,x0:x1],'RGBA')
            f=s*kk;fs=s*min(kk,1.0)
            nw,nh=max(1,round(im.width*fs)),max(1,round(im.height*fs))
            im=im.resize((nw,nh),Image.LANCZOS)
            dx=round((x0-CWc)*f);dy=round((y0-gs)*f);ds=round(f/fs,3)
            items.append((an,i,(im,dx,dy,ds)))
    # shelf pack
    AW=2048;x=y=rowh=0;pos=[];
    for an,i,t in items:
        if t is None:pos.append(None);continue
        im=t[0]
        if x+im.width>AW:x=0;y+=rowh+2;rowh=0
        pos.append((x,y));x+=im.width+2;rowh=max(rowh,im.height)
    AH=y+rowh
    atlas=Image.new('RGBA',(AW,AH),(0,0,0,0));meta={}
    for (an,i,t),p in zip(items,pos):
        meta.setdefault(an,[])
        if t is None:meta[an].append(None);continue
        im,dx,dy,ds=t;atlas.paste(im,p);meta[an].append([p[0],p[1],im.width,im.height,dx,dy,ds])
    b=io.BytesIO();atlas.save(b,'WEBP',quality=q,method=4)
    return atlas,meta,b.getvalue()
if __name__=='__main__':
    allm=json.load(open('sprmeta.json')) if os.path.exists('sprmeta.json') else {};tot=0
    only=sys.argv[1:]
    for h in [x for x in list(HERO)+list(BOSS)+list(ENEMY) if not only or x in only]:
        at,meta,by=build(h,Hg=(176 if h in ENEMY else 190));open(f'atlas_{h}.webp','wb').write(by);at.save(f'atlas_{h}.png');allm[h]=meta;tot+=len(by);print(h,at.size,len(by)//1024,'KB',{k:len(v) for k,v in meta.items()})
    json.dump(allm,open('sprmeta.json','w'));print('total',tot//1024,'KB')

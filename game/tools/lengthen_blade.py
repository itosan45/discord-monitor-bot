#!/usr/bin/env python3
"""アトラスの刀の長さを、全コマで同じにそろえる(2026-10-17 オーナー「政宗の刀が短すぎる」「全コマ刀同じ長さが当たり前」)。
元絵(Gemini)の刀は、動作ごとに刃の長さがまちまち(政宗は待機・歩きで体高の約0.4倍、他の行は約0.5倍)。
刃の先(切っ先)を刃の軸に沿って外へずらし、できた隙間を刃の断面(鋼の色+縁取り)で埋めて、目標の長さ(--target、実際に画面に出る画素での刃の長さ)まで伸ばす。
刃の位置(切っ先と柄元)は鋼色の塊から自動で求める。手や兜で誤検出するコマは tools/lengthen_blade_overrides.json に手で座標を書く(コマ内の座標=アトラス画素)。
使い方: python3 game/tools/lengthen_blade.py <キー> --rows idle,walk,... --target 105 [--preview out.png | --apply]
  --preview: 前後の比較画像と、各コマの測った長さを出すだけ。 --apply: gfx/atlas_<キー>.webp の末尾に新しいコマを足し、sprmeta.json のコマを差し替える(元のコマは残るが使われない)。
  加工したコマは tools/lengthen_blade_log.json に記録し、二重に加工しない。mk.py で作り直すと元に戻るので、作り直したら再実行すること。
  長い側(目標より長いコマ)は縮めない(報告だけ)。スプライトを新しく取り込んだら、まず --preview の長さの一覧を見て、行ごと・コマごとの長さの不揃いを直すこと。"""
import sys,os,json,argparse
import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage as ndi
H=os.path.dirname(os.path.abspath(__file__));REPO=os.path.dirname(os.path.dirname(H))
LOG=os.path.join(H,'lengthen_blade_log.json');OVR=os.path.join(H,'lengthen_blade_overrides.json')
STEEL=75
def steel_mask(c):
    c=c.astype(int);al=c[...,3];r,g,b=c[...,0],c[...,1],c[...,2]
    mx=np.maximum(np.maximum(r,g),b);mn=np.minimum(np.minimum(r,g),b)
    return (al>200)&(mn>STEEL)&((mx-mn)<55)
def find_blade(c,minlen):
    m=steel_mask(c);lab,k=ndi.label(ndi.binary_dilation(m,iterations=1));best=None
    for i in range(1,k+1):
        ys,xs=np.nonzero((lab==i)&m)
        if len(xs)<12:continue
        ext=np.hypot(xs.max()-xs.min(),ys.max()-ys.min())
        if best is None or ext>best[0]:best=(ext,xs,ys)
    return best if best and best[0]>=minlen else None
def detect(c,ov=None):
    """切っ先・柄元・向き・刃の画素(あれば)を返す。ov={'tip':[x,y],'base':[x,y]} があればそれを使う"""
    al=c[...,3]>40
    if ov:
        tip=np.array(ov['tip'],float);base=np.array(ov['base'],float);d=tip-base;L=np.hypot(*d);d=d/L
        return dict(tip=tip,base=base,d=d,L=L,pts=None,proj=None)
    by,bx=np.nonzero(al)
    if len(bx)==0:return None
    fh=by.max()-by.min()+1;res=find_blade(c,max(18,0.14*fh))
    if res is None:return None
    ext,xs,ys=res;cx,cy=bx.mean(),by.mean();pts=np.stack([xs,ys],1).astype(float);mu=pts.mean(0)
    _,_,vt=np.linalg.svd(pts-mu,full_matrices=False);d=vt[0];proj=(pts-mu)@d
    if np.hypot(*(pts[proj.argmax()]-[cx,cy]))<np.hypot(*(pts[proj.argmin()]-[cx,cy])):d=-d;proj=-proj
    lo,hi=proj.min(),proj.max();L=hi-lo
    sel=proj>hi-0.4*L
    if sel.sum()<4:return None
    q=pts[sel];m2=q.mean(0);_,_,vt2=np.linalg.svd(q-m2,full_matrices=False);dl=vt2[0]
    if dl@d<0:dl=-dl
    return dict(tip=pts[proj.argmax()],base=pts[proj.argmin()],d=dl/np.hypot(*dl),L=L,pts=pts,proj=proj)
def synth_tip(c,D,dL,lo_,hi_,base,nrm):
    """元絵のコマの端で刃が切れているコマ: 切れた所から同じ太さの刃を延ばし、最後を尖らせて切っ先を描き足す"""
    Hh,W=c.shape[:2];SS=4;d=D['d'];tip=D['tip'];hw=max(1.6,(hi_-lo_+1)/2.0-0.3)
    img=Image.new('RGBA',(W*SS,Hh*SS),(0,0,0,0));dr=ImageDraw.Draw(img);taper=min(12.0,0.3*dL);n=40
    def poly(scale,extra):
        left=[];right=[]
        for i in range(n+1):
            t=dL*i/n;f=1.0-0.25*min(1.0,t/max(1.0,dL-taper));w=(hw*scale*f+extra)*(1.0 if t<dL-taper else max(0.0,(dL-t)/taper))
            pc=tip+d*(t-0.5);left.append(pc+nrm*w);right.append(pc-nrm*w)
        return [tuple(v*SS) for v in left+right[::-1]]
    col=(176,180,190,255)
    if D['pts'] is not None:
        pr=D['proj'];sel=pr>pr.max()-8;rgb=c[...,:3][np.round(D['pts'][sel][:,1]).astype(int),np.round(D['pts'][sel][:,0]).astype(int)].mean(0);col=(int(rgb[0]),int(rgb[1]),int(rgb[2]),255)
    dr.polygon(poly(1.0,0.7),fill=(38,38,44,255));dr.polygon(poly(1.0,-0.3),fill=col)
    dr.polygon(poly(0.28,0.0),fill=(min(255,col[0]+55),min(255,col[1]+55),min(255,col[2]+55),255))  # 刃の中心の明るい筋
    big=np.array(img.resize((W,Hh),Image.LANCZOS)).astype(float);out=c.astype(float).copy();a2=big[...,3:4]/255*(c[...,3:4]<30)
    out[...,:3]=out[...,:3]*(1-a2)+big[...,:3]*a2;out[...,3:4]=np.maximum(out[...,3:4],big[...,3:4]*(c[...,3:4]<30))
    return np.clip(out,0,255).astype(np.uint8)
def lengthen(c,target_px,ov=None):
    """c の刀を目標の長さ(アトラス画素)まで伸ばす。戻り値=(新しい絵,情報)。伸ばさない時は (c,{'L':..,'dL':0})、検出できない時は (c,None)"""
    D=detect(c,ov)
    if D is None:return c,None
    L=D['L'];dL=target_px-L
    if dL<3:return c,dict(L=float(L),dL=0.0)
    Hh,W=c.shape[:2];al=c[...,3]>40;d=D['d'];nrm=np.array([-d[1],d[0]]);tip=D['tip']
    for _ in range(60):
        t2=tip+d*dL
        if 3<t2[0]<W-3 and 3<t2[1]<Hh-3:break
        dL*=0.93
    if dL<3:return c,dict(L=float(L),dL=0.0)
    cut_d=0.28*L;base=tip-d*cut_d  # 切る位置: 切っ先から刃の28%手前
    yy,xx=np.mgrid[0:Hh,0:W];P=np.stack([xx,yy],-1).astype(float)-base;pa=P@d;pn=P@nrm
    if D['pts'] is not None:
        proj=D['proj'];tproj=proj.max();near=np.abs(proj-(tproj-cut_d))<3.0
        if near.sum()<2:near=np.abs(proj-(tproj-cut_d))<6.0
        if near.sum()<2:return c,dict(L=float(L),dL=0.0,fail='width')
        nn=(D['pts'][near]-base)@nrm;lo_,hi_=np.percentile(nn,[5,95]);lo_=int(np.floor(lo_));hi_=int(np.ceil(hi_))
        if hi_-lo_>9:m_=(lo_+hi_)/2;lo_,hi_=int(round(m_-4)),int(round(m_+4))
    else:  # 手で座標を指定したコマ: 切っ先の少し手前で、軸に直交して絵が連続している幅を刃の太さとする
        p0=tip-d*4.0;have=set()
        for o in range(-8,9):
            x,y=int(round(p0[0]+nrm[0]*o)),int(round(p0[1]+nrm[1]*o))
            if 0<=x<W and 0<=y<Hh and c[y,x,3]>120:have.add(o)
        if have:
            lo_=hi_=min(have,key=abs)
            while lo_-1 in have:lo_-=1
            while hi_+1 in have:hi_+=1
        else:lo_,hi_=-2,2
        lo_=max(lo_,-4);hi_=min(hi_,4)
    clipped=bool(ov and ov.get('clipped'))
    if clipped:return synth_tip(c,D,dL,lo_,hi_,base,nrm),dict(L=float(L),dL=float(dL),clipped=True)
    half_lo,half_hi=float(lo_)-1.5,float(hi_)+1.5;ctr=(half_lo+half_hi)/2
    reg=al&(pa>0)&(np.abs(pn-ctr)<(half_hi-half_lo)/2+2.2)
    lab,k=ndi.label(reg);ids=set()
    ty0,tx0=int(round(tip[1])),int(round(tip[0]))
    for yy_ in range(max(0,ty0-3),min(Hh,ty0+4)):
        for xx_ in range(max(0,tx0-3),min(W,tx0+4)):
            if lab[yy_,xx_]>0:ids.add(int(lab[yy_,xx_]))
    tm=np.isin(lab,list(ids))
    if tm.sum()<6:return c,dict(L=float(L),dL=0.0,fail='tip')
    out=c.copy();ty,tx=np.nonzero(tm);vals=c[ty,tx].copy();out[ty,tx]=0
    nx=np.round(tx+d[0]*dL).astype(int);ny=np.round(ty+d[1]*dL).astype(int);ok=(nx>=0)&(nx<W)&(ny>=0)&(ny<Hh);out[ny[ok],nx[ok]]=vals[ok]
    off=list(range(lo_-1,hi_+2));sec=[]
    for o in off:
        p0=base+nrm*o-d*1.0;x,y=int(round(p0[0])),int(round(p0[1]));px=c[y,x] if 0<=x<W and 0<=y<Hh else np.zeros(4,np.uint8)
        if o<lo_ or o>hi_:
            lum=0.3*px[0]+0.59*px[1]+0.11*px[2];px=px if (px[3]>=150 and lum<95) else np.array([38,38,44,255],np.uint8)
        elif px[3]<150:px=np.array([170,174,182,255],np.uint8)
        sec.append(px)
    sec=np.array(sec)
    for i in range(int(np.ceil(dL))+2):
        for j,o in enumerate(off):
            p0=base+nrm*o+d*float(i);x,y=int(round(p0[0])),int(round(p0[1]))
            if 0<=x<W and 0<=y<Hh and out[y,x,3]<40:out[y,x]=sec[j]
    return out,dict(L=float(L),dL=float(dL))
def main():
    global STEEL
    ap=argparse.ArgumentParser();ap.add_argument('key');ap.add_argument('--rows',required=True);ap.add_argument('--target',type=float,default=105.0,help='目標の刃の長さ(画面に出る画素)')
    ap.add_argument('--steel',type=int,default=75);ap.add_argument('--skip',default='',help='例: a1:2,order:3(加工しないコマ)');ap.add_argument('--preview');ap.add_argument('--apply',action='store_true')
    a=ap.parse_args();STEEL=a.steel
    meta_p=os.path.join(REPO,'game/sprites/sprmeta.json');M=json.load(open(meta_p));S=M[a.key]
    atl_p=os.path.join(REPO,'gfx/atlas_%s.webp'%a.key);A=Image.open(atl_p).convert('RGBA');AA=np.array(A)
    log=json.load(open(LOG)) if os.path.exists(LOG) else {}
    ovr=json.load(open(OVR)).get(a.key,{}) if os.path.exists(OVR) else {}
    skip=set(t for t in a.skip.split(',') if t)|set(ovr.get('skip',[]))
    P=70;new={};previews=[];table={}
    for r in a.rows.split(','):
        line=[]
        for i,f in enumerate(S[r]):
            key='%s:%d'%(r,i);sx,sy,w,h,ox,oy,sc=f;sx,sy,w,h=int(sx),int(sy),int(w),int(h)
            can=np.zeros((h+2*P,w+2*P,4),np.uint8);can[P:P+h,P:P+w]=AA[sy:sy+h,sx:sx+w]
            ov=ovr.get('frames',{}).get(key)
            if ov:ov={k:([v[0]+P,v[1]+P] if isinstance(v,list) else v) for k,v in ov.items()}
            if key in skip:line.append('  skip');continue
            c2,info=lengthen(can,a.target/sc,ov)
            if info is None:line.append('  --  ');continue
            line.append('%3d%s'%(round(info['L']*sc),'+%d'%round(info['dL']*sc) if info['dL'] else '   '))
            if info['dL']==0 or key in log.get(a.key,[]):continue
            ys,xs=np.nonzero(c2[...,3]>0);x0,x1,y0,y1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
            new[(r,i)]=(c2[y0:y1,x0:x1],[None,None,int(x1-x0),int(y1-y0),round(float(ox+(x0-P)*sc),2),round(float(oy+(y0-P)*sc),2),sc])
            if a.preview:previews.append((r,i,can,c2))
        print('%-7s'%r,' '.join(line))
    print('(数字=今の刃の長さ(画素)、+数字=伸ばす長さ。skip=加工しない、--=刃を検出できない)')
    if a.preview and previews:
        n=len(previews);cols=min(n,6);rowsn=(n+cols-1)//cols;cw=max(p[2].shape[1] for p in previews);ch=max(p[2].shape[0] for p in previews)
        sh=Image.new('RGB',(cols*cw,rowsn*ch*2),(90,110,90));dr=ImageDraw.Draw(sh)
        for k,(r,i,b,c2) in enumerate(previews):
            for j,im in enumerate((b,c2)):
                t=Image.fromarray(im);bg=Image.new('RGB',t.size,(90,110,90));bg.paste(t,mask=t.split()[3]);sh.paste(bg,((k%cols)*cw,((k//cols)*2+j)*ch))
            dr.text(((k%cols)*cw+3,(k//cols)*2*ch+3),'%s%d'%(r,i),fill=(255,255,255))
        sh.save(a.preview);print('preview',a.preview,sh.size)
    if a.apply and new:
        shelf_y=A.size[1]+2;x=0;rowh=0;AW=A.size[0];pos={}
        for k,v in new.items():
            wd,ht=v[0].shape[1],v[0].shape[0]
            if x+wd>AW:x=0;shelf_y+=rowh+2;rowh=0
            pos[k]=(x,shelf_y);x+=wd+2;rowh=max(rowh,ht)
        NA=Image.new('RGBA',(AW,shelf_y+rowh+2),(0,0,0,0));NA.paste(A,(0,0))
        for k,(crop,nq) in new.items():
            NA.alpha_composite(Image.fromarray(crop),pos[k]);r,i=k;nq[0],nq[1]=int(pos[k][0]),int(pos[k][1]);S[r][i]=nq;log.setdefault(a.key,[]).append('%s:%d'%(r,i))
        NA.save(atl_p,'WEBP',quality=85,method=6)
        json.dump(M,open(meta_p,'w'),ensure_ascii=False,separators=(',',':'));json.dump(log,open(LOG,'w'),ensure_ascii=False,indent=1)
        print('applied',len(new),'frames; atlas',NA.size)
if __name__=='__main__':main()

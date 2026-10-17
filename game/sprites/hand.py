# estimate per-frame hand anchor (game coords rel. to feet) for heroes: thin weapon shafts removed by opening, then front-most body point in arm band
import json,numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage as nd
M=json.load(open('sprmeta.json'))
HE=['yuki','kage','mitsu','nobu','shin','musashi','yuki_u','kage_u','mitsu_u','nobu_u','shin_u','musashi_u']
def anchor(img,q):
    x,y,w,h,ox,oy,s=q;a=np.array(img.crop((x,y,x+w,y+h)))[:,:,3]>100
    k=max(3,int(round(9/s)))  # remove structures thinner than ~9 game px
    body=nd.binary_opening(a,structure=np.ones((k,k)))
    lab,n=nd.label(body)
    if n==0:return None
    sizes=nd.sum(body,lab,range(1,n+1));body=lab==(1+int(np.argmax(sizes)))
    # arm band: game y from -150 to -60
    ys=np.arange(h)*s+oy;band=(ys>-150)&(ys<-82)
    best=None
    for r in np.where(band)[0]:
        cols=np.where(body[r])[0]
        if len(cols):
            gx=cols.max()*s+ox
            if best is None or gx>best[0]:best=(gx,ys[r])
    if best is None:return None
    hx,hy=float(best[0])-6,float(best[1])
    thin=a&~nd.binary_dilation(body,iterations=2);lab2,n2=nd.label(thin,structure=np.ones((3,3)));ang=None
    if n2:
        bestc=None
        for i in range(1,n2+1):
            yy,xx=np.where(lab2==i)
            if len(yy)<40/s:continue
            gx=xx*s+ox;gy=yy*s+oy;dd=np.hypot(gx-hx,gy-hy)
            if dd.min()>45:continue
            ext=dd.max()
            if ext<50:continue
            if bestc is None or ext>bestc[0]:j=int(np.argmax(dd));bestc=(ext,float(gx[j]),float(gy[j]))
        if bestc:ang=round(float(np.arctan2(bestc[2]-hy,bestc[1]-hx)),3)
    return [round(hx,1),round(hy,1),ang]
out={}
for h in HE:
    img=Image.open('atlas_%s.png'%h).convert('RGBA');out[h]={}
    for an,fr in M[h].items():
        if not isinstance(fr,list) or not fr or not isinstance(fr[0],list):continue
        L=[anchor(img,q) for q in fr]
        if an in('idle','walk','hit','jump','down','getup','dead'):
            v=[p for p in L if p];md=[float(np.median([p[0] for p in v])),float(np.median([p[1] for p in v])),None] if v else None;L=[md]*len(L)
        out[h][an]=L
json.dump(out,open('hands.json','w'));print(json.dumps(out['yuki'])[:600])

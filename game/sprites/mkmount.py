import numpy as np,json,io,colorsys
from PIL import Image
meta=json.load(open('sprmeta.json'));A=Image.open('atlas_horsearcher.png').convert('RGBA');fr=meta['horsearcher']['idle']
def hsv(a):
    r,g,b=[a[...,i]/255.0 for i in range(3)];mx=np.max(a[...,:3],-1)/255.0;mn=np.min(a[...,:3],-1)/255.0;d=mx-mn+1e-6
    h=np.where(mx==r,((g-b)/d)%6,np.where(mx==g,(b-r)/d+2,(r-g)/d+4))*60;s=np.where(mx>0,d/(mx+1e-6),0);return h,s,mx
out=[]
for q in fr:
    f=np.array(A.crop((q[0],q[1],q[0]+q[2],q[1]+q[3]))).astype(np.float32);H,W=f.shape[:2]
    h,s,v=hsv(f);yy,xx=np.mgrid[0:H,0:W]
    brown=(h>8)&(h<45)&(s>0.3)&(v>0.25)            # horse coat
    dark=(v<0.28)                                   # mane / outlines
    rider=(yy<112)&(xx<200)
    keep_neck=(xx>112)&(yy>68)&(brown|dark)
    kill=rider&~keep_neck
    kill|=(yy<70)&(xx>=140)                         # bow tip
    kill|=(xx>=104)&(xx<=146)&(yy>=60)&(yy<=90)&~((h>8)&(h<40)&(s>0.5)&(v<0.75)&(v>0.3))   # rider's arm over the neck
    f[...,3]=np.where(kill,0,f[...,3])
    out.append(f.astype(np.uint8))
# recolor blue caparison/reins per side
def recolor(f,mode):
    g=f.astype(np.float32);h,s_,v=hsv(g);m=(h>185)&(h<255)&(s_>0.3)&(g[...,3]>0)
    import colorsys
    out=g.copy()
    for y,x in zip(*np.where(m)):
        r,gg,b=g[y,x,:3]/255.0;hh,ss,vv=colorsys.rgb_to_hsv(r,gg,b)
        if mode=='red':hh=0.0;ss=min(1,ss*1.05);vv=min(1,vv*1.05)
        elif mode=='purple':hh=0.78
        elif mode=='iron':ss*=0.15;vv*=0.85
        rr,g2,bb=colorsys.hsv_to_rgb(hh,ss,vv);out[y,x,:3]=[rr*255,g2*255,bb*255]
    return out.astype(np.uint8)
VAR={'red':'red','blue':None,'purple':'purple','iron':'iron'}
meta2={}
for k,mode in VAR.items():
    fs=[recolor(o,mode) if mode else o for o in out]
    W=sum(o.shape[1]+2 for o in fs);H=max(o.shape[0] for o in fs);at=Image.new('RGBA',(W,H));x=0;lst=[]
    for o,q in zip(fs,fr):at.paste(Image.fromarray(o,'RGBA'),(x,0));lst.append([x,0,o.shape[1],o.shape[0],q[4],q[5],1]);x+=o.shape[1]+2
    at.save('atlas_mount_%s.webp'%k,'WEBP',quality=60);at.save('atlas_mount_%s.png'%k);meta['mount_'+k]={'idle':lst,'belly':[-74],'saddle':[-7,-142]}
json.dump(meta,open('sprmeta.json','w'))
pv=Image.new('RGBA',(W*1,H*4),(60,90,60,255))
for i,k in enumerate(VAR):pv.alpha_composite(Image.open('atlas_mount_%s.png'%k),(0,i*H))
pv.save('mount_pv.png')
# save preview
W=sum(o.shape[1]+4 for o in out);H=max(o.shape[0] for o in out);pv=Image.new('RGBA',(W,H),(60,90,60,255));x=0
for o in out:im=Image.fromarray(o,'RGBA');pv.alpha_composite(im,(x,0));x+=o.shape[1]+4

np.save('mount_frames.npy',np.array(out,dtype=object),allow_pickle=True)

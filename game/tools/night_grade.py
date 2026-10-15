# 既存の背景を夜に調色して新しい絵を作る(2026-10-15)。使い方: python3 night_grade.py 元.png 出力.png 月のx,y,半径  (元の絵は上書きしない)
import sys,numpy as np
from PIL import Image,ImageFilter
def smooth(x,a,b):
    t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def night(src,out,moon=None,seed=1):
    im=np.asarray(Image.open(src).convert('RGB')).astype(np.float32)/255
    H,W,_=im.shape;R,G,B=im[...,0],im[...,1],im[...,2]
    V=im.max(-1);L=0.299*R+0.587*G+0.114*B
    # 1) gradient map (night palette) from luminance
    stops=np.array([[0.00,0.02,0.03,0.08],[0.30,0.09,0.11,0.24],[0.55,0.20,0.25,0.44],[0.80,0.40,0.47,0.66],[1.00,0.66,0.74,0.90]],np.float32)
    Lc=np.clip(L*1.05,0,1);cool=np.zeros_like(im)
    for c in range(3):cool[...,c]=np.interp(Lc,stops[:,0],stops[:,c+1])
    # 2) keep original warm light (fire / torches / lamp glow)
    ratio=G/(R+1e-4)
    fire=smooth(ratio,0.33,0.55)*smooth(V,0.62,0.9)*smooth(R-B,0.15,0.4)
    if moon:
        d0=np.sqrt((np.mgrid[0:H,0:W][1]-moon[0])**2+(np.mgrid[0:H,0:W][0]-moon[1])**2);fire=fire*smooth(d0,moon[2]*2.4,moon[2]*3.0)
    fire=np.asarray(Image.fromarray((fire*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.2))).astype(np.float32)/255
    glow=np.asarray(Image.fromarray((fire*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(26))).astype(np.float32)/255
    warm=im*np.array([1.0,0.93,0.82],np.float32)*(0.55+0.45*smooth(V,0.6,1.0))[...,None]
    res=cool*(1-fire[...,None])+warm*fire[...,None]
    # warm halo from light sources (lights the surroundings)
    res=res+glow[...,None]*np.array([0.20,0.09,0.02],np.float32)
    # 3) darken overall slightly and add vignette
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32);vg=1-0.35*(((xx-W/2)/(W/2))**2*0.6+((yy-H/2)/(H/2))**2*0.4)
    res=np.clip(res*vg[...,None]*1.02,0,1)
    out_im=Image.fromarray((res*255).astype(np.uint8))
    # 4) stars + moon in the sky (upper part, only where dark-blue sky)
    rng=np.random.default_rng(seed);arr=np.asarray(out_im).astype(np.float32)
    skym=smooth(1-V*0,0,1)  # placeholder
    sky=(smooth(0.5-yy/H,0.0,0.18))*(1-smooth(L,0.30,0.5))*(1-fire)
    for _ in range(200):
        x=int(rng.integers(0,W));y=int(rng.integers(0,int(H*0.42)));a=float(rng.uniform(0.25,0.85))*sky[y,x]
        r=0 if rng.random()<0.8 else 1
        arr[max(0,y-r):y+r+1,max(0,x-r):x+r+1]=arr[max(0,y-r):y+r+1,max(0,x-r):x+r+1]*(1-a)+np.array([235,240,255],np.float32)*a
    if moon:
        mx,my,mr=moon
        d=np.sqrt((xx-mx)**2+(yy-my)**2)
        halo=np.exp(-(d/(mr*3.2))**2)*0.55
        arr=arr+halo[...,None]*np.array([60,80,120],np.float32)
        disc=smooth(mr-d,-1.5,1.5)
        tex=0.97-0.07*np.exp(-(((xx-mx+0.35*mr)**2+(yy-my-0.1*mr)**2)/(2*(0.28*mr)**2)))-0.05*np.exp(-(((xx-mx-0.3*mr)**2+(yy-my+0.25*mr)**2)/(2*(0.22*mr)**2)))-0.04*(xx-mx)/mr*0.5
        arr=arr*(1-disc[...,None])+disc[...,None]*(np.array([232,236,246],np.float32)*tex[...,None])
    Image.fromarray(np.clip(arr,0,255).astype(np.uint8)).save(out)
if __name__=='__main__':
    src,out=sys.argv[1],sys.argv[2];moon=tuple(map(float,sys.argv[3].split(',')))if len(sys.argv)>3 else None
    night(src,out,moon)

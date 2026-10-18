from PIL import Image
import numpy as np
from pathlib import Path
root=Path(__file__).resolve().parent
repo=root.parents[2]
BG=(255,0,255)
def mask(a): return (a[:,:,0]>130)&(a[:,:,2]>130)&(a[:,:,1]<90)&(np.abs(a[:,:,0].astype(np.int16)-a[:,:,2].astype(np.int16))<55)
for key,srcname,count,cand in [('masamune','伊達政宗_歩き_6コマ_AI仮_v1.png',6,'伊達政宗_歩き_8コマ_AI仮_v1.png'),('munenori','柳生宗矩_歩き_5コマ_AI仮_v1.png',5,'柳生宗矩_歩き_8コマ_AI仮_v1.png')]:
 a=np.asarray(Image.open(repo/'assets'/'sprites'/srcname).convert('RGB')); h,w=a.shape[:2]; cw=w//count
 crops=[a[:,i*cw:(i+1)*cw].copy() for i in range(count)]
 hs=[]
 for t in crops:
  y,x=np.where(~mask(t)); hs.append(y.max()-y.min()+1)
 scale=188/float(np.median(hs))
 current=Image.new('RGB',(512,384),BG)
 t=crops[0]; t[mask(t)]=BG; tile=Image.fromarray(t).resize((round(cw*scale),round(h*scale)),Image.Resampling.LANCZOS)
 y,x=np.where(~mask(np.asarray(crops[0]))); top=363-round((y.max()+1)*scale)
 current.paste(tile,(round(256-tile.width/2),top))
 candim=Image.open(root/cand).convert('RGB').crop((0,0,512,384))
 out=Image.new('RGB',(1024,384),BG); out.paste(current,(0,0));out.paste(candim,(512,0));out.save(root/f'{key}-reference-vs-candidate.png',optimize=True)
 print(key,'reference uniform scale',scale,'reference heights',hs)

"""Normalize generated whole-rider art without replacing any existing PNG."""
import argparse, json, hashlib, runpy
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageSequence

p=argparse.ArgumentParser();p.add_argument('hero');p.add_argument('source');p.add_argument('--cells',type=int,default=5);p.add_argument('--hands',required=True);a=p.parse_args()
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(r'C:/Users/user/Desktop/output/sekigahara-new-20261006')
JP=dict(yuki='真田幸村',kage='上杉景勝',mitsu='石田三成',nobu='織田信長',shin='武田信玄',musashi='宮本武蔵')[a.hero]
qa=OUT/'qa/mounted-body-v3';qa.mkdir(parents=True,exist_ok=True)
raw=np.asarray(Image.open(a.source).convert('RGB'));h,w=raw.shape[:2];pieces=[]
from scipy import ndimage as ndi
fg=~((raw[:,:,0]>180)&(raw[:,:,1]<100)&(raw[:,:,2]>180))
labels,count=ndi.label(fg);sizes=np.bincount(labels.ravel())
main=[int(i) for i in np.where(sizes>10000)[0] if i]
assert len(main)==a.cells,(len(main),a.cells)
main.sort(key=lambda i:np.where(labels==i)[1].mean())
for i,lab in enumerate(main[:5]):
 mask=labels==lab;yy,xx=np.where(mask);l,t,r,b=int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)
 if l<=1 or r>=w-1 or t<=1 or b>=h-1:raise ValueError(('source touches outer edge',i,(l,t,r,b)))
 rgba=np.dstack([raw,np.where(mask,255,0).astype('uint8')]);pieces.append(Image.fromarray(rgba[t:b,l:r]))
scale=min(214/max(im.height for im in pieces),218/max(im.width for im in pieces));frames=[]
for im in pieces:
 im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS)
 f=Image.new('RGB',(256,256),(255,0,255));f.paste(im,((256-im.width)//2,230-im.height),im);frames.append(f)
name=f'馬上素体_{JP}_5コマ_v3.png';dest=ROOT/'assets/sprites'/name
if dest.exists():raise FileExistsError(dest)
strip=Image.new('RGB',(1280,256),(255,0,255))
for i,f in enumerate(frames):strip.paste(f,(i*256,0))
strip.save(dest)
check=runpy.run_path(str(OUT/'30_check_strip.py'))['check_strip'](dest,5,256)
if any(s.startswith('NG') for s in check):raise ValueError(check)
gif=qa/(a.hero+'.gif');frames[0].save(gif,save_all=True,append_images=frames[1:],duration=150,loop=0,disposal=2)
with Image.open(gif) as g:decoded=[f.convert('RGB').copy() for f in ImageSequence.Iterator(g)]
assert len(decoded)==5
contact=Image.new('RGB',(1280,280),(35,35,40));d=ImageDraw.Draw(contact)
for i,f in enumerate(decoded):contact.paste(f,(i*256,0));d.text((i*256+8,260),str(i),fill='white')
contact.save(qa/(a.hero+'-decoded.png'))
hands=json.loads(a.hands);assert len(hands)==5
atlas=strip.convert('RGBA');px=np.asarray(atlas).copy();bg=(px[:,:,0]>180)&(px[:,:,1]<100)&(px[:,:,2]>180);px[bg,3]=0
key='mountbody3_'+a.hero;Image.fromarray(px).save(ROOT/'game/sprites'/('atlas_'+key+'.webp'),'WEBP',lossless=True)
s=1.4;allq=[[i*256,0,256,256,-128*s,-230*s,s] for i in range(5)]
seq=[0,2,3,4,0];meta=dict(all=allq,idle=[allq[0]],walk=[allq[0],allq[1]],attack=[allq[i] for i in seq],handAll=[[(x-128)*s,(y-230)*s] for x,y in hands])
mp=ROOT/'game/sprites/sprmeta.json';m=json.loads(mp.read_text());m[key]=meta;mp.write_text(json.dumps(m,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
record=dict(name=name,source=a.source,sourceCells=a.cells,selectedCells=list(range(5)),checks=check,gifDecodedFrames=5,sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),status='qa_pending',hands=hands)
(qa/(a.hero+'-record.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(record,ensure_ascii=True))

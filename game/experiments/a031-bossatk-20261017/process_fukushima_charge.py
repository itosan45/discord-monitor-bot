from PIL import Image
import numpy as np, hashlib, json
from collections import deque
from pathlib import Path
base=Path('game/experiments/a031-bossatk-20261017')
src=base/'福島正則_体当たり_2x4生成原画.png'
raw=Image.open(src).convert('RGB')
assert raw.size==(1024,1536), raw.size
frames=[]; boxes=[]; edges=[]; removed=[]
magenta=np.array([255,0,255],dtype=np.uint8)
for i in range(8):
 row,col=divmod(i,2)
 a=np.asarray(raw.crop((col*512,row*384,(col+1)*512,(row+1)*384))).copy()
 h,w=a.shape[:2]
 bg=(a[:,:,0]>240)&(a[:,:,2]>240)&(a[:,:,1]<40)
 seen=np.zeros(bg.shape,bool); q=deque()
 for x in range(w):
  for y in (0,h-1):
   if bg[y,x] and not seen[y,x]: seen[y,x]=1; q.append((y,x))
 for y in range(h):
  for x in (0,w-1):
   if bg[y,x] and not seen[y,x]: seen[y,x]=1; q.append((y,x))
 while q:
  y,x=q.popleft()
  for ny,nx in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)):
   if 0<=ny<h and 0<=nx<w and bg[ny,nx] and not seen[ny,nx]: seen[ny,nx]=1;q.append((ny,nx))
 a[seen]=magenta
 mask=np.any(a!=magenta,axis=2); labels=np.zeros(mask.shape,bool); comps=[]
 for y,x in zip(*np.where(mask)):
  if labels[y,x]: continue
  qq=deque([(int(y),int(x))]); labels[y,x]=1; pts=[]
  while qq:
   yy,xx=qq.popleft();pts.append((yy,xx))
   for ny,nx in ((yy-1,xx),(yy+1,xx),(yy,xx-1),(yy,xx+1)):
    if 0<=ny<h and 0<=nx<w and mask[ny,nx] and not labels[ny,nx]:labels[ny,nx]=1;qq.append((ny,nx))
  comps.append(pts)
 drop=0
 for pts in comps:
  if len(pts)<36:
   for y,x in pts:a[y,x]=magenta
   drop+=len(pts)
 removed.append(drop)
 ys,xs=np.where(np.any(a!=magenta,axis=2))
 assert len(xs), i
 crop=Image.fromarray(a[ys.min():ys.max()+1,xs.min():xs.max()+1])
 s=min(220/crop.height,480/crop.width)
 nw=max(1,round(crop.width*s));nh=max(1,round(crop.height*s))
 fg=crop.resize((nw,nh),Image.Resampling.LANCZOS)
 canvas=Image.new('RGB',(512,384),(255,0,255));canvas.paste(fg,((512-nw)//2,363-nh))
 out=np.asarray(canvas); yy,xx=np.where(np.any(out!=magenta,axis=2));boxes.append([int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())])
 edge=np.concatenate((out[0],out[-1],out[:,0],out[:,-1]));edges.append(int(np.count_nonzero(np.any(edge!=magenta,axis=1))))
 frames.append(canvas)
sheet=Image.new('RGB',(4096,384),(255,0,255))
for i,f in enumerate(frames):sheet.paste(f,(i*512,0))
out=base/'福島正則_体当たり_8コマ_v1.png';sheet.save(out,optimize=True)
grid=Image.new('RGB',(1024,1536),(50,50,50))
for i,f in enumerate(frames):grid.paste(f,((i%2)*512,(i//2)*384))
grid.save(base/'福島正則_体当たり_review-grid-v1.png',optimize=True)
frames[0].save(base/'福島正則_体当たり_preview-v1.gif',save_all=True,append_images=frames[1:],duration=140,loop=0,disposal=2)
g=Image.open(base/'福島正則_体当たり_preview-v1.gif');dec=[]
for i in range(g.n_frames):g.seek(i);dec.append(np.asarray(g.convert('RGB')))
unique=len({hashlib.sha256(f.tobytes()).hexdigest() for f in dec})
sha=hashlib.sha256(out.read_bytes()).hexdigest()
qa={'character':'福島正則','asset':out.name,'status':'candidate, not game-integrated','sheet_size':[4096,384],'cell_size':[512,384],'frames':8,'background_rgb':[255,0,255],'groundline_y':363,'foot_anchor_x':256,'frame_foreground_bboxes':boxes,'nonmagenta_outer_edge_pixels_per_cell':edges,'removed_isolated_pixels_per_frame':removed,'decoded_gif_frames':len(dec),'unique_frame_count':unique,'adjacent_changed_pixel_fraction':[round(float(np.mean(np.any(dec[i]!=dec[i+1],axis=2))),4) for i in range(7)],'sha256':sha,'generation':'OpenAI built-in imagegen; AI generated and composed into cells, not hand-drawn. Source derived from original character reference.','notes':'Distinct grounded shoulder charge: guard, crouch, drive steps, charge, shoulder impact, decelerate and reset. Small disconnected specks under 36 pixels removed after boundary-connected magenta key. Candidate only; compare foot anchors and collisions in game before acceptance.'}
(base/'福島正則_体当たり_qa-v1.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
assert len(dec)==8 and unique==8 and not any(edges)
print(json.dumps({'sha256':sha,'boxes':boxes,'edge':edges,'removed':removed,'changed':qa['adjacent_changed_pixel_fraction']},ensure_ascii=False))

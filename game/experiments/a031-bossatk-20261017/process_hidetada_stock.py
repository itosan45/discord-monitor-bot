from PIL import Image
import numpy as np, hashlib, json, os
from collections import deque
src=r'game/experiments/a031-bossatk-20261017/徳川秀忠_銃床打ち_原画.png'; base=r'game/experiments/a031-bossatk-20261017/徳川秀忠_銃床打ち'
raw=Image.open(src).convert('RGB'); print('raw',raw.size); W,H=raw.size
# Six generated poses arranged as four across the upper band and two across the lower band.
boxes=[(0,0,W//4,H//2),(W//4,0,W//2,H//2),(W//2,0,3*W//4,H//2),(3*W//4,0,W,H//2),(0,H//2,W//4,H),(W//4,H//2,W//2,H)]
frames=[]; bboxes=[]; mags=[]; edges=[]; scales=[]
for i,b in enumerate(boxes):
 tile=raw.crop(b); a=np.asarray(tile).copy(); h,w=a.shape[:2]
 near=(a[:,:,0]>165)&(a[:,:,2]>165)&(a[:,:,1]<90)&(np.abs(a[:,:,0].astype(np.int16)-a[:,:,2].astype(np.int16))<85)
 bg=np.zeros((h,w),dtype=bool); q=deque()
 for x in range(w):
  if near[0,x]:bg[0,x]=1;q.append((0,x))
  if near[h-1,x] and not bg[h-1,x]:bg[h-1,x]=1;q.append((h-1,x))
 for y in range(h):
  if near[y,0] and not bg[y,0]:bg[y,0]=1;q.append((y,0))
  if near[y,w-1] and not bg[y,w-1]:bg[y,w-1]=1;q.append((y,w-1))
 while q:
  y,x=q.popleft()
  for ny,nx in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)):
   if 0<=ny<h and 0<=nx<w and near[ny,nx] and not bg[ny,nx]:bg[ny,nx]=1;q.append((ny,nx))
 a[bg]=[255,0,255]; arr=np.asarray(a); ys,xs=np.where(np.any(arr!=[255,0,255],axis=2)); crop=Image.fromarray(arr[min(ys):max(ys)+1,min(xs):max(xs)+1]); scale=188/crop.height; nw=round(crop.width*scale); nh=188; scales.append(scale); fg=crop.resize((nw,nh),Image.Resampling.LANCZOS)
 canvas=Image.new('RGB',(512,384),(255,0,255)); canvas.paste(fg,(256-nw//2,363-nh)); out=np.asarray(canvas); yy,xx=np.where(np.any(out!=[255,0,255],axis=2)); bboxes.append([int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())]); mags.append(int(np.count_nonzero(np.all(out==[255,0,255],axis=2)))); edge=np.concatenate([out[0],out[-1],out[:,0],out[:,-1]]);edges.append(int(np.count_nonzero(np.any(edge!=[255,0,255],axis=1))));frames.append(canvas)
sheet=Image.new('RGB',(3072,384),(255,0,255))
for i,f in enumerate(frames):sheet.paste(f,(i*512,0))
out=base+'_6コマ_v1.png';sheet.save(out,optimize=True)
grid=Image.new('RGB',(1536,768),(50,50,50))
for i,f in enumerate(frames):grid.paste(f,((i%3)*512,(i//3)*384))
grid.save(base+'_review-grid-v1.png',optimize=True)
frames[0].save(base+'_preview-v1.gif',save_all=True,append_images=frames[1:],duration=120,loop=0,disposal=2)
g=Image.open(base+'_preview-v1.gif'); decoded=[]
for i in range(g.n_frames):g.seek(i);decoded.append(np.asarray(g.convert('RGB').copy()))
assert len(decoded)==6 and len({hashlib.sha256(x.tobytes()).hexdigest() for x in decoded})==6 and not any(edges), (len(decoded),edges)
changes=[round(float(np.mean(np.any(decoded[i]!=decoded[i+1],axis=2))),4) for i in range(5)]
qa={'character':'徳川秀忠','asset':os.path.basename(out),'status':'candidate, not game-integrated','sheet_size':[3072,384],'cell_size':[512,384],'frames':6,'background_rgb':[255,0,255],'groundline_y':363,'foot_anchor_x':256,'target_standing_height_px':188,'source_crop_boxes':boxes,'scale_by_frame':scales,'frame_foreground_bboxes':bboxes,'exact_magenta_pixels_per_cell':mags,'nonmagenta_outer_edge_pixels_per_cell':edges,'decoded_gif_frames':len(decoded),'unique_frame_count':6,'adjacent_changed_pixel_fraction':changes,'sha256':hashlib.sha256(open(out,'rb').read()).hexdigest(),'generation':'OpenAI built-in imagegen using Hidetada setting sheet; AI generated and composed/cropped into cells, not hand-drawn.','notes':'Six weapon-specific poses: ready, draw-back anticipation, step/hip rotation, stock impact, compressed recoil, recovery. Tiny impact spark only on the hit; body/gun/foot positions carry the motion. Inspired by fighting-game distinction between startup, active strike, and recovery; not copied from any Samurai Shodown character. Visual/game runtime approval pending.'}
with open(base+'_qa-v1.json','w',encoding='utf-8') as f:json.dump(qa,f,ensure_ascii=False,indent=2)
print(json.dumps({'asset':out,'qa':qa},ensure_ascii=False))

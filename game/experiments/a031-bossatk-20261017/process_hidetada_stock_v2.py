from PIL import Image
import numpy as np, hashlib, json, os
from collections import deque
base='game/experiments/a031-bossatk-20261017/徳川秀忠_銃床打ち'; src=base+'_6コマ_v1.png'; old=np.asarray(Image.open(src).convert('RGB')); frames=[]; boxes=[]; edges=[]; mags=[]
for i in range(6):
 a=old[:,i*512:(i+1)*512].copy(); m=np.any(a!=[255,0,255],axis=2); seen=np.zeros(m.shape,bool); keep=np.zeros(m.shape,bool)
 for y,x in zip(*np.where(m)):
  if seen[y,x]:continue
  q=deque([(int(y),int(x))]);seen[y,x]=1;pts=[]
  while q:
   yy,xx=q.popleft();pts.append((yy,xx))
   for ny,nx in ((yy-1,xx),(yy+1,xx),(yy,xx-1),(yy,xx+1)):
    if 0<=ny<384 and 0<=nx<512 and m[ny,nx] and not seen[ny,nx]:seen[ny,nx]=1;q.append((ny,nx))
  if len(pts)>=1000:
   for yy,xx in pts:keep[yy,xx]=1
 a[~keep]=[255,0,255];ys,xs=np.where(keep);boxes.append([int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())]);mags.append(int(np.count_nonzero(~keep)));e=np.concatenate([keep[0],keep[-1],keep[:,0],keep[:,-1]]);edges.append(int(e.sum()));frames.append(Image.fromarray(a))
sheet=Image.new('RGB',(3072,384),(255,0,255))
for i,f in enumerate(frames):sheet.paste(f,(i*512,0))
out=base+'_6コマ_v2.png';sheet.save(out,optimize=True)
grid=Image.new('RGB',(1536,768),(50,50,50))
for i,f in enumerate(frames):grid.paste(f,((i%3)*512,(i//3)*384))
grid.save(base+'_review-grid-v2.png',optimize=True);frames[0].save(base+'_preview-v2.gif',save_all=True,append_images=frames[1:],duration=120,loop=0,disposal=2)
g=Image.open(base+'_preview-v2.gif');dec=[]
for i in range(g.n_frames):g.seek(i);dec.append(np.asarray(g.convert('RGB').copy()))
assert len(dec)==6 and len({hashlib.sha256(x.tobytes()).hexdigest() for x in dec})==6 and not any(edges)
qa=json.load(open(base+'_qa-v1.json',encoding='utf-8-sig'));qa.update({'asset':os.path.basename(out),'status':'candidate, not game-integrated','sheet_size':[3072,384],'frame_foreground_bboxes':boxes,'isolated_pixels_removed':[int(np.count_nonzero(old[:,i*512:(i+1)*512]!=np.asarray(frames[i]))) for i in range(6)],'nonmagenta_outer_edge_pixels_per_cell':edges,'exact_magenta_pixels_per_cell':mags,'decoded_gif_frames':6,'unique_frame_count':6,'adjacent_changed_pixel_fraction':[round(float(np.mean(np.any(dec[i]!=dec[i+1],axis=2))),4) for i in range(5)],'sha256':hashlib.sha256(open(out,'rb').read()).hexdigest(),'notes':'v2 removes only disconnected source fragments; preserves body poses, matchlock, and impact spark. Visual/gameplay approval pending.'})
with open(base+'_qa-v2.json','w',encoding='utf-8') as f:json.dump(qa,f,ensure_ascii=False,indent=2)
print(json.dumps({'asset':out,'sha256':qa['sha256'],'edges':edges,'changed':qa['adjacent_changed_pixel_fraction']},ensure_ascii=False))


from PIL import Image
import numpy as np,hashlib,json,os
from collections import deque
src=r'game/experiments/a031-bossatk-20261017/本多忠勝_三段突き_2x4原画.png';base=r'game/experiments/a031-bossatk-20261017/本多忠勝_三段突き';raw=Image.open(src).convert('RGB');assert raw.size==(1448,1086),raw.size
frames=[];bboxes=[];scales=[];edges=[];swh=724;sht=271
for i in range(8):
 row,col=divmod(i,2);a=np.asarray(raw.crop((col*swh,row*sht,(col+1)*swh,(row+1)*sht))).copy();h,w=a.shape[:2]
 bg=(a[:,:,0]>240)&(a[:,:,2]>240)&(a[:,:,1]<40);seen=np.zeros(bg.shape,bool);q=deque()
 for x in range(w):
  for y in (0,h-1):
   if bg[y,x] and not seen[y,x]:seen[y,x]=1;q.append((y,x))
 for y in range(h):
  for x in (0,w-1):
   if bg[y,x] and not seen[y,x]:seen[y,x]=1;q.append((y,x))
 while q:
  y,x=q.popleft()
  for ny,nx in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)):
   if 0<=ny<h and 0<=nx<w and bg[ny,nx] and not seen[ny,nx]:seen[ny,nx]=1;q.append((ny,nx))
 a[seen]=[255,0,255];m=np.any(a!=[255,0,255],axis=2);seen2=np.zeros(m.shape,bool);components=[]
 for yy,xx in zip(*np.where(m)):
  if seen2[yy,xx]:continue
  qq=deque([(int(yy),int(xx))]);seen2[yy,xx]=1;pts=[]
  while qq:
   y2,x2=qq.popleft();pts.append((y2,x2))
   for y3,x3 in ((y2-1,x2),(y2+1,x2),(y2,x2-1),(y2,x2+1)):
    if 0<=y3<h and 0<=x3<w and m[y3,x3] and not seen2[y3,x3]:seen2[y3,x3]=1;qq.append((y3,x3))
  components.append(pts)
 main=max(components,key=len);keep=np.zeros(m.shape,bool)
 for y2,x2 in main:keep[y2,x2]=1
 a[~keep]=[255,0,255];m=keep;ys,xs=np.where(m);crop=Image.fromarray(a[min(ys):max(ys)+1,min(xs):max(xs)+1]);s=min(188/crop.height,480/crop.width);scales.append(s);nw=max(1,round(crop.width*s));nh=max(1,round(crop.height*s));fg=crop.resize((nw,nh),Image.Resampling.LANCZOS);canvas=Image.new('RGB',(512,384),(255,0,255));canvas.paste(fg,((512-nw)//2,363-nh));out=np.asarray(canvas);yy,xx=np.where(np.any(out!=[255,0,255],axis=2));bboxes.append([int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())]);e=np.concatenate([out[0],out[-1],out[:,0],out[:,-1]]);edges.append(int(np.count_nonzero(np.any(e!=[255,0,255],axis=1))));frames.append(canvas)
sheet=Image.new('RGB',(4096,384),(255,0,255))
for i,f in enumerate(frames):sheet.paste(f,(i*512,0))
out=base+'_8コマ_v2.png';sheet.save(out,optimize=True);grid=Image.new('RGB',(1024,1536),(50,50,50))
for i,f in enumerate(frames):grid.paste(f,((i%2)*512,(i//2)*384))
grid.save(base+'_review-grid-v2.png',optimize=True);frames[0].save(base+'_preview-v2.gif',save_all=True,append_images=frames[1:],duration=130,loop=0,disposal=2);g=Image.open(base+'_preview-v2.gif');dec=[]
for i in range(g.n_frames):g.seek(i);dec.append(np.asarray(g.convert('RGB').copy()))
assert len(dec)==8 and len({hashlib.sha256(x.tobytes()).hexdigest() for x in dec})==8 and not any(edges),(len(dec),edges)
qa={'character':'本多忠勝','asset':os.path.basename(out),'status':'candidate, not game-integrated','sheet_size':[4096,384],'cell_size':[512,384],'frames':8,'background_rgb':[255,0,255],'groundline_y':363,'foot_anchor_x':256,'source_grid':[2,4],'source_cell_size':[724,271],'scale_by_frame':scales,'frame_foreground_bboxes':bboxes,'nonmagenta_outer_edge_pixels_per_cell':edges,'decoded_gif_frames':8,'unique_frame_count':8,'adjacent_changed_pixel_fraction':[round(float(np.mean(np.any(dec[i]!=dec[i+1],axis=2))),4) for i in range(7)],'sha256':hashlib.sha256(open(out,'rb').read()).hexdigest(),'generation':'OpenAI built-in imagegen using Honda Tadakatsu setting sheet; AI generated/composed into cells, not hand-drawn.','notes':'v2 retains the largest character+weapon component per cell, removing detached cross-row spear/head fragments. Three thrusts separated by distinct reload/retract phases: ready, load, chest thrust, retract, low thrust, reset, decisive high thrust, guard. Candidate; gameplay timing/hit boxes pending.'}
with open(base+'_qa-v2.json','w',encoding='utf-8') as f:json.dump(qa,f,ensure_ascii=False,indent=2)
print(json.dumps({'sha':qa['sha256'],'boxes':bboxes,'scales':scales,'edges':edges,'changes':qa['adjacent_changed_pixel_fraction']},ensure_ascii=False))

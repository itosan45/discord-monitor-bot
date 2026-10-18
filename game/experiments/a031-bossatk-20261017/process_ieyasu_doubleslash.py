from PIL import Image
import numpy as np, hashlib, json, os
from collections import deque
src=r'game/experiments/a031-bossatk-20261017/徳川家康_二段斬り_2x4原画.png';base=r'game/experiments/a031-bossatk-20261017/徳川家康_二段斬り';raw=Image.open(src).convert('RGB');assert raw.size==(1536,1024),raw.size
frames=[];boxes=[];scales=[];edges=[];mags=[];source_boxes=[]
for i in range(8):
 row,col=divmod(i,2);b=(col*768,row*256,(col+1)*768,(row+1)*256);source_boxes.append(b);tile=raw.crop(b);a=np.asarray(tile).copy();h,w=a.shape[:2]
 near=(a[:,:,0]>165)&(a[:,:,2]>165)&(a[:,:,1]<90)&(np.abs(a[:,:,0].astype(np.int16)-a[:,:,2].astype(np.int16))<85);bg=np.zeros((h,w),bool);q=deque()
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
 a[bg]=[255,0,255];arr=np.asarray(a);ys,xs=np.where(np.any(arr!=[255,0,255],axis=2));crop=Image.fromarray(arr[min(ys):max(ys)+1,min(xs):max(xs)+1]);s=min(188/crop.height,468/crop.width);nw=max(1,round(crop.width*s));nh=max(1,round(crop.height*s));scales.append(s);fg=crop.resize((nw,nh),Image.Resampling.LANCZOS);canvas=Image.new('RGB',(512,384),(255,0,255));canvas.paste(fg,((512-nw)//2,363-nh));out=np.asarray(canvas);yy,xx=np.where(np.any(out!=[255,0,255],axis=2));boxes.append([int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())]);e=np.concatenate([out[0],out[-1],out[:,0],out[:,-1]]);edges.append(int(np.count_nonzero(np.any(e!=[255,0,255],axis=1))));mags.append(int(np.count_nonzero(np.all(out==[255,0,255],axis=2))));frames.append(canvas)
sheet=Image.new('RGB',(4096,384),(255,0,255))
for i,f in enumerate(frames):sheet.paste(f,(i*512,0))
outpath=base+'_8コマ_v1.png';sheet.save(outpath,optimize=True);grid=Image.new('RGB',(1024,1536),(50,50,50))
for i,f in enumerate(frames):grid.paste(f,((i%2)*512,(i//2)*384))
grid.save(base+'_review-grid-v1.png',optimize=True);frames[0].save(base+'_preview-v1.gif',save_all=True,append_images=frames[1:],duration=130,loop=0,disposal=2);g=Image.open(base+'_preview-v1.gif');dec=[]
for i in range(g.n_frames):g.seek(i);dec.append(np.asarray(g.convert('RGB').copy()))
assert len(dec)==8 and len({hashlib.sha256(a.tobytes()).hexdigest() for a in dec})==8 and not any(edges),(len(dec),edges)
qa={'character':'徳川家康（影武者）','asset':os.path.basename(outpath),'status':'candidate, not game-integrated','sheet_size':[4096,384],'cell_size':[512,384],'frames':8,'background_rgb':[255,0,255],'groundline_y':363,'foot_anchor_x':256,'source_crop_boxes':source_boxes,'scale_by_frame':scales,'frame_foreground_bboxes':boxes,'exact_magenta_pixels_per_cell':mags,'nonmagenta_outer_edge_pixels_per_cell':edges,'decoded_gif_frames':8,'unique_frame_count':8,'adjacent_changed_pixel_fraction':[round(float(np.mean(np.any(dec[i]!=dec[i+1],axis=2))),4) for i in range(7)],'sha256':hashlib.sha256(open(outpath,'rb').read()).hexdigest(),'generation':'OpenAI built-in imagegen using Ieyasu shadow setting sheet; AI generated and composed into cells, not hand-drawn.','notes':'Two-part double slash: low ready, overhead load, first diagonal cut and follow-through, reverse-side load, opposite return cut, full extension, recovery guard. Slash marks are secondary to changing torso, foot and katana positions. Candidate; gameplay review pending.'}
with open(base+'_qa-v1.json','w',encoding='utf-8') as f:json.dump(qa,f,ensure_ascii=False,indent=2)
print(json.dumps({'sha256':qa['sha256'],'boxes':boxes,'scales':scales,'edges':edges,'changes':qa['adjacent_changed_pixel_fraction']},ensure_ascii=False))

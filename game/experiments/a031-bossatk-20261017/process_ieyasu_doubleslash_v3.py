from PIL import Image
import numpy as np,hashlib,json,os
from collections import deque
src=r'game/experiments/a031-bossatk-20261017/徳川家康_二段斬り_2x4原画_v2.png';base=r'game/experiments/a031-bossatk-20261017/徳川家康_二段斬り';raw=Image.open(src).convert('RGB');frames=[];boxes=[];edges=[];scales=[]
for i in range(8):
 row,col=divmod(i,2);a=np.asarray(raw.crop((col*768,row*256,(col+1)*768,(row+1)*256))).copy();h,w=a.shape[:2]
 # Narrow threshold to key magenta only; protects purple garments from broad hue deletion.
 bg=(a[:,:,0]>240)&(a[:,:,2]>240)&(a[:,:,1]<40);seen=np.zeros(bg.shape,bool);q=deque()
 for x in range(w):
  if bg[0,x]:seen[0,x]=1;q.append((0,x))
  if bg[h-1,x] and not seen[h-1,x]:seen[h-1,x]=1;q.append((h-1,x))
 for y in range(h):
  if bg[y,0] and not seen[y,0]:seen[y,0]=1;q.append((y,0))
  if bg[y,w-1] and not seen[y,w-1]:seen[y,w-1]=1;q.append((y,w-1))
 while q:
  y,x=q.popleft()
  for ny,nx in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)):
   if 0<=ny<h and 0<=nx<w and bg[ny,nx] and not seen[ny,nx]:seen[ny,nx]=1;q.append((ny,nx))
 a[seen]=[255,0,255];m=np.any(a!=[255,0,255],axis=2);ys,xs=np.where(m);crop=Image.fromarray(a[min(ys):max(ys)+1,min(xs):max(xs)+1]);s=min(188/crop.height,480/crop.width);scales.append(s);nw=max(1,round(crop.width*s));nh=max(1,round(crop.height*s));fg=crop.resize((nw,nh),Image.Resampling.LANCZOS);canvas=Image.new('RGB',(512,384),(255,0,255));canvas.paste(fg,((512-nw)//2,363-nh));out=np.asarray(canvas);yy,xx=np.where(np.any(out!=[255,0,255],axis=2));boxes.append([int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())]);e=np.concatenate([out[0],out[-1],out[:,0],out[:,-1]]);edges.append(int(np.count_nonzero(np.any(e!=[255,0,255],axis=1))));frames.append(canvas)
sheet=Image.new('RGB',(4096,384),(255,0,255))
for i,f in enumerate(frames):sheet.paste(f,(i*512,0))
out=base+'_8コマ_v3.png';sheet.save(out,optimize=True);grid=Image.new('RGB',(1024,1536),(50,50,50))
for i,f in enumerate(frames):grid.paste(f,((i%2)*512,(i//2)*384))
grid.save(base+'_review-grid-v3.png',optimize=True);frames[0].save(base+'_preview-v3.gif',save_all=True,append_images=frames[1:],duration=130,loop=0,disposal=2);g=Image.open(base+'_preview-v3.gif');dec=[]
for i in range(g.n_frames):g.seek(i);dec.append(np.asarray(g.convert('RGB').copy()))
assert len(dec)==8 and len({hashlib.sha256(x.tobytes()).hexdigest() for x in dec})==8 and not any(edges)
qa={'character':'徳川家康（影武者）','asset':os.path.basename(out),'status':'candidate, not game-integrated','sheet_size':[4096,384],'cell_size':[512,384],'frames':8,'background_rgb':[255,0,255],'groundline_y':363,'foot_anchor_x':256,'source_grid':[2,4],'source_crop_boxes':'8 cells of 768x256','background_key':'border-connected magenta r>240,b>240,g<40 to preserve purple cloth','scale_by_frame':scales,'frame_foreground_bboxes':boxes,'nonmagenta_outer_edge_pixels_per_cell':edges,'decoded_gif_frames':8,'unique_frame_count':8,'adjacent_changed_pixel_fraction':[round(float(np.mean(np.any(dec[i]!=dec[i+1],axis=2))),4) for i in range(7)],'sha256':hashlib.sha256(open(out,'rb').read()).hexdigest(),'generation':'OpenAI built-in imagegen using Ieyasu shadow setting; AI generated and composed into cells, not hand-drawn. v3 uses narrow magenta key.','notes':'Eight deliberate double-slash phases, from guard/load through two distinct cuts and recovery. v1/v2 retained as failed crop/segmentation trials; v3 visually reviewed. Candidate; game/runtime approval pending.'}
with open(base+'_qa-v3.json','w',encoding='utf-8') as f:json.dump(qa,f,ensure_ascii=False,indent=2)
print(json.dumps({'sha':qa['sha256'],'bboxes':boxes,'edges':edges,'scales':scales,'changes':qa['adjacent_changed_pixel_fraction']},ensure_ascii=False))

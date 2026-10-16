from PIL import Image
import numpy as np,hashlib,json,os
from collections import deque
src=r'game/experiments/a031-bossatk-20261017/小早川秀秋_背後斬り_2x4原画.png';base=r'game/experiments/a031-bossatk-20261017/小早川秀秋_背後斬り';raw=Image.open(src).convert('RGB');assert raw.size==(1024,1536),raw.size
frames=[];boxes=[];scales=[];edges=[];sizes=[]
for i in range(8):
 row,col=divmod(i,2);a=np.asarray(raw.crop((col*512,row*384,(col+1)*512,(row+1)*384))).copy();h,w=a.shape[:2]
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
 a[seen]=[255,0,255];m=np.any(a!=[255,0,255],axis=2);ys,xs=np.where(m);crop=Image.fromarray(a[min(ys):max(ys)+1,min(xs):max(xs)+1]);s=min(188/crop.height,470/crop.width);scales.append(s);nw=max(1,round(crop.width*s));nh=max(1,round(crop.height*s));fg=crop.resize((nw,nh),Image.Resampling.LANCZOS);canvas=Image.new('RGB',(512,384),(255,0,255));canvas.paste(fg,((512-nw)//2,363-nh));out=np.asarray(canvas);yy,xx=np.where(np.any(out!=[255,0,255],axis=2));boxes.append([int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())]);e=np.concatenate([out[0],out[-1],out[:,0],out[:,-1]]);edges.append(int(np.count_nonzero(np.any(e!=[255,0,255],axis=1))));frames.append(canvas)
sheet=Image.new('RGB',(4096,384),(255,0,255))
for i,f in enumerate(frames):sheet.paste(f,(i*512,0))
out=base+'_8コマ_v1.png';sheet.save(out,optimize=True);grid=Image.new('RGB',(1024,1536),(50,50,50))
for i,f in enumerate(frames):grid.paste(f,((i%2)*512,(i//2)*384))
grid.save(base+'_review-grid-v1.png',optimize=True);frames[0].save(base+'_preview-v1.gif',save_all=True,append_images=frames[1:],duration=130,loop=0,disposal=2);g=Image.open(base+'_preview-v1.gif');dec=[]
for i in range(g.n_frames):g.seek(i);dec.append(np.asarray(g.convert('RGB').copy()))
assert len(dec)==8 and len({hashlib.sha256(x.tobytes()).hexdigest() for x in dec})==8 and not any(edges),(len(dec),edges)
qa={'character':'小早川秀秋','asset':os.path.basename(out),'status':'candidate, not game-integrated','sheet_size':[4096,384],'cell_size':[512,384],'frames':8,'background_rgb':[255,0,255],'groundline_y':363,'foot_anchor_x':256,'source_grid':[2,4],'scale_by_frame':scales,'frame_foreground_bboxes':boxes,'nonmagenta_outer_edge_pixels_per_cell':edges,'decoded_gif_frames':8,'unique_frame_count':8,'adjacent_changed_pixel_fraction':[round(float(np.mean(np.any(dec[i]!=dec[i+1],axis=2))),4) for i in range(7)],'sha256':hashlib.sha256(open(out,'rb').read()).hexdigest(),'generation':'OpenAI built-in imagegen using Kobayakawa setting sheet; AI generated/composed into cells, not hand-drawn.','notes':'Rear-position ambush cut: compact low start, forward dash, low arrival, reverse-grip rise, diagonal cut, follow-through, recoil, guard. This is not the Samurai Shodown move/cell art; reference was the broad teleport-then-strike structure. Candidate and game assignment pending.'}
with open(base+'_qa-v1.json','w',encoding='utf-8') as f:json.dump(qa,f,ensure_ascii=False,indent=2)
print(json.dumps({'sha':qa['sha256'],'boxes':boxes,'edges':edges,'changes':qa['adjacent_changed_pixel_fraction']},ensure_ascii=False))

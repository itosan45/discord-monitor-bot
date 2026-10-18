from PIL import Image
import numpy as np,hashlib,json,os
from collections import deque
src=r'game/experiments/a031-bossatk-20261017/徳川家康_二段斬り_2x4原画_v2.png';base=r'game/experiments/a031-bossatk-20261017/徳川家康_二段斬り_v1';raw=Image.open(src).convert('RGB');assert raw.size==(1536,1024)
frames=[];bboxes=[];edges=[];mag=[];sizes=[];scales=[]
for i in range(8):
 row,col=divmod(i,2);a=np.asarray(raw.crop((col*768,row*256,(col+1)*768,(row+1)*256))).copy();h,w=a.shape[:2]
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
 a[bg]=[255,0,255];m=np.any(a!=[255,0,255],axis=2);seen=np.zeros(m.shape,bool);comps=[]
 for y,x in zip(*np.where(m)):
  if seen[y,x]:continue
  q=deque([(int(y),int(x))]);seen[y,x]=1;pts=[]
  while q:
   yy,xx=q.popleft();pts.append((yy,xx))
   for ny,nx in ((yy-1,xx),(yy+1,xx),(yy,nx-1),(yy,nx+1)):
    if 0<=ny<h and 0<=nx<w and m[ny,nx] and not seen[ny,nx]:seen[ny,nx]=1;q.append((ny,nx))
  comps.append(pts)
 main=max(comps,key=len);sizes.append([len(c) for c in sorted(comps,key=len,reverse=True)[:4]]);keep=np.zeros(m.shape,bool)
 for yy,xx in main:keep[yy,xx]=True
 ys,xs=np.where(keep);crop=Image.fromarray(a[min(ys):max(ys)+1,min(xs):max(xs)+1]);s=min(188/crop.height,480/crop.width);scales.append(s);nw=max(1,round(crop.width*s));nh=max(1,round(crop.height*s));fg=crop.resize((nw,nh),Image.Resampling.LANCZOS);canvas=Image.new('RGB',(512,384),(255,0,255));canvas.paste(fg,((512-nw)//2,363-nh));out=np.asarray(canvas);yy,xx=np.where(np.any(out!=[255,0,255],axis=2));bboxes.append([int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())]);e=np.concatenate([out[0],out[-1],out[:,0],out[:,-1]]);edges.append(int(np.count_nonzero(np.any(e!=[255,0,255],axis=1))));mag.append(int(np.count_nonzero(np.all(out==[255,0,255],axis=2))));frames.append(canvas)
sheet=Image.new('RGB',(4096,384),(255,0,255))
for i,f in enumerate(frames):sheet.paste(f,(i*512,0))
out=base+'_8コマ_v1.png';sheet.save(out,optimize=True);grid=Image.new('RGB',(1024,1536),(50,50,50))
for i,f in enumerate(frames):grid.paste(f,((i%2)*512,(i//2)*384))
grid.save(base+'_review-grid-v1.png',optimize=True);frames[0].save(base+'_preview-v1.gif',save_all=True,append_images=frames[1:],duration=130,loop=0,disposal=2);g=Image.open(base+'_preview-v1.gif');dec=[]
for i in range(g.n_frames):g.seek(i);dec.append(np.asarray(g.convert('RGB').copy()))
assert len(dec)==8 and len({hashlib.sha256(x.tobytes()).hexdigest() for x in dec})==8 and not any(edges),(len(dec),edges)
qa={'character':'徳川家康（影武者）','asset':os.path.basename(out),'status':'candidate, not game-integrated','sheet_size':[4096,384],'cell_size':[512,384],'frames':8,'background_rgb':[255,0,255],'groundline_y':363,'foot_anchor_x':256,'source_grid':[2,4],'main_component_area_per_frame':[x[0] for x in sizes],'source_crop_boxes':'8 cells of 768x256','scale_by_frame':scales,'frame_foreground_bboxes':bboxes,'exact_magenta_pixels_per_cell':mag,'nonmagenta_outer_edge_pixels_per_cell':edges,'decoded_gif_frames':8,'unique_frame_count':8,'adjacent_changed_pixel_fraction':[round(float(np.mean(np.any(dec[i]!=dec[i+1],axis=2))),4) for i in range(7)],'sha256':hashlib.sha256(open(out,'rb').read()).hexdigest(),'generation':'OpenAI built-in imagegen; reference: Ieyasu shadow setting. AI generated and composed into cells, not hand-drawn. Retained main pose component to exclude row-overlap fragments.','notes':'Second attempt after v1 crop cut row-overlap fragments. Eight pose phases: ready, load, first slash, follow-through, reverse load, rising return cut, extension, recovery. Motion and sword path differ across frames; candidate, game review pending.'}
with open(base+'_qa-v1.json','w',encoding='utf-8') as f:json.dump(qa,f,ensure_ascii=False,indent=2)
print(json.dumps({'sha':qa['sha256'],'bboxes':bboxes,'edges':edges,'areas':sizes,'changes':qa['adjacent_changed_pixel_fraction']},ensure_ascii=False))

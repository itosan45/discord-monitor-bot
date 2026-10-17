from PIL import Image
import numpy as np,hashlib,json,os
from collections import deque
src=r'game/experiments/a031-bossatk-20261017/黒田長政_斬り上げ_原画.png';base=r'game/experiments/a031-bossatk-20261017/黒田長政_斬り上げ';raw=Image.open(src).convert('RGB');assert raw.size==(1536,1024)
boxes=[(0,0,384,512),(384,0,768,512),(768,0,1152,512),(1152,0,1536,512),(0,512,768,1024),(768,512,1536,1024)];frames=[];bboxes=[];scales=[];edges=[]
for b in boxes:
 a=np.asarray(raw.crop(b)).copy();h,w=a.shape[:2];bg=(a[:,:,0]>240)&(a[:,:,2]>240)&(a[:,:,1]<40);seen=np.zeros(bg.shape,bool);q=deque()
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
 a[seen]=[255,0,255];m=np.any(a!=[255,0,255],axis=2);ys,xs=np.where(m);crop=Image.fromarray(a[min(ys):max(ys)+1,min(xs):max(xs)+1]);s=min(188/crop.height,480/crop.width);scales.append(s);nw=max(1,round(crop.width*s));nh=max(1,round(crop.height*s));fg=crop.resize((nw,nh),Image.Resampling.LANCZOS);canvas=Image.new('RGB',(512,384),(255,0,255));canvas.paste(fg,((512-nw)//2,363-nh));out=np.asarray(canvas);yy,xx=np.where(np.any(out!=[255,0,255],axis=2));bboxes.append([int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())]);e=np.concatenate([out[0],out[-1],out[:,0],out[:,-1]]);edges.append(int(np.count_nonzero(np.any(e!=[255,0,255],axis=1))));frames.append(canvas)
sheet=Image.new('RGB',(3072,384),(255,0,255))
for i,f in enumerate(frames):sheet.paste(f,(i*512,0))
out=base+'_6コマ_v2.png';sheet.save(out,optimize=True);grid=Image.new('RGB',(1536,768),(50,50,50))
for i,f in enumerate(frames):grid.paste(f,((i%3)*512,(i//3)*384))
grid.save(base+'_review-grid-v2.png',optimize=True);frames[0].save(base+'_preview-v2.gif',save_all=True,append_images=frames[1:],duration=130,loop=0,disposal=2);g=Image.open(base+'_preview-v2.gif');dec=[]
for i in range(g.n_frames):g.seek(i);dec.append(np.asarray(g.convert('RGB').copy()))
assert len(dec)==6 and len({hashlib.sha256(x.tobytes()).hexdigest() for x in dec})==6 and not any(edges)
qa={'character':'黒田長政','asset':os.path.basename(out),'status':'candidate, not game-integrated','sheet_size':[3072,384],'cell_size':[512,384],'frames':6,'background_rgb':[255,0,255],'groundline_y':363,'foot_anchor_x':256,'source_crop_boxes':boxes,'scale_by_frame':scales,'frame_foreground_bboxes':bboxes,'nonmagenta_outer_edge_pixels_per_cell':edges,'decoded_gif_frames':6,'unique_frame_count':6,'adjacent_changed_pixel_fraction':[round(float(np.mean(np.any(dec[i]!=dec[i+1],axis=2))),4) for i in range(5)],'sha256':hashlib.sha256(open(out,'rb').read()).hexdigest(),'generation':'OpenAI built-in imagegen using Kuroda setting; AI generated/composed into cells, not hand-drawn. v2 preserves all foreground components to avoid deleting thin sword details.','notes':'Six visibly distinct poses of two-sword rising launcher. v1 was an overly aggressive component-filter experiment and is not used. Candidate; gameplay review pending.'}
with open(base+'_qa-v2.json','w',encoding='utf-8') as f:json.dump(qa,f,ensure_ascii=False,indent=2)
print(json.dumps({'sha':qa['sha256'],'boxes':bboxes,'edges':edges,'changes':qa['adjacent_changed_pixel_fraction']},ensure_ascii=False))

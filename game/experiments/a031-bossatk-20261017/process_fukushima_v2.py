from PIL import Image
import numpy as np, hashlib, json, os
from collections import deque
base='game/experiments/a031-bossatk-20261017/福島正則_跳び込み攻撃'
inpath=base+'_8コマ_v1.png'; sheet=np.asarray(Image.open(inpath).convert('RGB')).copy(); old_sheet=sheet.copy(); frames=[]; bboxes=[]; mag=[]; edges=[]; changed=[]
for i in range(8):
 a=sheet[:,i*512:(i+1)*512].copy(); mask=np.any(a!=[255,0,255],axis=2); seen=np.zeros(mask.shape,bool); components=[]
 for y,x in zip(*np.where(mask)):
  if seen[y,x]: continue
  q=deque([(int(y),int(x))]); seen[y,x]=1; pts=[]
  while q:
   yy,xx=q.popleft(); pts.append((yy,xx))
   for ny,nx in ((yy-1,xx),(yy+1,xx),(yy,xx-1),(yy,xx+1)):
    if 0<=ny<384 and 0<=nx<512 and mask[ny,nx] and not seen[ny,nx]: seen[ny,nx]=1;q.append((ny,nx))
  if len(pts)>=1000: components.extend(pts)
 clean=np.full_like(a,[255,0,255]);
 for y,x in components: clean[y,x]=a[y,x]
 ys,xs=np.where(np.any(clean!=[255,0,255],axis=2)); bboxes.append([int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())]); mag.append(int(np.count_nonzero(np.all(clean==[255,0,255],axis=2))))
 e=np.concatenate([clean[0],clean[-1],clean[:,0],clean[:,-1]]); edges.append(int(np.count_nonzero(np.any(e!=[255,0,255],axis=1)))); frames.append(Image.fromarray(clean))
 if i<7: changed.append(round(float(np.mean(np.any(np.asarray(frames[-1])!=old_sheet[:,(i+1)*512:(i+2)*512],axis=2))),4))
out=Image.new('RGB',(4096,384),(255,0,255))
for i,f in enumerate(frames):out.paste(f,(i*512,0))
outpath=base+'_8コマ_v2.png';out.save(outpath,optimize=True)
grid=Image.new('RGB',(1024,1536),(50,50,50))
for i,f in enumerate(frames):grid.paste(f,((i%2)*512,(i//2)*384))
grid.save(base+'_review-grid-v2.png',optimize=True)
frames[0].save(base+'_preview-v2.gif',save_all=True,append_images=frames[1:],duration=150,loop=0,disposal=2)
g=Image.open(base+'_preview-v2.gif');dec=[]
for i in range(g.n_frames):g.seek(i);dec.append(np.asarray(g.convert('RGB').copy()))
assert len(dec)==8 and len({hashlib.sha256(x.tobytes()).hexdigest() for x in dec})==8 and not any(edges)
changes=[round(float(np.mean(np.any(dec[i]!=dec[i+1],axis=2))),4) for i in range(7)]
sha=hashlib.sha256(open(outpath,'rb').read()).hexdigest()
qa={'character':'福島正則','asset':os.path.basename(outpath),'status':'candidate, not game-integrated','sheet_size':[4096,384],'cell_size':[512,384],'frames':8,'background_rgb':[255,0,255],'groundline_y':363,'foot_anchor_x':256,'frame_foreground_bboxes':bboxes,'exact_magenta_pixels_per_cell':mag,'nonmagenta_outer_edge_pixels_per_cell':edges,'decoded_gif_frames':len(dec),'unique_frame_count':8,'adjacent_changed_pixel_fraction':changes,'sha256':sha,'generation':'OpenAI built-in imagegen; AI generated and composed into cells, not hand-drawn. v2 removes disconnected fragments under 1000 pixels per cell while retaining connected impact dust.','notes':'Right-facing fierce naginata boss. Eight poses: launch, leap, overhead wind-up, descending two-hand grip, ground-breaking naginata slam, aftershock, lift and recover, guard. v1 retained for comparison; v2 keeps the main pose/connected impact while removing isolated cross-cell fragments. Visual/gameplay approval pending.'}
with open(base+'_qa-v2.json','w',encoding='utf-8') as f:json.dump(qa,f,ensure_ascii=False,indent=2)
print(json.dumps({'sha256':sha,'boxes':bboxes,'outer_edge':edges,'changed':changes},ensure_ascii=False))


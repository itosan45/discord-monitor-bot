from PIL import Image
import numpy as np, hashlib, json, os
from collections import deque
src=r'game/experiments/a031-bossatk-20261017/福島正則_跳び込み攻撃_2x4生成原画.png'
outdir=r'game/experiments/a031-bossatk-20261017'
name='福島正則_跳び込み攻撃'
raw=Image.open(src).convert('RGB'); assert raw.size==(1024,1536), raw.size
frames=[]; bboxes=[]; exact=[]; scale=.55
# Launch and impact/recovery are grounded; frames 2-4 are airborne/descent.
offsets=[151,76,76,111,147,147,152,152]
for i in range(8):
 row,col=divmod(i,2); tile=raw.crop((col*512,row*384,(col+1)*512,(row+1)*384)); a=np.asarray(tile).copy()
 near=(a[:,:,0]>165)&(a[:,:,2]>165)&(a[:,:,1]<90)&(np.abs(a[:,:,0].astype(np.int16)-a[:,:,2].astype(np.int16))<85)
 bg=np.zeros((384,512),dtype=bool); q=deque()
 for x in range(512):
  if near[0,x]: bg[0,x]=1;q.append((0,x))
  if near[383,x] and not bg[383,x]: bg[383,x]=1;q.append((383,x))
 for y in range(384):
  if near[y,0] and not bg[y,0]: bg[y,0]=1;q.append((y,0))
  if near[y,511] and not bg[y,511]: bg[y,511]=1;q.append((y,511))
 while q:
  y,x=q.popleft()
  for ny,nx in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)):
   if 0<=ny<384 and 0<=nx<512 and near[ny,nx] and not bg[ny,nx]: bg[ny,nx]=1;q.append((ny,nx))
 a[bg]=[255,0,255]; tile=Image.fromarray(a).resize((282,211),Image.Resampling.LANCZOS)
 canvas=Image.new('RGB',(512,384),(255,0,255)); canvas.paste(tile,(115,round(offsets[i])))
 arr=np.asarray(canvas); ys,xs=np.where(np.any(arr!=[255,0,255],axis=2)); bboxes.append([int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())]); exact.append(int(np.count_nonzero(np.all(arr==[255,0,255],axis=2)))); frames.append(canvas)
sheet=Image.new('RGB',(4096,384),(255,0,255))
for i,f in enumerate(frames): sheet.paste(f,(i*512,0))
path=os.path.join(outdir,name+'_8コマ_v1.png'); sheet.save(path,optimize=True)
grid=Image.new('RGB',(1024,1536),(50,50,50))
for i,f in enumerate(frames): grid.paste(f,((i%2)*512,(i//2)*384))
grid.save(os.path.join(outdir,name+'_review-grid-v1.png'),optimize=True)
frames[0].save(os.path.join(outdir,name+'_preview-v1.gif'),save_all=True,append_images=frames[1:],duration=150,loop=0,disposal=2)
check=Image.open(path); gif=Image.open(os.path.join(outdir,name+'_preview-v1.gif')); decoded=[]
assert check.size==(4096,384)
for i in range(gif.n_frames): gif.seek(i); decoded.append(gif.convert('RGB').copy())
assert len(decoded)==8
edge=[]; changed=[]
for i in range(8):
 ar=np.asarray(check.crop((i*512,0,(i+1)*512,384))); e=np.concatenate([ar[0],ar[-1],ar[:,0],ar[:,-1]])
 edge.append(int(np.count_nonzero(np.any(e!=[255,0,255],axis=1))))
 if i<7: changed.append(round(float(np.mean(np.any(np.asarray(decoded[i])!=np.asarray(decoded[i+1]),axis=2))),4))
assert not any(edge), edge
assert all(np.any(np.asarray(decoded[i])!=np.asarray(decoded[i+1])) for i in range(7))
sha=hashlib.sha256(open(path,'rb').read()).hexdigest()
qa={'character':'福島正則','asset':os.path.basename(path),'status':'candidate, not game-integrated','sheet_size':[4096,384],'cell_size':[512,384],'frames':8,'background_rgb':[255,0,255],'groundline_y':363,'foot_anchor_x':256,'scale':scale,'frame_foreground_bboxes':bboxes,'exact_magenta_pixels_per_cell':exact,'nonmagenta_outer_edge_pixels_per_cell':edge,'decoded_gif_frames':len(decoded),'unique_frame_count':len({hashlib.sha256(np.asarray(f).tobytes()).hexdigest() for f in decoded}),'adjacent_changed_pixel_fraction':changed,'sha256':sha,'generation':'OpenAI built-in imagegen informed by official Samurai Shodown motion archetypes; AI generated and composed into cells, not hand-drawn.','notes':'Right-facing fierce naginata boss with horned helmet, bronze armor, and torn rust-red cloak. Sequence: low launch, leap, overhead wind-up, descending two-hand grip, heavy ground-breaking naginata slam, aftershock with debris, lift weapon and recover, grounded guard. Visual/gameplay approval pending.'}
with open(os.path.join(outdir,name+'_qa-v1.json'),'w',encoding='utf-8') as f: json.dump(qa,f,ensure_ascii=False,indent=2)
print(json.dumps({'path':path,'sha256':sha,'bboxes':bboxes,'magenta':exact,'edge':edge,'changed':changed},ensure_ascii=False))

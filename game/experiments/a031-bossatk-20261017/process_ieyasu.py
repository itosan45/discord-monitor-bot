from PIL import Image
import numpy as np, hashlib, json, os
from collections import deque
src=r'game/experiments/a031-bossatk-20261017/徳川家康_跳び込み攻撃_2x4生成原画.png'
outdir=r'game/experiments/a031-bossatk-20261017'
name='徳川家康_跳び込み攻撃'
raw=Image.open(src).convert('RGB')
assert raw.size==(1024,1536), raw.size
frames=[]; bboxes=[]; exact=[]
# Source is row-major 2x4: launch, ascent, overhead wind-up, descent, impact, aftershock, recover, guard.
# Grounded source soles were inspected in the full reference mosaic; air frames float above y=363.
# v6 aligns recovered/guard soles and removes the remaining one-pixel shard beside frame 8.
offsets=[154.0,86.4,86.4,86.4,161.0,159.0,175.7,176.8]
scale=.55
for i in range(8):
    row,col=divmod(i,2)
    tile=raw.crop((col*512,row*384,(col+1)*512,(row+1)*384))
    a=np.asarray(tile).copy()
    # Identify near-magenta pixels, then flood only the regions connected to tile edges.
    near=(a[:,:,0]>165)&(a[:,:,2]>165)&(a[:,:,1]<90)&(np.abs(a[:,:,0].astype(np.int16)-a[:,:,2].astype(np.int16))<85)
    # Explicit 4-neighbor flood fill through near-magenta pixels connected to tile edges.
    bg=np.zeros((384,512),dtype=bool)
    queue=deque()
    for x in range(512):
        if near[0,x]: bg[0,x]=True; queue.append((0,x))
        if near[383,x] and not bg[383,x]: bg[383,x]=True; queue.append((383,x))
    for y in range(384):
        if near[y,0] and not bg[y,0]: bg[y,0]=True; queue.append((y,0))
        if near[y,511] and not bg[y,511]: bg[y,511]=True; queue.append((y,511))
    while queue:
        y,x=queue.popleft()
        for ny,nx in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)):
            if 0<=ny<384 and 0<=nx<512 and near[ny,nx] and not bg[ny,nx]:
                bg[ny,nx]=True; queue.append((ny,nx))
    a[bg]=[255,0,255]
    tile=Image.fromarray(a,'RGB')
    tile=tile.resize((round(512*scale),round(384*scale)),Image.Resampling.LANCZOS)
    canvas=Image.new('RGB',(512,384),(255,0,255))
    ox=round((512-tile.width)/2)
    oy=round(offsets[i])
    canvas.paste(tile,(ox,oy))
    # A detached 57px generator artifact sits left of frame-8 body; clear only its measured bbox.
    if i==7:
        canvas.putpixel((118,199),(255,0,255))
        for yy in range(201,215):
            for xx in range(115,121): canvas.putpixel((xx,yy),(255,0,255))
    arr=np.asarray(canvas)
    ys,xs=np.where(np.any(arr!=[255,0,255],axis=2))
    if len(xs): bboxes.append([int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())])
    else: bboxes.append(None)
    exact.append(int(np.count_nonzero(np.all(arr==[255,0,255],axis=2))))
    frames.append(canvas)
sheet=Image.new('RGB',(4096,384),(255,0,255))
for i,f in enumerate(frames): sheet.paste(f,(i*512,0))
path=os.path.join(outdir,name+'_8コマ_v6.png'); sheet.save(path,optimize=True)
grid=Image.new('RGB',(1024,1536),(50,50,50))
for i,f in enumerate(frames): grid.paste(f,((i%2)*512,(i//2)*384))
grid.save(os.path.join(outdir,name+'_review-grid-v6.png'),optimize=True)
frames[0].save(os.path.join(outdir,name+'_preview-v6.gif'),save_all=True,append_images=frames[1:],duration=150,loop=0,disposal=2)
# Re-open and inspect output dimensions, 8-frame GIF, frame uniqueness and hard outer edge.
check=Image.open(path); assert check.size==(4096,384)
gif=Image.open(os.path.join(outdir,name+'_preview-v6.gif')); decoded=[]
for i in range(gif.n_frames): gif.seek(i); decoded.append(gif.convert('RGB').copy())
assert len(decoded)==8
edge_nonmag=[]; changed=[]
for i in range(8):
    ar=np.asarray(check.crop((i*512,0,(i+1)*512,384)))
    edge=np.concatenate([ar[0],ar[-1],ar[:,0],ar[:,-1]])
    edge_nonmag.append(int(np.count_nonzero(np.any(edge!=[255,0,255],axis=1))))
    if i<7:
        p=np.asarray(decoded[i]); q=np.asarray(decoded[i+1]); changed.append(round(float(np.mean(np.any(p!=q,axis=2))),4))
assert not any(edge_nonmag), edge_nonmag
assert all(np.any(np.asarray(decoded[i])!=np.asarray(decoded[i+1])) for i in range(7))
sha=hashlib.sha256(open(path,'rb').read()).hexdigest()
qa={'character':'徳川家康（影武者）','asset':os.path.basename(path),'status':'candidate, not game-integrated','sheet_size':[4096,384],'cell_size':[512,384],'frames':8,'background_rgb':[255,0,255],'groundline_y':363,'foot_anchor_x':256,'scale':scale,'frame_foreground_bboxes':bboxes,'exact_magenta_pixels_per_cell':exact,'nonmagenta_outer_edge_pixels_per_cell':edge_nonmag,'decoded_gif_frames':len(decoded),'unique_frame_count':len({hashlib.sha256(np.asarray(f).tobytes()).hexdigest() for f in decoded}),'adjacent_changed_pixel_fraction':changed,'sha256':sha,'source_image':os.path.basename(src),'generation':'OpenAI built-in imagegen; references: Ieyasu setting and existing Ieyasu jump 4-frame v2; AI generated then composed into cells, not hand-drawn.','notes':'v1 retained: first flood-fill implementation failed to normalize source background. v2 retained: guard/recovery sole alignment was 20px high. v3-v5 retained with detached generated specks around frame 8. v6 aligns poses to the shared ground anchor and removes only those isolated specks. Frames 1, 5-8 are grounded actions/recovery; 2-4 are airborne. Impact includes restrained dust. Visual pose continuity and true animation require reviewer and game runtime confirmation.'}
with open(os.path.join(outdir,name+'_qa-v6.json'),'w',encoding='utf-8') as f: json.dump(qa,f,ensure_ascii=False,indent=2)
print(json.dumps({'path':path,'sha256':sha,'bboxes':bboxes,'magenta':exact,'edge':edge_nonmag,'changed':changed},ensure_ascii=False))


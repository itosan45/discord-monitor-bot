from PIL import Image
import numpy as np, json, hashlib, os, cv2
BASE=os.path.join(os.path.dirname(__file__),'本多忠勝_三段突き')
raw=Image.open(BASE+'_16f-source-v2.png').convert('RGB');W,H=raw.size
assert W%4==0 and abs(H/4-W/4*.75)<1,raw.size
mag=np.array([255,0,255],dtype=np.uint8);frames=[];boxes=[];anchors=[];edges=[];changes=[];scales=[]
for i in range(16):
 r,c=divmod(i,4);x0=round(c*W/4);x1=round((c+1)*W/4);y0=round(r*H/4);y1=round((r+1)*H/4)
 a=np.asarray(raw.crop((x0+8,y0+8,x1-8,y1-8)).convert('RGB')).copy()
 bg=(a[:,:,0]>=180)&(a[:,:,2]>=180)&(a[:,:,1]<=125);a[bg]=mag
 fg=np.any(a!=mag,axis=2).astype(np.uint8);n,l,stats,cent=cv2.connectedComponentsWithStats(fg,8)
 lab=1+int(np.argmax(stats[1:,cv2.CC_STAT_AREA]));keep=(l==lab);a[~keep]=mag
 ys,xs=np.where(keep);assert len(xs)>500,(i,len(xs))
 crop=Image.fromarray(a[ys.min():ys.max()+1,xs.min():xs.max()+1]);ch,cw=np.asarray(crop).shape[:2]
 ly,lx=np.where(keep[max(0,keep.shape[0]-50):,:]);ax=float(np.mean(lx)) if len(lx) else float((xs.min()+xs.max())/2);axc=ax-float(xs.min())
 span=max(axc,cw-1-axc,1.0);s=min(188/ch,480/cw,244/span);nw=max(1,round(cw*s));nh=max(1,round(ch*s));im=crop.resize((nw,nh),Image.Resampling.LANCZOS)
 px=round(256-axc*s);py=363-nh
 canvas=Image.new('RGB',(512,384),(255,0,255));canvas.paste(im,(px,py));o=np.asarray(canvas);oy,ox=np.where(np.any(o!=mag,axis=2));border=np.concatenate([o[0],o[-1],o[:,0],o[:,-1]])
 boxes.append([int(ox.min()),int(oy.min()),int(ox.max()),int(oy.max())]);anchors.append([round(px+axc*s,2),int(oy.max())]);edges.append(int(np.count_nonzero(np.any(border!=mag,axis=1))));scales.append(round(s,5));frames.append(canvas)
sheet=Image.new('RGB',(8192,384),(255,0,255))
for i,f in enumerate(frames):sheet.paste(f,(i*512,0))
out=BASE+'_16コマ_v5.png';sheet.save(out,optimize=True)
grid=Image.new('RGB',(2048,1536),(48,48,48))
for i,f in enumerate(frames):grid.paste(f,((i%4)*512,(i//4)*384))
grid.save(BASE+'_review-grid-16f-v5.png',optimize=True)
frames[0].save(BASE+'_preview-16f-v5.gif',save_all=True,append_images=frames[1:],duration=65,loop=0,disposal=2)
g=Image.open(BASE+'_preview-16f-v5.gif');dec=[]
for i in range(g.n_frames):g.seek(i);dec.append(np.asarray(g.convert('RGB').copy()))
h=[hashlib.sha256(x.tobytes()).hexdigest() for x in dec];changes=[round(float(np.mean(np.any(dec[i]!=dec[i+1],axis=2))),4) for i in range(15)]
qa={'character':'本多忠勝','asset':os.path.basename(out),'status':'candidate, not game-integrated','sheet_size':[8192,384],'cell_size':[512,384],'frames':16,'background_rgb':[255,0,255],'groundline_y':363,'foot_anchor_target_x':256,'source_grid':[4,4],'source_size':[W,H],'frame_foreground_bboxes':boxes,'estimated_bottom_anchors':anchors,'nonmagenta_outer_edge_pixels_per_cell':edges,'decoded_gif_frames':g.n_frames,'unique_frame_count':len(set(h)),'adjacent_changed_pixel_fraction':changes,'sha256':hashlib.sha256(open(out,'rb').read()).hexdigest(),'generation':'OpenAI built-in imagegen using existing Honda Tadakatsu triple-thrust sheet as identity reference; AI generated and cell-composited, not hand-drawn.','notes':'v5 keeps only the largest connected component in each cell to remove detached cross-cell fragments and scales about the estimated foot anchor to preserve safe margins. Sequence: load/step, chest thrust/recoil, low thrust/reset, pivot/rising thrust, recoil and guard recovery. Existing 8-frame versions and rejected v1-v4 remain preserved. Static QA only; game timing, hitboxes, runtime and independent review pending.'}
with open(BASE+'_qa-16f-v5.json','w',encoding='utf-8') as f:json.dump(qa,f,ensure_ascii=False,indent=2)
assert g.n_frames==16 and len(set(h))==16 and not any(edges),(g.n_frames,len(set(h)),edges)
print(json.dumps({'size':Image.open(out).size,'frames':g.n_frames,'unique':len(set(h)),'edges':edges,'changes':changes,'anchors':anchors},ensure_ascii=False))

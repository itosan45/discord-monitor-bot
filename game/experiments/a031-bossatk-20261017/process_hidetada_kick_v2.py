from PIL import Image
import numpy as np, hashlib, json, os
src='game/experiments/a031-bossatk-20261017/徳川秀忠_前蹴り_6コマ_v1.png';base='game/experiments/a031-bossatk-20261017/徳川秀忠_前蹴り'; old=np.asarray(Image.open(src).convert('RGB'));frames=[];boxes=[];edges=[]
for i in range(6):
 a=old[:,i*512:(i+1)*512].copy()
 if i==2:a[228:238,343:351]=[255,0,255]
 m=np.any(a!=[255,0,255],axis=2);y,x=np.where(m);boxes.append([int(x.min()),int(y.min()),int(x.max()),int(y.max())]);e=np.concatenate([m[0],m[-1],m[:,0],m[:,-1]]);edges.append(int(e.sum()));frames.append(Image.fromarray(a))
sheet=Image.new('RGB',(3072,384),(255,0,255))
for i,f in enumerate(frames):sheet.paste(f,(i*512,0))
out=base+'_6コマ_v2.png';sheet.save(out,optimize=True);grid=Image.new('RGB',(1536,768),(50,50,50))
for i,f in enumerate(frames):grid.paste(f,((i%3)*512,(i//3)*384))
grid.save(base+'_review-grid-v2.png',optimize=True);frames[0].save(base+'_preview-v2.gif',save_all=True,append_images=frames[1:],duration=120,loop=0,disposal=2)
g=Image.open(base+'_preview-v2.gif');dec=[]
for i in range(g.n_frames):g.seek(i);dec.append(np.asarray(g.convert('RGB').copy()))
assert len(dec)==6 and len({hashlib.sha256(a.tobytes()).hexdigest() for a in dec})==6 and not any(edges)
qa=json.load(open(base+'_qa-v1.json',encoding='utf-8-sig'));qa.update({'asset':os.path.basename(out),'status':'candidate, not game-integrated','frame_foreground_bboxes':boxes,'nonmagenta_outer_edge_pixels_per_cell':edges,'decoded_gif_frames':6,'unique_frame_count':6,'adjacent_changed_pixel_fraction':[round(float(np.mean(np.any(dec[i]!=dec[i+1],axis=2))),4) for i in range(5)],'sha256':hashlib.sha256(open(out,'rb').read()).hexdigest(),'generation':qa['generation']+' v2 removes one tiny detached source speck near frame 3 kick foot.','notes':'Six visibly distinct front kick phases. v2 clears one isolated fleck near the extended leg while keeping the foot silhouette. Candidate; gameplay review pending.'})
with open(base+'_qa-v2.json','w',encoding='utf-8') as f:json.dump(qa,f,ensure_ascii=False,indent=2)
print(json.dumps({'sha256':qa['sha256'],'edges':edges,'changed':qa['adjacent_changed_pixel_fraction']},ensure_ascii=False))

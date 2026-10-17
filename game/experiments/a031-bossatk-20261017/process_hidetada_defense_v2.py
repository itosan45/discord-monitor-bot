from PIL import Image, ImageDraw
from pathlib import Path
import numpy as np, hashlib, json, cv2
root=Path(__file__).resolve().parent

def find(pattern):
 m=list(root.glob(pattern))
 if len(m)!=1: raise RuntimeError((pattern,len(m)))
 return m[0]
inputs={
 '構え':[(find('徳川秀忠_防御_構え_source-v1.png'),3,2)],
 '受け止め':[(find('徳川秀忠_防御_受け止め_source-v1.png'),2,2)],
 '受け流し':[(find('徳川秀忠_防御_受け流し_source-1-v1.png'),2,2),(find('徳川秀忠_防御_受け流し_source-2-v1.png'),2,2)],
 '崩れ':[(find('徳川秀忠_防御_崩れ_source-v1.png'),3,2)],
}
qa={'candidate_only':True,'integrated':False,'generated_and_composited':True,'component_cleanup':'Remove isolated RGB components of <=25 pixels after scale; retain connected figure/weapon silhouette.','actions':{}}
for action,specs in inputs.items():
 frames=[]; sources=[]
 for path,nc,nr in specs:
  im=Image.open(path).convert('RGBA'); cw=im.width//nc; ch=im.height//nr; sources.append(path.name)
  for idx in range(nc*nr):
   x=(idx%nc)*cw;y=(idx//nc)*ch
   tile=im.crop((x,y,x+cw,y+ch)); alpha=np.array(tile.getchannel('A'))
   yy,xx=np.where(alpha>24)
   if not len(xx): raise RuntimeError(f'empty source tile {path.name}:{idx+1}')
   bbox=(int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1))
   frames.append((tile.crop(bbox),bbox,(cw,ch),path.name,idx+1))
 heights=[v[0].height for v in frames]
 scale=min(188/float(np.median(heights)),440/max(v[0].width for v in frames))
 outframes=[]; detail=[]
 for i,(fg,bbox,cell,src,cellidx) in enumerate(frames,1):
  nw=max(1,round(fg.width*scale)); nh=max(1,round(fg.height*scale)); fg=fg.resize((nw,nh),Image.Resampling.LANCZOS)
  # Ground/root anchor from bottom silhouette band; keep action-wide scale fixed.
  ar=np.array(fg.getchannel('A')); band=ar[max(0,nh-8):,:]>24; fx=np.where(band.any(axis=0))[0]
  footx=float((fx.min()+fx.max())/2) if len(fx) else nw/2
  px=round(256-footx); py=363-nh
  canvas=Image.new('RGBA',(512,384),(255,0,255,255)); canvas.alpha_composite(fg,(px,py)); rgb=np.array(canvas.convert('RGB'))
  mask=np.any(rgb!=[255,0,255],axis=2).astype('uint8'); n,labels,stats,_=cv2.connectedComponentsWithStats(mask,8)
  removed=[]
  for lab in range(1,n):
   area=int(stats[lab,cv2.CC_STAT_AREA])
   if area<=25:
    removed.append(area); rgb[labels==lab]=[255,0,255]
  canvas=Image.fromarray(rgb,'RGB'); outframes.append(canvas)
  ys,xs=np.where(np.any(rgb!=[255,0,255],axis=2))
  detail.append({'frame':i,'source':src,'source_cell':cellidx,'source_bbox_alpha_gt24':bbox,'output_bbox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'foot_anchor':[round(footx+px,2),363],'scale':round(scale,5),'removed_isolated_components_px':removed})
 out=Image.new('RGB',(512*len(outframes),384),(255,0,255))
 for i,fr in enumerate(outframes):out.paste(fr,(i*512,0))
 name=f'徳川秀忠_防御_{action}_{len(outframes)}コマ_v2.png'; op=root/name
 if op.exists():raise FileExistsError(op)
 out.save(op,optimize=True)
 cols=4;tw=256;th=192; rows=(len(outframes)+cols-1)//cols
 grid=Image.new('RGB',(cols*tw,rows*(th+24)),(42,42,48));d=ImageDraw.Draw(grid)
 for i,fr in enumerate(outframes):
  x=(i%cols)*tw;y=(i//cols)*(th+24);grid.paste(fr.resize((tw,th),Image.Resampling.NEAREST),(x,y));d.text((x+4,y+th+2),f'{i+1:02}',fill='white')
 gridname=f'徳川秀忠_防御_{action}_review-v2.png';grid.save(root/gridname,optimize=True)
 gifname=f'徳川秀忠_防御_{action}_preview-v2.gif';outframes[0].save(root/gifname,save_all=True,append_images=outframes[1:],duration=110,loop=0,optimize=False)
 qa['actions'][action]={'sprite':name,'frames':len(outframes),'size':list(out.size),'sha256':hashlib.sha256(op.read_bytes()).hexdigest(),'unique_frames':len({hashlib.sha256(np.asarray(f).tobytes()).hexdigest() for f in outframes}),'sources':sources,'review_grid':gridname,'preview_gif':gifname,'frames_detail':detail,'notes':'AI-generated source with crop, alpha extraction, uniform per-action scaling and anchor placement; candidate only; runtime not checked.'}
qa['contact_frames']={'guard':'no hitbox/no advance','block':'incoming contact on frame 2; no advance','parry':'deflection/contact on frame 4; step on frame 2','stagger':'incoming impact on frame 1; no advance'}
qa['limitations']=['Defensive motion only; does not count toward the requested five attack variants.','No runtime, hitbox, facing-left or mobile check.','Source is AI-generated and composites; not hand-painted.']
(root/'徳川秀忠_防御_QA-v2.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:{'file':v['sprite'],'frames':v['frames'],'unique':v['unique_frames'],'sha256':v['sha256'],'cleanup':sum(len(f['removed_isolated_components_px']) for f in v['frames_detail'])} for k,v in qa['actions'].items()},ensure_ascii=False,indent=2))

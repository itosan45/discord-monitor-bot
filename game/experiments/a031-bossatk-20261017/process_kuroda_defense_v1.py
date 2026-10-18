from pathlib import Path
from PIL import Image, ImageFilter, ImageStat, ImageChops
import cv2, hashlib, json
import numpy as np

ROOT=Path(__file__).parent
CELL=(512,384); AX=256; GROUND=363; TARGET_H=188
ITEMS=[
 ("構え",6,3,[(0,512),(512,1024)],"黒田長政_防御_構え_source-v1.png",(1536,1024)),
 ("受け止め",4,2,[(0,512),(512,1024)],"黒田長政_防御_受け止め_source-v1.png",(1536,1024)),
 ("受け流し",8,4,[(0,444),(444,887)],"黒田長政_防御_受け流し_source-v1.png",(1774,887)),
 ("崩れ",6,3,[(0,512),(512,1024)],"黒田長政_防御_崩れ_source-v1.png",(1536,1024)),
]

def bg_candidate(rgb):
 r,g,b=rgb
 return r>=165 and b>=165 and g<=110 and g*2<min(r,b)

def extract_mask(tile):
 arr=np.asarray(tile,dtype=np.uint8)
 bg=((arr[:,:,0]>=165)&(arr[:,:,2]>=165)&(arr[:,:,1]<=110)&(arr[:,:,1]*2<np.minimum(arr[:,:,0],arr[:,:,2]))).astype(np.uint8)
 n,labels,stats,_=cv2.connectedComponentsWithStats(bg,8)
 edge_labels=set(labels[0,:].tolist()+labels[-1,:].tolist()+labels[:,0].tolist()+labels[:,-1].tolist())-{0}
 remove=np.isin(labels,list(edge_labels))
 alpha=np.where(remove,0,255).astype(np.uint8)
 alpha=cv2.erode(alpha,np.ones((3,3),np.uint8),iterations=1)
 n,labels,stats,_=cv2.connectedComponentsWithStats((alpha>=32).astype(np.uint8),8)
 for i in range(1,n):
  if stats[i,cv2.CC_STAT_AREA]<=600: alpha[labels==i]=0
 return Image.fromarray(alpha)

def make_frame(src,idx,cols,row_bounds):
 w,h=src.size; c=idx%cols; r=idx//cols
 x0=round(c*w/cols); x1=round((c+1)*w/cols); y0,y1=row_bounds[r]
 tile=src.crop((x0,y0,x1,y1)); mask=extract_mask(tile); bb=mask.getbbox()
 if not bb: raise ValueError(f"empty mask frame {idx+1}")
 fg=tile.crop(bb); mask=mask.crop(bb); fw,fh=fg.size
 scale=min(TARGET_H/fh,480/fw); nw=max(1,round(fw*scale)); nh=max(1,round(fh*scale))
 fg=fg.resize((nw,nh),Image.Resampling.LANCZOS); mask=mask.resize((nw,nh),Image.Resampling.LANCZOS)
 ap=np.array(mask,dtype=np.uint8,copy=True); n,labels,stats,_=cv2.connectedComponentsWithStats((ap>=32).astype(np.uint8),8)
 for i in range(1,n):
  if stats[i,cv2.CC_STAT_AREA]<=400: ap[labels==i]=0
 mask=Image.fromarray(ap); ys,xs=np.where(ap>=96)
 if len(xs)==0: raise ValueError(f"no foreground frame {idx+1}")
 foot_band=ys>=max(0,int(nh*.82)); foot_center=float(xs[foot_band].mean()) if foot_band.any() else float(xs.mean())
 px=round(AX-foot_center); py=GROUND-1-int(ys.max())
 if px<0 or px+nw>CELL[0] or py<0 or py+nh>CELL[1]: raise ValueError(f"clipped frame {idx+1}: {(px,py,nw,nh)}")
 cell=Image.new("RGBA",CELL,(255,0,255,255)); layer=fg.convert("RGBA"); layer.putalpha(mask); cell.alpha_composite(layer,(px,py)); rgb=cell.convert("RGB")
 points=[(x,0) for x in range(CELL[0])]+[(x,CELL[1]-1) for x in range(CELL[0])]+[(0,y) for y in range(CELL[1])]+[(CELL[0]-1,y) for y in range(CELL[1])]
 detail={"source_cell":[c+1,r+1],"crop_box":[x0,y0,x1,y1],"mask_bbox":[x0+bb[0],y0+bb[1],x0+bb[2],y0+bb[3]],"output_bbox":[px,py,px+nw,py+nh],"ground_contact_y":GROUND-1,"scale":round(scale,6),"edge_contact":any(rgb.getpixel(p)!=(255,0,255) for p in points)}
 return rgb,detail

qa={"character":"黒田長政","candidate_only":True,"integrated":False,"generation":"built-in image_gen AI source poses, boundary-connected magenta flood removal, 1px erosion, small-component cleanup, uniform scale and cell placement","cell_size":list(CELL),"anchor":{"lower_body_center_x":AX,"ground_y":GROUND},"target_height_px":TARGET_H,"actions":{}}
for action,count,cols,row_bounds,source_name,source_size in ITEMS:
 source=Image.open(ROOT/source_name).convert("RGB")
 if source.size!=source_size: raise ValueError(f"unexpected source size {source_name}: {source.size}")
 frames=[]; details=[]
 for i in range(count):
  f,d=make_frame(source,i,cols,row_bounds); frames.append(f); details.append(d)
 strip=Image.new("RGB",(CELL[0]*count,CELL[1]),(255,0,255))
 for i,f in enumerate(frames): strip.paste(f,(i*CELL[0],0))
 stem=f"黒田長政_防御_{action}"; png=ROOT/f"{stem}_{count}コマ_v1.png"; gif=ROOT/f"{stem}_preview-v1.gif"; grid=ROOT/f"{stem}_review-v1.png"
 for p in (png,gif,grid):
  if p.exists(): raise FileExistsError(f"refusing to overwrite {p.name}")
 strip.save(png,optimize=True); frames[0].save(gif,save_all=True,append_images=frames[1:],duration=110,loop=0,disposal=2)
 ncols=min(4,count); thumb=(256,192); nrows=(count+ncols-1)//ncols; review=Image.new("RGB",(ncols*thumb[0],nrows*thumb[1]),(255,0,255))
 for i,f in enumerate(frames): review.paste(f.resize(thumb,Image.Resampling.LANCZOS),((i%ncols)*thumb[0],(i//ncols)*thumb[1]))
 review.save(grid,optimize=True)
 hashes=[hashlib.sha256(f.tobytes()).hexdigest() for f in frames]
 diffs=[sum(ImageStat.Stat(ImageChops.difference(frames[i-1],frames[i])).sum) for i in range(1,count)]
 qa["actions"][action]={"sprite":png.name,"frames":count,"size":list(strip.size),"sha256":hashlib.sha256(png.read_bytes()).hexdigest(),"unique_frames":len(set(hashes)),"source":source_name,"source_size":list(source.size),"preview_gif":gif.name,"review_grid":grid.name,"frame_details":details,"adjacent_pixel_difference_sum":diffs,"candidate_contact_frame":{"構え":None,"受け止め":2,"受け流し":5,"崩れ":1}[action],"forward_step_frame":None,"notes":"候補。目視から置いた接触候補はゲーム判定ではない。ゲーム統合、左右向き、実機は未確認。"}
qpath=ROOT/"黒田長政_防御_QA-v1.json"
if qpath.exists(): raise FileExistsError(f"refusing to overwrite {qpath.name}")
qpath.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({a:{"sprite":d["sprite"],"frames":d["frames"],"size":d["size"],"unique":d["unique_frames"],"edge_contact":sum(x["edge_contact"] for x in d["frame_details"]),"min_adjacent_diff":min(d["adjacent_pixel_difference_sum"] or [0])} for a,d in qa["actions"].items()},ensure_ascii=False,indent=2))

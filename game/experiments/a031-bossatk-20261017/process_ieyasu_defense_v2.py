from pathlib import Path
from PIL import Image, ImageFilter, ImageChops, ImageStat
from collections import deque
import json, hashlib

ROOT=Path(__file__).parent
ITEMS=[
 ("構え",6,3,2,"徳川家康_防御_構え_source-v2.png"),
 ("受け止め",4,2,2,"徳川家康_防御_受け止め_source-v1.png"),
 ("受け流し",8,2,4,"徳川家康_防御_受け流し_source-v2.png"),
 ("崩れ",6,3,2,"徳川家康_防御_崩れ_source-v1.png"),
]
CELL=(512,384); AX=256; GROUND=363; TARGET_H=188; VERSION=2

def make_mask(im):
    p=im.load(); m=Image.new("L",im.size,0); q=m.load()
    for y in range(im.height):
        for x in range(im.width):
            r,g,b=p[x,y]
            if not (r>=178 and b>=178 and g<=90 and g*2<min(r,b)):
                q[x,y]=255
    m=m.filter(ImageFilter.MinFilter(3))
    # Remove only tiny isolated segmentation specks; preserve detached sword pieces.
    w,h=m.size; a=m.load(); seen=bytearray(w*h)
    for y in range(h):
        for x in range(w):
            start=y*w+x
            if a[x,y]<32 or seen[start]: continue
            seen[start]=1; stack=[start]; comp=[start]
            while stack:
                k=stack.pop(); xx=k%w; yy=k//w
                for dy in (-1,0,1):
                    ny=yy+dy
                    if ny<0 or ny>=h: continue
                    for dx in (-1,0,1):
                        if dx==0 and dy==0: continue
                        nx=xx+dx
                        if nx<0 or nx>=w: continue
                        nk=ny*w+nx
                        if not seen[nk] and a[nx,ny]>=32:
                            seen[nk]=1; stack.append(nk); comp.append(nk)
            if len(comp)<=25:
                for k in comp: a[k%w,k//w]=0
    return m

def frame_from(src,i,cols,rows):
    w,h=src.size; c=i%cols; r=i//cols
    x0=round(c*w/cols); x1=round((c+1)*w/cols)
    y0=round(r*h/rows); y1=round((r+1)*h/rows)
    tile=src.crop((x0,y0,x1,y1)); mask=make_mask(tile); bb=mask.getbbox()
    if not bb: raise ValueError(f"empty frame {i+1}")
    crop=tile.crop(bb); alpha=mask.crop(bb); bw,bh=crop.size
    scale=min(TARGET_H/bh,480/bw)
    nw,nh=max(1,round(bw*scale)),max(1,round(bh*scale))
    crop=crop.resize((nw,nh),Image.Resampling.LANCZOS)
    alpha=alpha.resize((nw,nh),Image.Resampling.LANCZOS)
    al=alpha.load()
    lower=[x for y in range(max(0,round(nh*.82)),nh) for x in range(nw) if al[x,y]>=32]
    if not lower: raise ValueError(f"no foot anchor pixels frame {i+1}")
    footcx=sum(lower)/len(lower)
    px=round(AX-footcx); py=GROUND-nh
    cell=Image.new("RGBA",CELL,(255,0,255,255))
    fg=crop.convert("RGBA"); fg.putalpha(alpha); cell.alpha_composite(fg,(px,py))
    rgb=cell.convert("RGB")
    # Avoid accidental clipping and record cell bounds.
    edge=[rgb.getpixel((x,y))!=(255,0,255) for x,y in
      [(x,0) for x in range(CELL[0])] + [(x,CELL[1]-1) for x in range(CELL[0])] +
      [(0,y) for y in range(CELL[1])] + [(CELL[0]-1,y) for y in range(CELL[1])]]
    return rgb,{"source_cell":[c+1,r+1],"source_bbox":[x0+bb[0],y0+bb[1],x0+bb[2],y0+bb[3]],
      "output_bbox":[px,py,px+nw,py+nh],"foot_anchor":[AX,GROUND],
      "source_cell_size":[x1-x0,y1-y0],"scale":round(scale,5),"frame_edge_contact":any(edge)}

qa={"character":"徳川家康(第六幕の影武者)","candidate_only":True,"integrated":False,
 "generation":"built-in image_gen; AI-generated source frames, threshold cutout, uniform resize and placement",
 "cell_size":list(CELL),"anchor":{"foot_x":AX,"ground_y":GROUND},"target_height_px":TARGET_H,"actions":{}}
for action,count,cols,rows,src_name in ITEMS:
    src=Image.open(ROOT/src_name).convert("RGB"); frames=[]; details=[]
    for i in range(count):
        f,d=frame_from(src,i,cols,rows); frames.append(f); details.append(d)
    strip=Image.new("RGB",(CELL[0]*count,CELL[1]),(255,0,255))
    for i,f in enumerate(frames): strip.paste(f,(i*CELL[0],0))
    stem=f"徳川家康_防御_{action}"
    png=ROOT/f"{stem}_{count}コマ_v{VERSION}.png"; gif=ROOT/f"{stem}_preview-v{VERSION}.gif"
    grid=ROOT/f"{stem}_review-v{VERSION}.png"
    for path in (png,gif,grid):
        if path.exists(): raise FileExistsError(f"refusing to overwrite {path.name}")
    strip.save(png,optimize=True)
    frames[0].save(gif,save_all=True,append_images=frames[1:],duration=110,loop=0,disposal=2)
    ncols=min(4,count); thumb=(256,192); nrows=(count+ncols-1)//ncols
    review=Image.new("RGB",(ncols*thumb[0],nrows*thumb[1]),(255,0,255))
    for i,f in enumerate(frames): review.paste(f.resize(thumb,Image.Resampling.LANCZOS),((i%ncols)*thumb[0],(i//ncols)*thumb[1]))
    review.save(grid,optimize=True)
    hashes=[hashlib.sha256(f.tobytes()).hexdigest() for f in frames]
    adjacent=[sum(ImageStat.Stat(ImageChops.difference(frames[i-1],frames[i])).sum) for i in range(1,count)]
    qa["actions"][action]={"sprite":png.name,"frames":count,"size":list(strip.size),
      "sha256":hashlib.sha256(png.read_bytes()).hexdigest(),"unique_frames":len(set(hashes)),
      "source":src_name,"source_size":list(src.size),"preview_gif":gif.name,"review_grid":grid.name,
      "frames_detail":details,"adjacent_pixel_difference_sum":adjacent,
      "contact_frame":"visual defense only; no hitbox specified",
      "forward_step_frame":"none; repositioning is defensive only",
      "notes":"候補。Claude側の組み込み・ゲーム中の防御判定・左右・実機は未確認。"}
qpath=ROOT/f"徳川家康_防御_QA-v{VERSION}.json"
if qpath.exists(): raise FileExistsError(f"refusing to overwrite {qpath.name}")
qpath.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({k:{"sprite":v["sprite"],"frames":v["frames"],"size":v["size"],"unique":v["unique_frames"],"edge_contact":sum(f["frame_edge_contact"] for f in v["frames_detail"]),"min_adjacent_diff":min(v["adjacent_pixel_difference_sum"])} for k,v in qa["actions"].items()},ensure_ascii=True))

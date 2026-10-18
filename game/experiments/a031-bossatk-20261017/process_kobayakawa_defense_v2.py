from pathlib import Path
from PIL import Image, ImageFilter, ImageStat, ImageChops
from collections import deque
import cv2
import numpy as np
import json, hashlib

ROOT = Path(__file__).parent
CELL = (512, 384)
AX, GROUND, TARGET_H = 256, 363, 188
ITEMS = [
    ("構え", 6, 3, [(0, 512), (512, 1024)], "小早川秀秋_防御_構え_source-v1.png"),
    ("受け止め", 4, 2, [(0, 512), (512, 1024)], "小早川秀秋_防御_受け止め_source-v1.png"),
    ("受け流し", 8, 2, [(0, 268), (268, 520), (520, 760), (760, 1024)], "小早川秀秋_防御_受け流し_source-v1.png"),
    ("崩れ", 6, 3, [(0, 512), (512, 1024)], "小早川秀秋_防御_崩れ_source-v1.png"),
]

def is_bg_candidate(rgb):
    r, g, b = rgb
    return r >= 165 and b >= 165 and g <= 110 and g * 2 < min(r, b)

def mask_boundary_magenta(tile):
    """Flood only magenta-like pixels connected to the crop boundary, retaining purple blade."""
    pix = tile.load(); w, h = tile.size
    bg = bytearray(w*h)
    q = deque()
    for x in range(w):
        for y in (0, h-1):
            k=y*w+x
            if not bg[k] and is_bg_candidate(pix[x,y]): bg[k]=1; q.append(k)
    for y in range(h):
        for x in (0, w-1):
            k=y*w+x
            if not bg[k] and is_bg_candidate(pix[x,y]): bg[k]=1; q.append(k)
    while q:
        k=q.popleft(); x=k%w; y=k//w
        for dy in (-1,0,1):
            yy=y+dy
            if not 0 <= yy < h: continue
            for dx in (-1,0,1):
                xx=x+dx
                if (dx or dy) and 0 <= xx < w:
                    nk=yy*w+xx
                    if not bg[nk] and is_bg_candidate(pix[xx,yy]): bg[nk]=1; q.append(nk)
    alpha=Image.new("L",(w,h),255); a=alpha.load()
    for y in range(h):
        for x in range(w):
            if bg[y*w+x]: a[x,y]=0
    # Remove edge-color fringe conservatively; this also protects the violet sword interior.
    alpha=alpha.filter(ImageFilter.MinFilter(3))
    # Drop detached color flecks left inside enclosed folds; keep large separated accessories.
    arr=np.asarray(alpha,dtype=np.uint8).copy()
    n, labels, stats, _=cv2.connectedComponentsWithStats((arr>=32).astype(np.uint8),8)
    for component in range(1,n):
        if stats[component,cv2.CC_STAT_AREA] <= 140:
            arr[labels==component]=0
    return Image.fromarray(arr)

def make_frame(src, idx, cols, row_bounds):
    w,h=src.size; col=idx%cols; row=idx//cols
    x0=round(col*w/cols); x1=round((col+1)*w/cols); y0,y1=row_bounds[row]
    tile=src.crop((x0,y0,x1,y1)); alpha=mask_boundary_magenta(tile); bb=alpha.getbbox()
    if not bb: raise ValueError(f"empty mask at frame {idx+1}")
    fg=tile.crop(bb); alpha=alpha.crop(bb); fw,fh=fg.size
    scale=min(TARGET_H/fh,480/fw); nw=max(1,round(fw*scale)); nh=max(1,round(fh*scale))
    fg=fg.resize((nw,nh),Image.Resampling.LANCZOS); alpha=alpha.resize((nw,nh),Image.Resampling.LANCZOS)
    # Align the lowest visible contact (foot or deliberate brace hand) to the common ground line.
    ap=alpha.load(); visible=[(x,y) for y in range(nh) for x in range(nw) if ap[x,y]>=96]
    if not visible: raise ValueError(f"no visible pixels at frame {idx+1}")
    minx=min(p[0] for p in visible); maxx=max(p[0] for p in visible); maxy=max(p[1] for p in visible)
    px=round(AX-(minx+maxx+1)/2); py=GROUND-1-maxy
    cell=Image.new("RGBA",CELL,(255,0,255,255)); layer=fg.convert("RGBA"); layer.putalpha(alpha); cell.alpha_composite(layer,(px,py))
    rgb=cell.convert("RGB")
    edges=[rgb.getpixel((x,0))!=(255,0,255) for x in range(CELL[0])]
    edges += [rgb.getpixel((x,CELL[1]-1))!=(255,0,255) for x in range(CELL[0])]
    edges += [rgb.getpixel((0,y))!=(255,0,255) or rgb.getpixel((CELL[0]-1,y))!=(255,0,255) for y in range(CELL[1])]
    return rgb,{"source_cell":[col+1,row+1],"crop_box":[x0,y0,x1,y1],"mask_bbox":[x0+bb[0],y0+bb[1],x0+bb[2],y0+bb[3]],"output_bbox":[px,py,px+nw,py+nh],"ground_contact_y":GROUND-1,"scale":round(scale,6),"edge_contact":any(edges)}

qa={"character":"小早川秀秋","candidate_only":True,"integrated":False,"generation":"built-in image_gen AI source poses, boundary-connected magenta flood removal, uniform scale and cell placement","cell_size":list(CELL),"anchor":{"center_x":AX,"ground_y":GROUND},"target_height_px":TARGET_H,"actions":{}}
for action,count,cols,row_bounds,source_name in ITEMS:
    source=Image.open(ROOT/source_name).convert("RGB")
    if source.size != (1536,1024): raise ValueError(f"unexpected source size: {source_name} {source.size}")
    frames=[]; details=[]
    for i in range(count):
        frame,detail=make_frame(source,i,cols,row_bounds); frames.append(frame); details.append(detail)
    strip=Image.new("RGB",(CELL[0]*count,CELL[1]),(255,0,255))
    for i,frame in enumerate(frames): strip.paste(frame,(i*CELL[0],0))
    stem=f"小早川秀秋_防御_{action}"
    png=ROOT/f"{stem}_{count}コマ_v2.png"; gif=ROOT/f"{stem}_preview-v2.gif"; grid=ROOT/f"{stem}_review-v2.png"
    for p in (png,gif,grid):
        if p.exists(): raise FileExistsError(f"refusing to overwrite {p.name}")
    strip.save(png,optimize=True)
    frames[0].save(gif,save_all=True,append_images=frames[1:],duration=110,loop=0,disposal=2)
    ncols=min(4,count); thumb=(256,192); nrows=(count+ncols-1)//ncols
    review=Image.new("RGB",(ncols*thumb[0],nrows*thumb[1]),(255,0,255))
    for i,frame in enumerate(frames): review.paste(frame.resize(thumb,Image.Resampling.LANCZOS),((i%ncols)*thumb[0],(i//ncols)*thumb[1]))
    review.save(grid,optimize=True)
    frame_hashes=[hashlib.sha256(f.tobytes()).hexdigest() for f in frames]
    diffs=[sum(ImageStat.Stat(ImageChops.difference(frames[i-1],frames[i])).sum) for i in range(1,count)]
    qa["actions"][action]={"sprite":png.name,"frames":count,"size":list(strip.size),"sha256":hashlib.sha256(png.read_bytes()).hexdigest(),"unique_frames":len(set(frame_hashes)),"source":source_name,"source_size":list(source.size),"preview_gif":gif.name,"review_grid":grid.name,"frame_details":details,"adjacent_pixel_difference_sum":diffs,"contact_frame":"候補目安なし。ゲーム側で防御処理と同期する","forward_step_frame":"なし。受け流しの相対位置移動はClaude側で処理する","notes":"候補素材。実ゲームの当たり判定、速度、左右向き、実機は未確認。防御は攻撃バリエーションに含めない。"}
qpath=ROOT/"小早川秀秋_防御_QA-v2.json"
if qpath.exists(): raise FileExistsError(f"refusing to overwrite {qpath.name}")
qpath.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({a:{"sprite":d["sprite"],"frames":d["frames"],"size":d["size"],"unique":d["unique_frames"],"edge_contact":sum(x["edge_contact"] for x in d["frame_details"]),"min_adjacent_diff":min(d["adjacent_pixel_difference_sum"] or [0])} for a,d in qa["actions"].items()},ensure_ascii=False,indent=2))

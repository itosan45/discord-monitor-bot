from pathlib import Path
from PIL import Image, ImageFilter, ImageChops, ImageStat
import json, hashlib

ROOT = Path(__file__).parent
ITEMS = [
    ("構え", 6, 3, 2, "徳川家康_防御_構え_source-v1.png"),
    ("受け止め", 4, 2, 2, "徳川家康_防御_受け止め_source-v1.png"),
    ("受け流し", 8, 4, 2, "徳川家康_防御_受け流し_source-v1.png"),
    ("崩れ", 6, 3, 2, "徳川家康_防御_崩れ_source-v1.png"),
]
CELL = (512, 384)
ANCHOR_X, GROUND_Y = 256, 363
TARGET_H = 188

def foreground_mask(rgb):
    pix = rgb.load()
    mask = Image.new("L", rgb.size, 0)
    m = mask.load()
    for y in range(rgb.height):
        for x in range(rgb.width):
            r, g, b = pix[x, y]
            # The generated background is bright magenta; dark purple armor stays foreground.
            if not (r >= 178 and b >= 178 and g <= 90 and g * 2 < min(r, b)):
                m[x, y] = 255
    # One-pixel erosion removes the magenta fringe left by antialiasing.
    return mask.filter(ImageFilter.MinFilter(3))

def build_frame(source, col, row, cols, rows):
    w, h = source.size
    x0, y0 = round(col*w/cols), round(row*h/rows)
    x1, y1 = round((col+1)*w/cols), round((row+1)*h/rows)
    tile = source.crop((x0, y0, x1, y1))
    mask = foreground_mask(tile)
    bbox = mask.getbbox()
    if not bbox:
        raise ValueError(f"empty foreground at {col},{row}")
    cropped, alpha = tile.crop(bbox), mask.crop(bbox)
    bw, bh = cropped.size
    scale = min(TARGET_H/bh, 480/bw)
    nw, nh = max(1,round(bw*scale)), max(1,round(bh*scale))
    cropped = cropped.resize((nw,nh),Image.Resampling.LANCZOS)
    alpha = alpha.resize((nw,nh),Image.Resampling.LANCZOS)
    # Foot anchor uses the central mass of the bottom 18% of the figure, excluding cape and sword.
    ap = alpha.load()
    foot_y = nh-1
    lower = [x for y in range(max(0,round(nh*.82)),nh) for x in range(nw) if ap[x,y] >= 32]
    if not lower:
        raise ValueError(f"no foot pixels at {col},{row}")
    foot_cx = sum(lower)/len(lower)
    px = round(ANCHOR_X-foot_cx)
    py = GROUND_Y-nh
    cell = Image.new("RGBA",CELL,(255,0,255,255))
    cell.alpha_composite(Image.new("RGBA", (nw,nh),(0,0,0,0)),(px,py)) if False else None
    fg = cropped.convert("RGBA")
    fg.putalpha(alpha)
    cell.alpha_composite(fg,(px,py))
    return cell.convert("RGB"), {
      "source_cell":[col+1,row+1], "source_bbox":[x0+bbox[0],y0+bbox[1],x0+bbox[2],y0+bbox[3]],
      "output_bbox":[px,py,px+nw,py+nh], "foot_anchor":[ANCHOR_X,GROUND_Y],
      "scale":round(scale,5), "source_cell_size":[x1-x0,y1-y0]
    }

qa = {"character":"徳川家康(影武者)","candidate_only":True,"integrated":False,
      "pipeline":"built-in imagegen source -> magenta flood-background threshold/1px shrink -> uniform scaling -> foot-anchor placement",
      "cell_size":list(CELL),"anchor":{"foot_x":ANCHOR_X,"ground_y":GROUND_Y},
      "target_character_height_px":TARGET_H,"actions":{}}
for action,count,cols,rows,source_name in ITEMS:
    src_path = ROOT/source_name
    src = Image.open(src_path).convert("RGB")
    frames, details = [], []
    for i in range(count):
        col, row = i%cols, i//cols
        frame, info = build_frame(src,col,row,cols,rows)
        frames.append(frame)
        details.append(info)
    strip = Image.new("RGB",(CELL[0]*count,CELL[1]),(255,0,255))
    for i,frame in enumerate(frames): strip.paste(frame,(i*CELL[0],0))
    name=f"徳川家康_防御_{action}_{count}コマ_v1.png"
    if (ROOT/name).exists(): raise FileExistsError(f"refusing to overwrite {name}")
    strip.save(ROOT/name,optimize=True)
    gif=ROOT/f"徳川家康_防御_{action}_preview-v1.gif"
    if gif.exists(): raise FileExistsError(f"refusing to overwrite {gif.name}")
    frames[0].save(gif,save_all=True,append_images=frames[1:],duration=110,loop=0,disposal=2)
    hashes=[hashlib.sha256(f.tobytes()).hexdigest() for f in frames]
    diffs=[]
    for i in range(1,len(frames)):
        diff=ImageChops.difference(frames[i-1],frames[i])
        diffs.append(sum(ImageStat.Stat(diff).sum))
    qa["actions"][action]={"sprite":name,"frames":count,"size":list(strip.size),
      "sha256":hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),"unique_frames":len(set(hashes)),
      "source":source_name,"source_size":list(src.size),"preview_gif":gif.name,
      "frames_detail":details,"adjacent_pixel_difference_sum":diffs,
      "notes":"候補のみ。ゲーム組み込み・左右向き・実速度・当たり判定は未確認。"}
    # Compact contact grid preserving all frames for visual review.
    thumb_size=(256,192)
    thumbs=[f.resize(thumb_size,Image.Resampling.LANCZOS) for f in frames]
    ncols=min(4,count); nrows=(count+ncols-1)//ncols
    grid=Image.new("RGB",(ncols*thumb_size[0],nrows*thumb_size[1]),(255,0,255))
    for i,t in enumerate(thumbs): grid.paste(t,((i%ncols)*thumb_size[0],(i//ncols)*thumb_size[1]))
    review=ROOT/f"徳川家康_防御_{action}_review-v1.png"
    if review.exists(): raise FileExistsError(f"refusing to overwrite {review.name}")
    grid.save(review,optimize=True)

qa_path=ROOT/"徳川家康_防御_QA-v1.json"
if qa_path.exists(): raise FileExistsError("refusing to overwrite QA")
qa_path.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({k:{"frames":v["frames"],"size":v["size"],"unique":v["unique_frames"],"min_adjacent_diff":min(v["adjacent_pixel_difference_sum"])} for k,v in qa["actions"].items()},ensure_ascii=False))

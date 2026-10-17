from pathlib import Path
from PIL import Image,ImageFilter,ImageChops,ImageStat
import json,hashlib
ROOT=Path(__file__).parent
SRC=ROOT/"徳川家康_防御_受け流し_source-v2.png"
OUT=ROOT/"徳川家康_防御_受け流し_8コマ_v4.png"
GIF=ROOT/"徳川家康_防御_受け流し_preview-v4.gif"
GRID=ROOT/"徳川家康_防御_受け流し_review-v4.png"
QA=ROOT/"徳川家康_防御_受け流し_QA-v4.json"
if not SRC.exists():raise FileNotFoundError(SRC)
for p in (OUT,GIF,GRID,QA):
 if p.exists():raise FileExistsError(f"refusing to overwrite {p.name}")
src=Image.open(SRC).convert("RGB")
if src.size!=(1536,1024):raise ValueError(src.size)
row_bounds=[(0,272),(272,510),(510,750),(750,1024)]
frames=[];details=[]
for i in range(8):
 col=i%2;row=i//2;x0=col*768;x1=(col+1)*768;y0,y1=row_bounds[row]
 tile=src.crop((x0,y0,x1,y1));p=tile.load();mask=Image.new("L",tile.size,0);q=mask.load()
 for y in range(tile.height):
  for x in range(tile.width):
   r,g,b=p[x,y]
   if not(r>=178 and b>=178 and g<=90 and g*2<min(r,b)):q[x,y]=255
 mask=mask.filter(ImageFilter.MinFilter(3));w,h=mask.size;a=mask.load();seen=bytearray(w*h);comps=[]
 for y in range(h):
  for x in range(w):
   k=y*w+x
   if a[x,y]<32 or seen[k]:continue
   seen[k]=1;stack=[k];ids=[];minx=w;miny=h;maxx=-1;maxy=-1
   while stack:
    z=stack.pop();xx=z%w;yy=z//w;ids.append(z)
    minx=min(minx,xx);miny=min(miny,yy);maxx=max(maxx,xx);maxy=max(maxy,yy)
    for dy in (-1,0,1):
     ny=yy+dy
     if 0<=ny<h:
      for dx in (-1,0,1):
       nx=xx+dx
       if (dx or dy) and 0<=nx<w:
        nz=ny*w+nx
        if not seen[nz] and a[nx,ny]>=32:seen[nz]=1;stack.append(nz)
   comps.append((len(ids),ids,(minx,miny,maxx+1,maxy+1)))
 if not comps:raise ValueError(f"empty frame {i+1}")
 comps.sort(key=lambda c:c[0],reverse=True)
 # Keep the connected character+katana silhouette; remove detached panel-overlap specks.
 selected=set(comps[0][1])
 for size,ids,_ in comps[1:]:
  if size>50:selected.update(ids)
  else:
   for z in ids:a[z%w,z//w]=0
 for y in range(h):
  for x in range(w):
   if y*w+x not in selected:a[x,y]=0
 bb=mask.getbbox()
 crop=tile.crop(bb);alpha=mask.crop(bb);bw,bh=crop.size;scale=min(188/bh,480/bw)
 nw=max(1,round(bw*scale));nh=max(1,round(bh*scale))
 crop=crop.resize((nw,nh),Image.Resampling.LANCZOS);alpha=alpha.resize((nw,nh),Image.Resampling.LANCZOS)
 al=alpha.load();lower=[x for y in range(round(nh*.82),nh) for x in range(nw) if al[x,y]>=32]
 foot=sum(lower)/len(lower);px=round(256-foot);py=363-nh
 cell=Image.new("RGBA",(512,384),(255,0,255,255));fg=crop.convert("RGBA");fg.putalpha(alpha);cell.alpha_composite(fg,(px,py));rgb=cell.convert("RGB")
 edge=any(rgb.getpixel((x,y))!=(255,0,255) for x,y in [(x,0) for x in range(512)]+[(x,383) for x in range(512)]+[(0,y) for y in range(384)]+[(511,y) for y in range(384)])
 frames.append(rgb);details.append({"frame":i+1,"source_row_y":[y0,y1],"source_bbox":[x0+bb[0],y0+bb[1],x0+bb[2],y0+bb[3]],"largest_components":[c[0] for c in comps[:3]],"removed_small_components":[c[0] for c in comps[1:] if c[0]<=50],"output_bbox":[px,py,px+nw,py+nh],"foot_anchor":[256,363],"frame_edge_contact":edge})
strip=Image.new("RGB",(4096,384),(255,0,255))
for i,f in enumerate(frames):strip.paste(f,(512*i,0))
strip.save(OUT,optimize=True);frames[0].save(GIF,save_all=True,append_images=frames[1:],duration=110,loop=0,disposal=2)
grid=Image.new("RGB",(1024,384),(255,0,255))
for i,f in enumerate(frames):grid.paste(f.resize((256,192),Image.Resampling.LANCZOS),((i%4)*256,(i//4)*192))
grid.save(GRID,optimize=True)
hashes=[hashlib.sha256(f.tobytes()).hexdigest() for f in frames]
diffs=[sum(ImageStat.Stat(ImageChops.difference(frames[i-1],frames[i])).sum) for i in range(1,8)]
QA.write_text(json.dumps({"sprite":OUT.name,"preview_gif":GIF.name,"review_grid":GRID.name,"frames":8,"size":list(strip.size),"unique_frames":len(set(hashes)),"frame_details":details,"adjacent_pixel_difference_sum":diffs,"candidate_only":True,"integrated":False,"notes":"Per-row crop bounds adjusted to source character gaps; detached components under 51px removed. Runtime/hitbox not verified."},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"frames":len(frames),"unique":len(set(hashes)),"edge_contact":sum(d["frame_edge_contact"] for d in details),"diff_min":min(diffs),"removed":[d["removed_small_components"] for d in details]},ensure_ascii=True))

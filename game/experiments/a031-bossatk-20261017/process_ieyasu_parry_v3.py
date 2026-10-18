from pathlib import Path
from PIL import Image, ImageFilter, ImageChops, ImageStat
import json, hashlib

ROOT=Path(__file__).parent; SRC=ROOT/"徳川家康_防御_受け流し_source-v2.png"
OUT=ROOT/"徳川家康_防御_受け流し_8コマ_v3.png"
GIF=ROOT/"徳川家康_防御_受け流し_preview-v3.gif"
GRID=ROOT/"徳川家康_防御_受け流し_review-v3.png"
QA=ROOT/"徳川家康_防御_受け流し_QA-v3.json"
CELL=(512,384); W,H=1536,1024
if not SRC.exists(): raise FileNotFoundError(SRC)
for p in (OUT,GIF,GRID,QA):
 if p.exists(): raise FileExistsError(f"refusing to overwrite {p.name}")
src=Image.open(SRC).convert("RGB")
if src.size!=(W,H): raise ValueError(f"unexpected source size {src.size}")
frames=[]; details=[]
for i in range(8):
 col=i%2; row=i//2
 x0=round(col*W/2); x1=round((col+1)*W/2)
 nominal0=round(row*H/4); nominal1=round((row+1)*H/4)
 y0=max(0,nominal0-18); y1=min(H,nominal1+18)
 tile=src.crop((x0,y0,x1,y1)); p=tile.load()
 mask=Image.new("L",tile.size,0); q=mask.load()
 for y in range(tile.height):
  for x in range(tile.width):
   r,g,b=p[x,y]
   if not (r>=178 and b>=178 and g<=90 and g*2<min(r,b)): q[x,y]=255
 mask=mask.filter(ImageFilter.MinFilter(3))
 mw,mh=mask.size; a=mask.load(); seen=bytearray(mw*mh); comps=[]
 for y in range(mh):
  for x in range(mw):
   k=y*mw+x
   if a[x,y]<32 or seen[k]: continue
   seen[k]=1; stack=[k]; ids=[]; sx=0; sy=0; minx=mw; miny=mh; maxx=-1; maxy=-1
   while stack:
    z=stack.pop(); xx=z%mw; yy=z//mw; ids.append(z); sx+=xx; sy+=yy
    minx=min(minx,xx); miny=min(miny,yy); maxx=max(maxx,xx); maxy=max(maxy,yy)
    for dy in (-1,0,1):
     ny=yy+dy
     if 0<=ny<mh:
      for dx in (-1,0,1):
       nx=xx+dx
       if (dx or dy) and 0<=nx<mw:
        nz=ny*mw+nx
        if not seen[nz] and a[nx,ny]>=32: seen[nz]=1;stack.append(nz)
   comps.append((len(ids),ids,(minx,miny,maxx+1,maxy+1),sx/len(ids),sy/len(ids)))
 if not comps: raise ValueError(f"empty frame {i+1}")
 comps.sort(key=lambda z:z[0],reverse=True); main=comps[0][0]
 keep=[c for c in comps if c[0]>=max(60,main*0.02) and nominal0-12<=c[4]+y0<=nominal1+12]
 selected=set()
 for c in keep:
  for z in c[1]: selected.add(z)
 for y in range(mh):
  for x in range(mw):
   if y*mw+x not in selected: a[x,y]=0
 bb=mask.getbbox()
 if not bb: raise ValueError(f"empty selected mask frame {i+1}")
 crop=tile.crop(bb); alpha=mask.crop(bb); bw,bh=crop.size
 scale=min(188/bh,480/bw); nw=max(1,round(bw*scale)); nh=max(1,round(bh*scale))
 crop=crop.resize((nw,nh),Image.Resampling.LANCZOS); alpha=alpha.resize((nw,nh),Image.Resampling.LANCZOS)
 al=alpha.load(); lower=[x for y in range(max(0,round(nh*.82)),nh) for x in range(nw) if al[x,y]>=32]
 foot=sum(lower)/len(lower); px=round(256-foot); py=363-nh
 cell=Image.new("RGBA",CELL,(255,0,255,255)); fg=crop.convert("RGBA");fg.putalpha(alpha);cell.alpha_composite(fg,(px,py))
 rgb=cell.convert("RGB")
 edge=any(rgb.getpixel((x,y))!=(255,0,255) for x,y in [(x,0) for x in range(512)]+[(x,383) for x in range(512)]+[(0,y) for y in range(384)]+[(511,y) for y in range(384)])
 frames.append(rgb); details.append({"frame":i+1,"grid_cell":[col+1,row+1],"row_overlap_px":18,"source_bbox":[x0+bb[0],y0+bb[1],x0+bb[2],y0+bb[3]],"kept_components":[c[0] for c in keep],"output_bbox":[px,py,px+nw,py+nh],"foot_anchor":[256,363],"frame_edge_contact":edge})
strip=Image.new("RGB",(512*8,384),(255,0,255))
for i,f in enumerate(frames):strip.paste(f,(512*i,0))
strip.save(OUT,optimize=True)
frames[0].save(GIF,save_all=True,append_images=frames[1:],duration=110,loop=0,disposal=2)
grid=Image.new("RGB",(4*256,2*192),(255,0,255))
for i,f in enumerate(frames):grid.paste(f.resize((256,192),Image.Resampling.LANCZOS),((i%4)*256,(i//4)*192))
grid.save(GRID,optimize=True)
hashes=[hashlib.sha256(f.tobytes()).hexdigest() for f in frames]
diffs=[sum(ImageStat.Stat(ImageChops.difference(frames[i-1],frames[i])).sum) for i in range(1,8)]
qa={"sprite":OUT.name,"preview_gif":GIF.name,"review_grid":GRID.name,"frames":8,"size":list(strip.size),"unique_frames":len(set(hashes)),"frame_details":details,"adjacent_pixel_difference_sum":diffs,"candidate_only":True,"integrated":False,"notes":"Overlapped source row crops by 18px and retained the main character components to remove adjacent-row fragments. Game runtime and hitbox not verified."}
QA.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"size":strip.size,"unique":len(set(hashes)),"edge_contact":sum(d["frame_edge_contact"] for d in details),"diff_min":min(diffs),"files":[OUT.name,GIF.name,GRID.name,QA.name]},ensure_ascii=True))

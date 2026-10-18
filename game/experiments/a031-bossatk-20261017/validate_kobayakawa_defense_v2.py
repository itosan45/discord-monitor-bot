from pathlib import Path
from PIL import Image
import hashlib, json

root=Path(__file__).parent
qa=json.loads((root/"小早川秀秋_防御_QA-v2.json").read_text(encoding="utf-8"))
result={}; failures=[]
for action,meta in qa["actions"].items():
    image=Image.open(root/meta["sprite"]).convert("RGB")
    cell_count=meta["frames"]
    hashes=[]; edge_cells=[]; magenta_pixels=0
    for i in range(cell_count):
        frame=image.crop((i*512,0,(i+1)*512,384))
        hashes.append(hashlib.sha256(frame.tobytes()).hexdigest())
        magenta_pixels += sum(1 for p in frame.getdata() if p==(255,0,255))
        edge_cells.append(any(frame.getpixel((x,y))!=(255,0,255) for x,y in
            [(x,0) for x in range(512)]+[(x,383) for x in range(512)]+
            [(0,y) for y in range(384)]+[(511,y) for y in range(384)]))
    gif=Image.open(root/meta["preview_gif"]); gif_frames=0
    try:
        while True:
            gif.seek(gif_frames); gif_frames+=1
    except EOFError:
        pass
    row={"size":list(image.size),"frames":cell_count,"gif_frames":gif_frames,
         "unique_frames":len(set(hashes)),"edge_contact_cells":sum(edge_cells),
         "pure_magenta_pixels":magenta_pixels,
         "sha256":hashlib.sha256((root/meta["sprite"]).read_bytes()).hexdigest()}
    result[action]=row
    if image.size!=(cell_count*512,384) or gif_frames!=cell_count or len(set(hashes))!=cell_count or any(edge_cells):
        failures.append(action)
print(json.dumps({"failures":failures,"actions":result},ensure_ascii=False,indent=2))
if failures: raise SystemExit(1)

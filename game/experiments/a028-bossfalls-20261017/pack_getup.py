from pathlib import Path
import cv2
import numpy as np
from PIL import Image

src = Path(r'C:\Users\user\.codex\generated_images\01a13ec6-5bd1-71a0-abbd-bbcae834c824\exec-a8f93e5c-555a-478b-ae3f-2c4d440ce987.png')
out = Path(__file__).parent / '井伊直政_起き上がり_4コマ_v1.png'
image = Image.open(src).convert('RGB')
if image.size != (1254, 1254):
    raise SystemExit(f'unexpected source size: {image.size}')
arr = np.asarray(image)
# The generated four poses are free-positioned on a single canvas, not clipped grid cells.
bg = ((arr[:,:,0] >= 190) & (arr[:,:,1] <= 70) & (arr[:,:,2] >= 190)).astype(np.uint8)
n, labels, stats, _ = cv2.connectedComponentsWithStats(bg, connectivity=4)
edge_ids = set(np.unique(np.concatenate([labels[0,:], labels[-1,:], labels[:,0], labels[:,-1]])).tolist())
fg = ((labels == 0) | ~np.isin(labels, list(edge_ids))).astype(np.uint8)
n, components, boxes, centers = cv2.connectedComponentsWithStats(fg, connectivity=8)
poses = sorted([i for i in range(1,n) if boxes[i,cv2.CC_STAT_AREA] > 15000], key=lambda i:(centers[i][1] // 627, centers[i][0] // 627))
if len(poses) != 4:
    raise SystemExit(f'expected four connected poses, found {len(poses)}')
canvas = Image.new('RGB', (1536,384), (255,0,255))
scale = 188 / 506  # match existing Ii Naomasa idle height (~188 px)
report=[]
for frame, label in enumerate(poses,1):
    x,y,w,h,area = boxes[label].tolist()
    mask = components[y:y+h,x:x+w] == label
    crop = arr[y:y+h,x:x+w].copy()
    crop[~mask] = (255,0,255)
    im = Image.fromarray(crop).resize((round(w*scale),round(h*scale)),Image.Resampling.LANCZOS)
    # Resize mask with nearest-neighbour to avoid bringing back the generator backdrop.
    im_mask = Image.fromarray((mask.astype(np.uint8)*255)).resize(im.size,Image.Resampling.NEAREST)
    xdst=(384-im.width)//2; ydst=364-im.height
    if xdst<0 or ydst<0: raise SystemExit('frame does not fit')
    canvas.paste(im,(xdst + 384*(frame-1),ydst),im_mask)
    report.append({'frame':frame,'source_bbox':(x,y,x+w,y+h),'source_wh':(w,h),'component_px':area,'scaled_wh':im.size,'dest_xy':(xdst,ydst)})
canvas.save(out,format='PNG',optimize=True)
print('source',image.size,'scale',scale,'output',out,canvas.size)
for row in report: print(row)





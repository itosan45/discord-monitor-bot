"""Register boss artwork by foot contact, independent of weapon bounding boxes.

Animation scales are constant across a strip, so crouches and leaps retain their
poses. Original PNGs and packed image rectangles are never altered here.
"""
import numpy as np
from scipy import ndimage as ndi

SCALE = {
    'boss1': {'a1': 1.28, 'big': 1.12},
    'boss2': {'a1': 1.06},
    'boss4': {'big': 1.50},
    'boss7': {'a1': 1.20, 'big': 1.28, 'dash': 0.90},
    'boss8': {'a1': 1.15, 'big': 1.08},
    'boss9': {'a1': 1.50, 'big': 1.20, 'dash': 1.25},
}

def foot_contact(atlas, q):
    x,y,w,h,ox,oy,s = q
    a = np.array(atlas.crop((x,y,x+w,y+h)))[:,:,3] > 100
    # Exclude thin weapons; keep both legs even when opening separates a foot.
    opened = ndi.binary_opening(a, structure=np.ones((5,5)))
    lab,n = ndi.label(opened)
    sizes = ndi.sum(opened,lab,range(1,n+1))
    keep = np.zeros_like(a)
    for j,sz in enumerate(sizes,1):
        if sz >= max(50, sizes.max()*.04): keep |= lab == j
    ys,xs = np.where(keep)
    bottom = ys.max()
    feet = xs[ys >= bottom-6]
    return (float(feet.min()+feet.max())/2, float(bottom))

def register_boss(atlas, meta, key):
    for an in ('idle','walk','hit','a1','big','dash'):
        if an not in meta: continue
        scale = SCALE.get(key,{}).get(an,1.0)
        for i,q in enumerate(meta[an]):
            fx,fy = foot_contact(atlas,q)
            old_y = q[5]+fy*q[6]
            q[6] = round(q[6]*scale,4)
            q[4] = round(-fx*q[6],2)
            # Honda's leap frames intentionally lift both feet. Their airborne
            # artwork remains airborne, rather than snapping to the ground.
            lift = min(0,old_y-19) if key=='boss7' and an=='big' and i in (3,4) else 0
            q[5] = round(-fy*q[6]+lift*scale,2)
    return meta

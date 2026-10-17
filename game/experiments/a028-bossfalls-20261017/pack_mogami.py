from pathlib import Path
import cv2, numpy as np
from PIL import Image
root=Path(__file__).parent
repo=Path(__file__).resolve().parents[3]
ref=Image.open(repo/'assets'/'sprites'/'最上義光_待機_4コマ.png')
refa=np.asarray(ref.convert('RGB'))
refbg=((refa[:,:,0]>=190)&(refa[:,:,1]<=70)&(refa[:,:,2]>=190)).astype(np.uint8)
n,rl,_,_=cv2.connectedComponentsWithStats(refbg,connectivity=4); re=set(np.unique(np.concatenate([rl[0,:],rl[-1,:],rl[:,0],rl[:,-1]])).tolist())
refmask=((rl==0)|~np.isin(rl,list(re)))
ys,xs=np.where(refmask[:,0:384]); target_h=int(ys.max()-ys.min()+1); baseline=int(ys.max())
print('reference target height',target_h,'baseline',baseline)

def pack(action, source_name, out_name, frame_number):
    src=Image.open(root/source_name).convert('RGB')
    a=np.asarray(src)
    bg=((a[:,:,0]>=190)&(a[:,:,1]<=70)&(a[:,:,2]>=190)).astype(np.uint8)
    n,l,_,_=cv2.connectedComponentsWithStats(bg,connectivity=4)
    edges=set(np.unique(np.concatenate([l[0,:],l[-1,:],l[:,0],l[:,-1]])).tolist())
    fg=((l==0)|~np.isin(l,list(edges))).astype(np.uint8)
    n,components,stats,centers=cv2.connectedComponentsWithStats(fg,connectivity=8)
    poses=[i for i in range(1,n) if stats[i,cv2.CC_STAT_AREA]>15000]
    poses.sort(key=lambda i:(int(centers[i][1]//627),int(centers[i][0]//627)))
    if len(poses)!=4: raise SystemExit(f'{action}: expected 4 poses; got {len(poses)}')
    standing_h=max(int(stats[poses[0],cv2.CC_STAT_HEIGHT]), int(stats[poses[3],cv2.CC_STAT_HEIGHT]))
    scale=target_h/standing_h
    canvas=Image.new('RGB',(1536,384),(255,0,255)); rows=[]
    for frame,label in enumerate(poses,1):
        x,y,w,h,area=stats[label].tolist()
        m=components[y:y+h,x:x+w]==label
        crop=a[y:y+h,x:x+w].copy(); crop[~m]=(255,0,255)
        im=Image.fromarray(crop).resize((round(w*scale),round(h*scale)),Image.Resampling.LANCZOS)
        imask=Image.fromarray((m.astype(np.uint8)*255)).resize(im.size,Image.Resampling.NEAREST)
        xd=(384-im.width)//2; yd=baseline+1-im.height
        if xd<0 or yd<0 or yd+im.height>384: raise SystemExit(f'{action} frame {frame} out of bounds')
        canvas.paste(im,(xd+384*(frame-1),yd),imask)
        rows.append({'frame':frame,'source_bbox':[x,y,x+w,y+h],'source_wh':[w,h],'area':area,'scaled_wh':list(im.size),'dest_xy':[xd,yd]})
    out=root/out_name; canvas.save(out,format='PNG',optimize=True)
    print(action,'scale',scale,'output',out,'sheet',canvas.size)
    for row in rows: print(row)

pack('転倒','mogami_source_fall.png','最上義光_転倒_4コマ_v1.png',4)
pack('起き上がり','mogami_source_getup.png','最上義光_起き上がり_4コマ_v1.png',4)


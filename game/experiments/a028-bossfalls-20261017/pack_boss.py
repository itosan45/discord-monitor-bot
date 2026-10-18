from pathlib import Path
import argparse, cv2, numpy as np
from PIL import Image
p=argparse.ArgumentParser(); p.add_argument('--character',required=True); args=p.parse_args()
root=Path(__file__).parent; repo=Path(__file__).resolve().parents[3]; name=args.character
ref=Image.open(repo/'assets'/'sprites'/f'{name}_待機_4コマ.png').convert('RGB'); ra=np.asarray(ref)
rbg=((ra[:,:,0]>=190)&(ra[:,:,1]<=70)&(ra[:,:,2]>=190)).astype(np.uint8); n,rl,_,_=cv2.connectedComponentsWithStats(rbg,connectivity=4); re=set(np.unique(np.r_[rl[0,:],rl[-1,:],rl[:,0],rl[:,-1]])); rm=(rl==0)|~np.isin(rl,list(re)); ys,xs=np.where(rm[:,:384]); target_h=int(ys.max()-ys.min()+1); baseline=int(ys.max()); print('reference',target_h,baseline)

def pose_data(action):
 src=Image.open(root/f'source_{name}_{action}.png').convert('RGB'); a=np.asarray(src); bg=((a[:,:,0]>=190)&(a[:,:,1]<=70)&(a[:,:,2]>=190)).astype(np.uint8); n,l,_,_=cv2.connectedComponentsWithStats(bg,connectivity=4); e=set(np.unique(np.r_[l[0,:],l[-1,:],l[:,0],l[:,-1]])); fg=((l==0)|~np.isin(l,list(e))).astype(np.uint8); n,c,s,cent=cv2.connectedComponentsWithStats(fg,connectivity=8); ids=[i for i in range(1,n) if s[i,cv2.CC_STAT_AREA]>15000]; ids.sort(key=lambda i:(cent[i][1]>=627,cent[i][0]>=627));
 if len(ids)!=4: raise SystemExit(f'{action}: expected 4 poses, found {len(ids)}')
 return src,a,c,s,ids
fall=pose_data('fall'); getup=pose_data('getup'); scale=target_h/max(fall[3][fall[4][0],cv2.CC_STAT_HEIGHT],getup[3][getup[4][-1],cv2.CC_STAT_HEIGHT]); print('scale',scale)
for action,(src,a,components,stats,ids) in [('fall',fall),('getup',getup)]:
 canvas=Image.new('RGB',(1536,384),(255,0,255));
 for frame,label in enumerate(ids,1):
  x,y,w,h,area=stats[label].tolist(); mask=components[y:y+h,x:x+w]==label; crop=a[y:y+h,x:x+w].copy(); crop[~mask]=(255,0,255); im=Image.fromarray(crop).resize((round(w*scale),round(h*scale)),Image.Resampling.LANCZOS); m=Image.fromarray((mask.astype(np.uint8)*255)).resize(im.size,Image.Resampling.NEAREST); xd=(384-im.width)//2; yd=baseline+1-im.height
  if xd<0 or yd<0 or yd+im.height>384: raise SystemExit(f'{action} frame {frame} out of bounds')
  canvas.paste(im,(xd+384*(frame-1),yd),m); print(action,frame,'source',(x,y,x+w,y+h),'scaled',im.size,'dest',(xd,yd),'area',area)
 label = {"fall":"\u8ee2\u5012", "getup":"\u8d77\u304d\u4e0a\u304c\u308a"}[action]
 canvas.save(root / (name+"_"+label+"_4\u30b3\u30de_v1.png"),format="PNG",optimize=True)



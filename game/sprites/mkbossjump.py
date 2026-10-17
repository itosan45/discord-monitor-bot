"""ボス8人のジャンプ4コマ(assets/sprites/<名前>_ジャンプ_4コマ_v2.png)を、別キー bjump_<boss> のアトラスにする。
既存のボスのアトラス(atlas_boss*.webp)と元PNGは変更しない。
- 縮尺: ジャンプの原画は待機より大きく描かれているので、4コマ目(脚を伸ばした姿勢)の高さが TARGET_H になるようそろえる。
- 位置: 各コマとも足の接地点(foot_contact)を原点にする。跳躍の高さはゲーム側の z で付ける。
使い方: cd game/sprites && python3 mkbossjump.py"""
import io,json,os,sys
import numpy as np
from PIL import Image
sys.argv=sys.argv[:1]
import mk
from boss_registration import foot_contact
TARGET_H=205  # 待機は高さ190にそろえている。脚を伸ばした跳躍姿勢は少し高い
def build(h):
    n=mk.BOSS[h];a=mk.keyim(Image.open(mk.SRC+n+'_ジャンプ_4コマ_v2.png'));cw=a.shape[1]//4
    cells=[mk.clean(a[:,i*cw:(i+1)*cw]) for i in range(4)]
    ys=np.where(cells[3][...,3]>40)[0];s=TARGET_H/(ys.max()-ys.min()+1)
    ims=[]
    for c in cells:
        ys,xs=np.where(c[...,3]>40);x0,x1,y0,y1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
        im=Image.fromarray(c[y0:y1,x0:x1],'RGBA');im=im.resize((max(1,round(im.width*s)),max(1,round(im.height*s))),Image.LANCZOS);ims.append(im)
    AW=sum(i.width+2 for i in ims);AH=max(i.height for i in ims)
    atlas=Image.new('RGBA',(AW,AH),(0,0,0,0));meta={'jump':[]};x=0
    for im in ims:
        atlas.paste(im,(x,0));q=[x,0,im.width,im.height,0,0,1.0];fx,fy=foot_contact(atlas,q);q[4]=round(-fx,2);q[5]=round(-fy,2);meta['jump'].append(q);x+=im.width+2
    b=io.BytesIO();atlas.save(b,'WEBP',quality=52,method=4);return atlas,meta,b.getvalue()
if __name__=='__main__':
    allm=json.load(open('sprmeta.json'))
    for h in mk.BOSS:
        at,meta,by=build(h);k='bjump_'+h;open(f'atlas_{k}.webp','wb').write(by);allm[k]=meta;print(k,at.size,len(by)//1024,'KB')
    json.dump(allm,open('sprmeta.json','w'))

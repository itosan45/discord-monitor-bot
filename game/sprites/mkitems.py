import os,numpy as np,json,io
from PIL import Image
from mk import keyim
S=os.path.join(os.path.dirname(os.path.abspath(__file__)),'../../assets/sprites/')
IT={'onigiri':'回復アイテム_おにぎり_v1.png','hyorou':'回復アイテム_兵糧_v1.png','sushi':'回復アイテム_寿司_v1.png','sake':'回復アイテム_酒_v1.png','manju':'回復アイテム_饅頭_v1.png',
 'w_yoto':'拾得武器_妖刀_v1.png','w_yumi':'拾得武器_弓矢_v1.png','w_ono':'拾得武器_斧_v1.png','w_konbou':'拾得武器_棍棒_v1.png','w_takeyari':'拾得武器_竹槍_v1.png','w_naginata':'拾得武器_薙刀_v1.png','w_kusari':'拾得武器_鎖鎌_v1.png','w_odachi':'拾得武器_長剣_v1.png'}
items=[];meta={}
for k,f in IT.items():
    a=keyim(Image.open(S+f));m=a[...,3]>60;ys,xs=np.where(m);x0,x1,y0,y1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
    # grip = opaque pixel closest to bottom-left, tip = closest to top-right (for weapons)
    d1=(xs-x0)+(y1-ys);i1=np.argmin(d1);d2=(x1-xs)+(ys-y0);i2=np.argmin(d2)
    g=(xs[i1]-x0,ys[i1]-y0);t=(xs[i2]-x0,ys[i2]-y0)
    if k=='w_kusari':g=(int((x1-x0)*0.12),int((y1-y0)*0.9))
    im=Image.fromarray(a[y0:y1,x0:x1],'RGBA');sc=1.0 if k.startswith('w_') else 0.5
    im=im.resize((round(im.width*sc),round(im.height*sc)),Image.LANCZOS);items.append((k,im,[round(g[0]*sc),round(g[1]*sc),round(t[0]*sc),round(t[1]*sc)]))
AW=1024;x=y=rh=0;atl=[]
for k,im,gt in items:
    if x+im.width>AW:x=0;y+=rh+2;rh=0
    atl.append((k,im,gt,x,y));x+=im.width+2;rh=max(rh,im.height)
at=Image.new('RGBA',(AW,y+rh))
for k,im,gt,px,py in atl:at.paste(im,(px,py));meta[k]=[px,py,im.width,im.height]+gt
b=io.BytesIO();at.save(b,'WEBP',quality=70,method=4);open('atlas_items.webp','wb').write(b.getvalue());at.save('atlas_items.png')
M=json.load(open('sprmeta.json'));M['items']={'idle':[[0,0,1,1,0,0,1]],'icons':meta};json.dump(M,open('sprmeta.json','w'))
print(at.size,len(b.getvalue())//1024,'KB');print(meta)

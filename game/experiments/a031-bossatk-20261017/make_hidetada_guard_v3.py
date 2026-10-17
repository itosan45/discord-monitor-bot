from PIL import Image,ImageDraw
from pathlib import Path
import numpy as np,cv2,hashlib,json
p=Path(__file__).resolve().parent
name='徳川秀忠_防御_構え_6コマ_v2.png'; im=Image.open(p/name).convert('RGB'); frames=[im.crop((i*512,0,(i+1)*512,384)) for i in range(6)]
fr=frames[4];a=np.asarray(fr).copy();mask=np.any(a!=[255,0,255],axis=2).astype('uint8');n,l,s,c=cv2.connectedComponentsWithStats(mask,8)
main=int(np.argmax(s[1:,cv2.CC_STAT_AREA])+1);mainbox=s[main,:4]
removed=[]
for lab in range(1,n):
 area=int(s[lab,cv2.CC_STAT_AREA]); x,y,w,h=map(int,s[lab,:4])
 if lab==main:continue
 # this one clearly detached speck, spatially isolated from the main sprite
 if area<=100 and (x+w<mainbox[0]-8 or x>mainbox[0]+mainbox[2]+8 or y+h<mainbox[1]-8 or y>mainbox[1]+mainbox[3]+8):
  a[l==lab]=[255,0,255];removed.append({'area':area,'bbox':[x,y,w,h]})
frames[4]=Image.fromarray(a)
out=Image.new('RGB',(3072,384),(255,0,255))
for i,f in enumerate(frames):out.paste(f,(512*i,0))
outname='徳川秀忠_防御_構え_6コマ_v3.png';out.save(p/outname,optimize=True)
cols=4;tw=256;th=192;grid=Image.new('RGB',(1024,432),(42,42,48));d=ImageDraw.Draw(grid)
for i,f in enumerate(frames):
 x=(i%cols)*tw;y=(i//cols)*(th+24);grid.paste(f.resize((tw,th),Image.Resampling.NEAREST),(x,y));d.text((x+4,y+th+2),f'{i+1:02}',fill='white')
gridname='徳川秀忠_防御_構え_review-v3.png';grid.save(p/gridname,optimize=True)
gifname='徳川秀忠_防御_構え_preview-v3.gif';frames[0].save(p/gifname,save_all=True,append_images=frames[1:],duration=110,loop=0,optimize=False)
qa=json.loads((p/'徳川秀忠_防御_QA-v2.json').read_text(encoding='utf-8'))
qa['actions']['構え']['sprite']=outname;qa['actions']['構え']['sha256']=hashlib.sha256((p/outname).read_bytes()).hexdigest();qa['actions']['構え']['review_grid']=gridname;qa['actions']['構え']['preview_gif']=gifname
qa['actions']['構え']['notes']+=' Frame 5 has one isolated 72-pixel speck removed; original v1/v2 candidates retained.'
qa['actions']['構え']['isolated_cleanup_v3']=removed
(p/'徳川秀忠_防御_QA-v3.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
print(outname,hashlib.sha256((p/outname).read_bytes()).hexdigest(),'removed',removed)

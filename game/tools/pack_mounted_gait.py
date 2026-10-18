"""Pack versioned whole-horse gait keys; preserve every existing PNG/atlas."""
import argparse,json,shutil,sys
from pathlib import Path
import numpy as np
from PIL import Image

p=argparse.ArgumentParser();p.add_argument('hero');p.add_argument('strip',type=Path);p.add_argument('--hand',nargs=2,type=float,required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[2];spr=root/'game/sprites';key='mountwalk5_'+a.hero
im=Image.open(a.strip).convert('RGBA');assert im.height==256 and im.width==1024
sys.path.insert(0,str(spr));from mk import keyim
data=keyim(im)
for i in range(4):
 y,x=np.where(data[:,i*256:(i+1)*256,3]>100);assert len(x)>3000;assert min(x.min(),y.min(),255-x.max(),255-y.max())>=16
dest=root/'assets/sprites'/a.strip.name
if dest.exists():assert dest.read_bytes()==a.strip.read_bytes(),'Refuse existing PNG overwrite'
else:shutil.copyfile(a.strip,dest)
atlas=spr/f'atlas_{key}.webp'
if atlas.exists():assert np.array_equal(np.asarray(Image.open(atlas).convert('RGBA')),data),'Refuse existing atlas overwrite'
else:Image.fromarray(data).save(atlas,'WEBP',lossless=True)
scale=1.4;hx,hy=a.hand
meta=json.loads((spr/'sprmeta.json').read_text(encoding='utf-8'));meta[key]={'all':[[i*256,0,256,256,-128*scale,-230*scale,scale] for i in range(4)],'handAll':[[(hx-128)*scale,(hy-230)*scale] for _ in range(4)]}
(spr/'sprmeta.json').write_text(json.dumps(meta,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
print(key,im.size)

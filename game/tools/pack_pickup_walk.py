"""Add a versioned pickup-walk atlas without rebuilding other hero animations."""
import argparse,json,shutil,sys
from pathlib import Path
import numpy as np
from PIL import Image

parser=argparse.ArgumentParser();parser.add_argument('hero');parser.add_argument('strip',type=Path);parser.add_argument('--hand',nargs=2,type=float,required=True);args=parser.parse_args()
ROOT=Path(__file__).resolve().parents[2];SPR=ROOT/'game/sprites';key='walkbody3_'+args.hero
im=Image.open(args.strip).convert('RGBA');assert im.size==(2048,256)
sys.path.insert(0,str(SPR))
from mk import keyim
data=keyim(im)
destination=ROOT/'assets/sprites'/args.strip.name
if destination.exists():assert destination.read_bytes()==args.strip.read_bytes(),'Refuse to overwrite an existing PNG'
else:shutil.copyfile(args.strip,destination)
Image.fromarray(data).save(SPR/f'atlas_{key}.webp','WEBP',lossless=True)
# Match the existing hero walk height of 190 game pixels, independent of PNG padding.
heights=[]
for i in range(8):
 y,x=np.where(data[:,i*256:(i+1)*256,3]>100);assert len(x)>3000;assert min(x.min(),y.min(),255-x.max(),255-y.max())>=12;heights.append(int(y.max()-y.min()+1))
scale=190/max(heights);meta=json.loads((SPR/'sprmeta.json').read_text(encoding='utf-8'));meta[key]={'walk':[[i*256,0,256,256,-128*scale,-230*scale,scale] for i in range(8)]}
hands=json.loads((SPR/'hands.json').read_text(encoding='utf-8'));hx,hy=args.hand;hands[key]={'walk':[[(hx-128)*scale,(hy-230)*scale,None] for i in range(8)]}
(SPR/'sprmeta.json').write_text(json.dumps(meta,ensure_ascii=False,separators=(',',':')),encoding='utf-8');(SPR/'hands.json').write_text(json.dumps(hands,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
print(key,scale)

"""game_src.html + data/audio.json + sprites/*.json -> ../index.html (リポジトリ直下)。
使い方: cd game && python3 build.py
sprites/ に atlas_*.webp があれば ../gfx/ にコピーしてから組み立てる。"""
import json,os,shutil,glob,hashlib
H=os.path.dirname(os.path.abspath(__file__));REPO=os.path.dirname(H);GFX=os.path.join(REPO,'gfx')
data=json.load(open(os.path.join(H,'data','audio.json')))
for f in glob.glob(os.path.join(H,'sprites','atlas_*.webp')):shutil.copyfile(f,os.path.join(GFX,os.path.basename(f)))
def image_url(f):
    # Atlas metadata ships inside HTML. A cached atlas must be the exact bytes
    # used by that build, otherwise new frames can point beyond the old image.
    with open(f,'rb') as source:
        version=hashlib.sha256(source.read()).hexdigest()[:16]
    return 'gfx/'+os.path.basename(f)+'?v='+version

data['bg']={os.path.basename(f)[3:-5]:image_url(f) for f in sorted(glob.glob(os.path.join(GFX,'bg_*.webp')))}
data['spr']={os.path.basename(f)[6:-5]:image_url(f) for f in sorted(glob.glob(os.path.join(GFX,'atlas_*.webp')))}
data['sm']=json.load(open(os.path.join(H,'sprites','sprmeta.json')));data['hands']=json.load(open(os.path.join(H,'sprites','hands.json')))
miss=sorted(set(data['spr'])-set(data['sm']))
if miss:raise SystemExit('sprmeta.json に位置データが無い画像があります: %s'%miss)
s=open(os.path.join(H,'game_src.html'),encoding='utf-8').read().replace('__AUDIO__',json.dumps(data))
open(os.path.join(REPO,'index.html'),'w',encoding='utf-8').write(s)
print(len(s)/1e6,'MB html')

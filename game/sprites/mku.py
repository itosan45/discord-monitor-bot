# build unarmed (手ぶら) atlases <hero>_u, size-matched to the armed atlas
import json,os,sys,numpy as np
from PIL import Image
import mk
exec(open('bodyh.py').read().split("for h in sys.argv")[0].replace("M=json.load(open('sprmeta.json'))",""))
UA=[('idle','待機_4'),('walk','歩き_8'),('jump','ジャンプ_4'),('dash','ダッシュ_5'),('a1','攻撃A_5'),('a2','攻撃B_5'),('a3','攻撃C_5')]
def ufind(h,key):
    base=mk.HERO[h[:-2]]+'_手ぶら_'+key+'コマ'
    for suf in ['_v3','_v2','']:
        if os.path.exists(mk.SRC+base+suf+'.png'):return base+suf+'.png'
    return None

M=json.load(open('sprmeta.json'))
orig_find=mk.find
def f2(h,key):
    if h.endswith('_u'):return ufind(h,key)
    return orig_find(h,key)
mk.find=f2
OUT={}
for h in mk.HERO.copy():
    if h.endswith('_u'):continue
    hu=h+'_u';mk.HERO[hu]=mk.HERO[h];mk.NAME[hu]=mk.HERO[h]
    anims=[(a,k) for a,k in UA if ufind(hu,k)]
    if not any(a=='idle' for a,_ in anims):continue
    mk.ANIM=anims
    # reference body area from armed atlas
    img=Image.open('atlas_%s.png'%h).convert('RGBA')
    ref=np.median([body(img,q)[2] for q in M[h]['idle']+M[h]['walk'] if q and body(img,q)])
    for it in range(2):
        at,meta,by=mk.build(hu,Hg=190)
        at.save('atlas_%s.png'%hu);ia=at.convert('RGBA')
        for an,fr in meta.items():
            a=np.median([body(ia,q)[2] for q in fr if q and body(ia,q)])
            k=float(np.sqrt(ref/a)) if an in('idle','walk','jump') else float(np.sqrt(ref/a))*1.0
            mk.KFIX[(hu,an)]=mk.KFIX.get((hu,an),1.0)*max(0.6,min(1.6,k))
    at,meta,by=mk.build(hu,Hg=190);open('atlas_%s.webp'%hu,'wb').write(by);at.save('atlas_%s.png'%hu)
    M[hu]=meta;OUT[hu]={k:len(v) for k,v in meta.items()}
json.dump(M,open('sprmeta.json','w'));print(OUT)

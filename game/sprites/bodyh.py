import json,numpy as np,sys
from PIL import Image
from scipy import ndimage as nd
M=json.load(open('sprmeta.json'))
def body(img,q):
    x,y,w,h,ox,oy,s=q;a=np.array(img.crop((x,y,x+w,y+h)))[:,:,3]>100
    k=max(3,int(round(9/s)));b=nd.binary_opening(a,structure=np.ones((k,k)));lab,n=nd.label(b)
    if not n:return None
    sz=nd.sum(b,lab,range(1,n+1));b=lab==(1+int(np.argmax(sz)));ys,xs=np.where(b)
    return (ys.min()*s+oy, ys.max()*s+oy, b.sum()*s*s)
for h in sys.argv[1:] or ['yuki','kage','mitsu','nobu','shin','musashi']:
    img=Image.open('atlas_%s.png'%h).convert('RGBA');row=[]
    for an in ['idle','walk','a1','a2','a3','a4','dash','jatk','hit']:
        fr=[body(img,q) for q in M[h].get(an,[]) if q]
        fr=[f for f in fr if f]
        if fr:row.append('%s top%.0f area%.0fk'%(an,np.median([f[0] for f in fr]),np.median([f[2] for f in fr])/1000))
    print(h,' | '.join(row))

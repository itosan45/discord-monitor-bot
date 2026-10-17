#!/usr/bin/env python3
"""スプライトの大きさの検品(2026-10-17 オーナー「スプライトシートがそもそも小さく/大きく描かれているから、取り込む時点でサイズ調整するのを当たり前にやってくれ」)。
アトラスの各コマを実際の拡大率で測り、「体の高さ」(細い刀・飾り・効果を除いた本体の高さ)を待機の1コマ目と比べて、差の大きいコマを出す。
使い方: python3 game/tools/check_sprite_scale.py <キー...> [--tol 0.12]    (キー省略=ボス全部)
見方: 立ち姿の行(idle/walk/a1/order…)は待機とほぼ同じ高さのはず(±tol以内)。しゃがみ・跳躍・倒れのコマは低くてよいので、低い側は目で見て判断する。
大きい側(比 > 1+tol)は、取り込み時の拡大率のミスの可能性が高い。新しい絵を取り込んだら必ず実行して、sprmeta の拡大率(q[6])とオフセット(q[4],q[5])を同じ比率で直すこと。"""
import sys,json,os,argparse
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
H=os.path.dirname(os.path.abspath(__file__));REPO=os.path.dirname(os.path.dirname(H))
def body_h(c):
    a=c[...,3]>60
    if not a.any():return 0
    o=ndi.binary_opening(a,structure=np.ones((9,9)))  # 幅9px未満(刀・槍・飾り・光の筋)を消して本体だけにする
    ys=np.nonzero(o.any(1))[0]
    return (ys.max()-ys.min()+1) if len(ys) else 0
def main():
    ap=argparse.ArgumentParser();ap.add_argument('keys',nargs='*');ap.add_argument('--tol',type=float,default=0.12);a=ap.parse_args()
    M=json.load(open(os.path.join(REPO,'game/sprites/sprmeta.json')))
    keys=a.keys or [k for k in M if k.startswith('boss') or k in('masamune','munenori','ieyasu2','tenkai')]
    bad=0
    for k in keys:
        p=os.path.join(REPO,'gfx/atlas_%s.webp'%k)
        if not os.path.exists(p):continue
        A=np.array(Image.open(p).convert('RGBA'));S=M[k];ref=None
        if 'idle' in S:
            f=S['idle'][0];sx,sy,w,h=map(int,f[:4]);ref=body_h(A[sy:sy+h,sx:sx+w])*f[6]
        if not ref:continue
        for row,fr in S.items():
            if not isinstance(fr,list):continue
            hs=[]
            for f in fr:
                sx,sy,w,h=map(int,f[:4]);hs.append(body_h(A[sy:sy+h,sx:sx+w])*f[6]/ref)
            flag=[i for i,r in enumerate(hs) if r>1+a.tol]
            print('%-9s %-7s %s%s'%(k,row,' '.join('%.2f'%r for r in hs),('   <-- 大きい: '+','.join(map(str,flag))) if flag else ''))
            bad+=len(flag)
    print('大きすぎる疑いのコマ:',bad)
if __name__=='__main__':main()

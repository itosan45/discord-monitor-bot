#!/usr/bin/env python3
"""歩きのコマの横ずれ補正(2026-10-18 オーナー「政宗や柳生の歩き方が滑らかじゃない」)。
各コマの「胴体の横位置」(頭から腰あたりの不透明画素の横の中央値。刀・腕の振りは除く)を測り、全コマで同じ位置になるよう sprmeta のオフセット q[4] だけを直す。PNGは変えない。
使い方: python3 game/tools/stabilize_walk.py masamune munenori [--dry]"""
import json, sys
import numpy as np
from PIL import Image
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
META = ROOT / 'game' / 'sprites' / 'sprmeta.json'
keys = [a for a in sys.argv[1:] if not a.startswith('--')]
dry = '--dry' in sys.argv
M = json.load(open(META))
for k in keys:
    A = np.asarray(Image.open(ROOT / 'gfx' / f'atlas_{k}.webp').convert('RGBA'))
    fr = M[k]['walk']
    cx = []
    for f in fr:
        sx, sy, w, h = map(int, f[:4])
        a = A[sy:sy + h, sx:sx + w, 3] > 128
        ys = np.where(a.any(1))[0]
        top, bot = ys[0], ys[-1]
        hh = bot - top
        band = a[top + int(hh * 0.12):top + int(hh * 0.55)]  # 頭〜腰(刀の先や脚の開きは入れない)
        xs = np.where(band)[1]
        cx.append(float(np.median(xs)) * (f[6] or 1) + f[4])  # 胴体の横位置(足元の基準からの距離)
    tgt = float(np.mean(cx))
    print(k, '胴体x(補正前)', [round(c, 1) for c in cx], '→目標', round(tgt, 1))
    for f, c in zip(fr, cx):
        f[4] = round(f[4] + (tgt - c), 2)
    if not dry:
        M[k]['walk'] = fr
if not dry:
    open(META, 'w').write(json.dumps(M, ensure_ascii=False, separators=(',', ':')))
    print('sprmeta 更新')

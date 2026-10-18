#!/usr/bin/env python3
"""A-035 などの「歩き8コマ」候補を、既存のアトラス(gfx/atlas_<key>.webp)の下に足して walk の行を差し替える。
元の歩きは行 walk_v1 として残す(古い絵は消さない)。元PNGは変更しない。
- 入力: 横1行8コマ・1コマ512x384・純マゼンタ・足元 x=256・接地 y=363 のPNG
使い方: python3 game/tools/append_walk.py masamune game/experiments/a035-walk-20261018/伊達政宗_歩き_8コマ_AI仮_v1.png"""
import io, json, sys
from pathlib import Path
import numpy as np
from PIL import Image
ROOT = Path(__file__).resolve().parents[2]
key, src = sys.argv[1], ROOT / sys.argv[2]
CW, CH, GROUND = 512, 384, 364
a = np.asarray(Image.open(src).convert('RGB')).astype(int)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
bg = (r > 200) & (g < 80) & (b > 200)
edge = (r > 150) & (b > 150) & (r - g > 60) & (b - g > 60) & ~bg
rgb = a.copy()
rgb[..., 0] = np.where(edge, np.minimum(r, g + 40), r)
rgb[..., 2] = np.where(edge, np.minimum(b, g + 40), b)
rgba = np.dstack([rgb, np.where(bg, 0, np.where(edge, 140, 255))]).astype(np.uint8)
cs = [rgba[:, i * CW:(i + 1) * CW] for i in range(rgba.shape[1] // CW)]
bs = []
for c in cs:
    ys, xs = np.where(c[..., 3] > 0)
    bs.append((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
x0, y0 = int(min(t[0] for t in bs)), int(min(t[1] for t in bs))
x1, y1 = int(max(t[2] for t in bs)), int(max(t[3] for t in bs))
W, H = x1 - x0, y1 - y0
atl_p = ROOT / 'gfx' / f'atlas_{key}.webp'
atl = Image.open(atl_p).convert('RGBA')
per = max(1, atl.width // (W + 2))
nrow = (len(cs) + per - 1) // per
big = Image.new('RGBA', (atl.width, atl.height + nrow * H + 2), (0, 0, 0, 0))
big.paste(atl, (0, 0))
base = atl.height + 2
new = []
for i, c in enumerate(cs):
    cx, cy = (i % per) * (W + 2), base + (i // per) * H
    big.paste(Image.fromarray(c[y0:y1, x0:x1], 'RGBA'), (cx, cy))
    new.append([cx, cy, W, H, float(-(CW / 2 - x0)), float(-(GROUND - y0)), 1])
meta_p = ROOT / 'game' / 'sprites' / 'sprmeta.json'
M = json.loads(meta_p.read_text(encoding='utf-8'))
if 'walk_v1' not in M[key]:
    M[key]['walk_v1'] = M[key]['walk']
M[key]['walk'] = new
meta_p.write_text(json.dumps(M, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
buf = io.BytesIO()
big.save(buf, 'WEBP', quality=88, method=6)
atl_p.write_bytes(buf.getvalue())
print(key, big.size, len(buf.getvalue()) // 1024, 'KB', 'walk', len(new), 'コマ')

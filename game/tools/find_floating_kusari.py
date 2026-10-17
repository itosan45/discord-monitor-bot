"""鎖鎌のコマで、分銅(暗い灰色の丸)が体と鎖でつながっていない(浮いている)コマを探す。
結果を game/sprites/kball.json に書く: {キー: {動作: {コマ番号: [x, y, 半径]}}}(足元原点・描画単位)。
ゲームはこの位置へ、体の後ろから鎖を描いて分銅をつなぐ。"""
import json, sys
import numpy as np
from PIL import Image
from scipy import ndimage as nd
from pathlib import Path
R = Path(__file__).resolve().parents[2]
M = json.load(open(R / 'game/sprites/sprmeta.json'))
KEYS = ['yuki', 'kage', 'mitsu', 'nobu', 'shin', 'musashi']
ANIMS = ['kspin', 'kwalk', 'kthrow', 'kpull', 'kret', 'kslash']
out, report = {}, []
for key in KEYS:
    at = np.array(Image.open(R / f'gfx/atlas_{key}.webp').convert('RGBA'))
    for an in ANIMS:
        for i, q in enumerate(M[key].get(an, [])):
            x, y, w, h, ox, oy = q[:6]; s = q[6] if len(q) > 6 else 1
            fr = at[y:y + h, x:x + w]
            a = fr[..., 3] > 60
            lab, n = nd.label(a)
            if n < 2: continue
            sizes = nd.sum(a, lab, range(1, n + 1)); main = 1 + int(np.argmax(sizes))
            for c in range(1, n + 1):
                if c == main: continue
                ys, xs = np.where(lab == c)
                area = len(ys); bw = xs.max() - xs.min() + 1; bh = ys.max() - ys.min() + 1
                if area < 60 or area > 1500: continue
                if not (0.6 < bw / bh < 1.6): continue                      # 丸い
                if area / (bw * bh) < 0.55: continue                        # 中が詰まっている
                rgb = fr[ys, xs, :3].astype(float); L = rgb.mean(); sat = (rgb.max(1) - rgb.min(1)).mean()
                if L > 150 or sat > 45: continue                            # 暗い灰色(鉄)
                cx = (xs.min() + xs.max()) / 2; cy = (ys.min() + ys.max()) / 2
                bx, by, r = round(cx * s + ox, 1), round(cy * s + oy, 1), round(max(bw, bh) / 2 * s, 1)
                out.setdefault(key, {}).setdefault(an, {})[str(i)] = [bx, by, r]
                report.append((key, an, i, bx, by, r, area))
json.dump(out, open(R / 'game/sprites/kball.json', 'w'), separators=(',', ':'))
for r in report: print(*r)
print('浮いている分銅のコマ数:', len(report))

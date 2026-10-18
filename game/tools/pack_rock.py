"""2026-10-14 戦場素材「岩の転がり」(戦場_岩_転がり_3コマ_v1.png、512×384セル×3、純マゼンタ、亀裂の向きが違う3コマ) → atlas_rockroll.webp(新キー rockroll {roll:[3コマ]})。元PNGは変更しない。
縮尺 SCALE=0.46(岩の直径が画面で約100px、レーンの奥行き約170pxに対して大きすぎず小さすぎない大きさ)。3コマは共通の切り出し枠で詰める。
frame の(x,y)(w,h)は atlas 内の位置と大きさ。第5・6要素は岩の中心を原点にした描画位置(-w/2, -h/2)。移動と回転はコード側(drawHazards の 'rocks')。
使い方: python3 game/tools/pack_rock.py  → cd game && python3 build.py"""
import io, json, sys
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SPRITES = ROOT / 'game' / 'sprites'
SRC = ROOT / 'assets' / 'sprites'
sys.path.insert(0, str(SPRITES))
sys.argv = sys.argv[:1]
import mk  # noqa: E402

meta = json.loads((SPRITES / 'sprmeta.json').read_text(encoding='utf-8'))
raw = Image.open(SRC / '戦場_岩_転がり_3コマ_v1.png')
a = mk.keyim(raw)
# 純マゼンタの縁の紫の滲み(min(r,b)-g)を除く(馬防柵と同じ)
_r, _g, _b = (a[..., k].astype(int) for k in range(3))
_ex = np.clip(np.minimum(_r, _b) - _g, 0, None)
a = a.copy()
a[..., 0] = np.clip(_r - _ex, 0, 255).astype('uint8')
a[..., 2] = np.clip(_b - _ex, 0, 255).astype('uint8')
SCALE = 0.46
n = 3
w = a.shape[1] // n
cs = [mk.clean(a[:, i * w:(i + 1) * w]) for i in range(n)]


def bbox(c):
    ys, xs = np.where(c[..., 3] > 40)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


bs = [bbox(c) for c in cs]
x0, y0, x1, y1 = (int(v) for v in (min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs)))
W, H = max(1, round((x1 - x0) * SCALE)), max(1, round((y1 - y0) * SCALE))
atlas = Image.new('RGBA', ((W + 2) * n, H), (0, 0, 0, 0))
arr = []
for i, c in enumerate(cs):
    atlas.paste(Image.fromarray(c[y0:y1, x0:x1], 'RGBA').resize((W, H), Image.LANCZOS), (i * (W + 2), 0))
    arr.append([i * (W + 2), 0, W, H, float(-W / 2), float(-H / 2), 1])
meta['rockroll'] = {'roll': arr}
b = io.BytesIO()
atlas.save(b, 'WEBP', lossless=False, quality=84, method=6)
(SPRITES / 'atlas_rockroll.webp').write_bytes(b.getvalue())
(SPRITES / 'sprmeta.json').write_text(json.dumps(meta), encoding='utf-8')
print('crop', (x0, y0, x1, y1), 'atlas', atlas.size, len(b.getvalue()) // 1024, 'KB', 'frame0', arr[0])

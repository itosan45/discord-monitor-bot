"""2026-10-13 武田信玄の通常2(軍配返し打ち、5コマ)の作り直し版 → atlas_atk3b_shin.webp(新キー atk3b_shin {turn:[5コマ]})。元PNGは変更しない。
旧 `武田信玄_通常2_5コマ.png` はセルの境目で軍配や体が切れていた(コマ0の右端・コマ1/2/3の端に欠片)ので、v2(1280×256・5コマ)で置き換える。
使い方は pack_new_art_v2.py の「新しい攻撃」と同じ: 身長=既存の通常1の1コマ目の描画高さ、原点=1コマ目の最下段(足元)の中央。
使い方: python3 game/tools/pack_shin_turn.py   → cd game && python3 build.py"""
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
a = mk.keyim(Image.open(SRC / '武田信玄_通常2_5コマ_v2.png'))
n = 5
w = a.shape[1] // n
cs = [mk.clean(a[:, i * w:(i + 1) * w]) for i in range(n)]


def bbox(c):
    ys, xs = np.where(c[..., 3] > 40)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


ref = meta['shin']['a1'][0]
target = ref[3] * ref[6]
bs = [bbox(c) for c in cs]
b0 = bs[0]
s = target / (b0[3] - b0[1])
ys, xs = np.where(cs[0][..., 3] > 40)
fy = ys.max() + 1
fxs = xs[ys >= fy - 8]
fx = (fxs.min() + fxs.max()) / 2
x0, y0, x1, y1 = min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs)
W, H = max(1, round((x1 - x0) * s)), max(1, round((y1 - y0) * s))
atlas = Image.new('RGBA', ((W + 2) * n, H), (0, 0, 0, 0))
arr = []
for i, c in enumerate(cs):
    im = Image.fromarray(c[y0:y1, x0:x1], 'RGBA').resize((W, H), Image.LANCZOS)
    atlas.paste(im, (i * (W + 2), 0))
    arr.append([i * (W + 2), 0, W, H, float(round(-(fx - x0) * s, 2)), float(round(-(fy - y0) * s, 2)), 1])
meta['atk3b_shin'] = {'turn': arr}
b = io.BytesIO()
atlas.save(b, 'WEBP', lossless=False, quality=82, method=6)
(SPRITES / 'atlas_atk3b_shin.webp').write_bytes(b.getvalue())
print('scale', round(s, 3), 'foot', (round(fx), int(fy)), 'atlas', atlas.size, len(b.getvalue()) // 1024, 'KB')
(SPRITES / 'sprmeta.json').write_text(json.dumps(meta), encoding='utf-8')

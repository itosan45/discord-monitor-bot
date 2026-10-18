"""2026-10-14 鉄球大僧の鉄球回転6コマ(`武器_鉄球大僧_鉄球回転_6コマ_v1.png`、256×256セル×6、純マゼンタ。2026-10-12納品・未使用だった) → atlas_monkball.webp(新キー monkball {spin:[6コマ]})。元PNGは変更しない。
大僧の鉄球投げ(`mthrow` の絵と対。`k:'ironball'` の飛び道具)で使う。縮尺0.42(球の直径が画面で約80px。大僧が手に持つ鉄球と同じくらい)。原点=球の中心(frame の第5・6要素=-w/2,-h/2)。
使い方: python3 game/tools/pack_monkball.py  → cd game && python3 build.py"""
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
a = mk.keyim(Image.open(SRC / '武器_鉄球大僧_鉄球回転_6コマ_v1.png'))
_r, _g, _b = (a[..., k].astype(int) for k in range(3))
_ex = np.clip(np.minimum(_r, _b) - _g, 0, None)   # 純マゼンタの縁の紫の滲みを除く
a = a.copy()
a[..., 0] = np.clip(_r - _ex, 0, 255).astype('uint8')
a[..., 2] = np.clip(_b - _ex, 0, 255).astype('uint8')
n = 6
w = a.shape[1] // n
cs = [mk.clean(a[:, i * w:(i + 1) * w]) for i in range(n)]
SCALE = 0.42
bs = []
for c in cs:
    ys, xs = np.where(c[..., 3] > 40)
    bs.append((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
x0, y0, x1, y1 = (int(v) for v in (min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs)))
W, H = max(1, round((x1 - x0) * SCALE)), max(1, round((y1 - y0) * SCALE))
atlas = Image.new('RGBA', ((W + 2) * n, H), (0, 0, 0, 0))
arr = []
for i, c in enumerate(cs):
    atlas.paste(Image.fromarray(c[y0:y1, x0:x1], 'RGBA').resize((W, H), Image.LANCZOS), (i * (W + 2), 0))
    arr.append([i * (W + 2), 0, W, H, float(-W / 2), float(-H / 2 + H * 0.12), 1])   # 鎖の根元(上)が少し長いので、球の重心が中心に来るよう少し上へ
meta['monkball'] = {'spin': arr}
b = io.BytesIO()
atlas.save(b, 'WEBP', lossless=False, quality=84, method=6)
(SPRITES / 'atlas_monkball.webp').write_bytes(b.getvalue())
(SPRITES / 'sprmeta.json').write_text(json.dumps(meta), encoding='utf-8')
print('crop', (x0, y0, x1, y1), 'atlas', atlas.size, len(b.getvalue()) // 1024, 'KB', 'frame0', arr[0])

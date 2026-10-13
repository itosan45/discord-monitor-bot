"""2026-10-14 A-016 馬防柵(画面の上から下まで続く破壊可能な柵)の3状態 → atlas_umabo.webp(新キー umabo {wall:[健全, 損傷, 倒壊]})。元PNGは変更しない。
`戦場_馬防柵_破壊_3コマ_v1.png`(768×768・256×768セル×3・純マゼンタ)。縮尺1.0。3コマは共通の切り出し枠で詰め、原点=セル中央のx・セルの上端y。
ゲーム側は drawProp で「柵の中心x(p.x)・セル上端を画面y=-24」に置く(健全の柵列がセル内y24〜743 → 画面0〜719の1280×720全高)。
使い方: python3 game/tools/pack_umabo.py  → cd game && python3 build.py"""
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
raw = Image.open(SRC / '戦場_馬防柵_破壊_3コマ_v1.png')
a = mk.keyim(raw)
# 倒壊コマの瓦礫の影・縁に、純マゼンタが混ざった紫(r≈b>g)が不透明のまま残っている(約5800px)。木の色は茶(r>g>b)なので、紫の分(min(r,b)-g)だけ r と b から引いて除く
_r, _g, _b = (a[..., k].astype(int) for k in range(3))
_ex = np.clip(np.minimum(_r, _b) - _g, 0, None)
a = a.copy()
a[..., 0] = np.clip(_r - _ex, 0, 255).astype('uint8')
a[..., 2] = np.clip(_b - _ex, 0, 255).astype('uint8')
n = 3
w = a.shape[1] // n
cs = [mk.clean(a[:, i * w:(i + 1) * w]) for i in range(n)]


def bbox(c):
    ys, xs = np.where(c[..., 3] > 40)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


bs = [bbox(c) for c in cs]
x0, y0, x1, y1 = (int(v) for v in (min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs)))
W, H = x1 - x0, y1 - y0
atlas = Image.new('RGBA', ((W + 2) * n, H), (0, 0, 0, 0))
arr = []
for i, c in enumerate(cs):
    atlas.paste(Image.fromarray(c[y0:y1, x0:x1], 'RGBA'), (i * (W + 2), 0))
    arr.append([i * (W + 2), 0, W, H, float(x0 - w / 2), float(y0), 1])
meta['umabo'] = {'wall': arr}
b = io.BytesIO()
atlas.save(b, 'WEBP', lossless=False, quality=82, method=6)
(SPRITES / 'atlas_umabo.webp').write_bytes(b.getvalue())
(SPRITES / 'sprmeta.json').write_text(json.dumps(meta), encoding='utf-8')
print('crop', (x0, y0, x1, y1), 'atlas', atlas.size, len(b.getvalue()) // 1024, 'KB', 'frame0', arr[0])

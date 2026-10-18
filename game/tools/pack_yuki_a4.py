"""2026-10-14 真田幸村の通常4(旋回槍、7コマ)の縮尺修正版 v2 → atlas_atk3_yuki.webp(新キー atk3_yuki {spin:[7コマ]})。元PNGは変更しない。
旧 `真田幸村_通常4_7コマ.png` は3コマ目などが途中で切れていた。v2(1792×256・7コマ・純マゼンタ・接地y247)で置き換える。
主アトラス yuki は作り直さず(mk.py は同じ武将の他の動作の版まで入れ替えてしまうため)、この1動作だけ別アトラスにして
ゲーム側の ATK3 表(主武器・徒歩の攻撃で別の絵を使う仕組み)で idx3 に当てる。
縮尺は既存の待機と同じ 0.7724(待機の絵の高さ246px→ゲーム190px)、原点は mk.py と同じ「セル中央のx・待機の接地線y248」。
使い方: python3 game/tools/pack_yuki_a4.py  → cd game && python3 build.py"""
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
idle = meta['yuki']['idle'][0]
a = mk.keyim(Image.open(SRC / '真田幸村_通常4_7コマ_v2.png'))
n = 7
w = a.shape[1] // n
cs = [mk.clean(a[:, i * w:(i + 1) * w]) for i in range(n)]
ic = mk.keyim(Image.open(SRC / '真田幸村_待機_4コマ.png'))
iw = ic.shape[1] // 4
ys, xs = np.where(mk.clean(ic[:, :iw])[..., 3] > 40)
s = idle[3] * idle[6] / (ys.max() + 1 - ys.min())      # 待機と同じ縮尺
ground = float(ys.max() + 1)                            # 待機の接地線(セル内y)
cx = w / 2


def bbox(c):
    ys, xs = np.where(c[..., 3] > 40)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


bs = [bbox(c) for c in cs]
x0, y0, x1, y1 = min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs)
W, H = max(1, round((x1 - x0) * s)), max(1, round((y1 - y0) * s))
atlas = Image.new('RGBA', ((W + 2) * n, H), (0, 0, 0, 0))
arr = []
for i, c in enumerate(cs):
    im = Image.fromarray(c[y0:y1, x0:x1], 'RGBA').resize((W, H), Image.LANCZOS)
    atlas.paste(im, (i * (W + 2), 0))
    arr.append([i * (W + 2), 0, W, H, float(round((x0 - cx) * s, 2)), float(round((y0 - ground) * s, 2)), 1])
meta['atk3_yuki'] = {'spin': arr}
b = io.BytesIO()
atlas.save(b, 'WEBP', lossless=False, quality=82, method=6)
(SPRITES / 'atlas_atk3_yuki.webp').write_bytes(b.getvalue())
(SPRITES / 'sprmeta.json').write_text(json.dumps(meta), encoding='utf-8')
print('scale', round(s, 4), 'ground', ground, 'atlas', atlas.size, len(b.getvalue()) // 1024, 'KB', arr[0], arr[4])

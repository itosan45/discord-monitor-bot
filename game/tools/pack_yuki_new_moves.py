"""2026-10-11 画像担当が納品した幸村の新規3素材を、ゲーム用のアトラス(新キー)にする。元PNGは変更しない。
- 真田幸村_六段突き_12コマ_v1.png (512x256 x12) -> atlas_yukirokudan1.webp / sprmeta 'yukirokudan1' {'thrust':12}
  原画は旗込みの身長が約212pxで、待機(旗込み190px)より大きいので 190/212 に縮める。足の接地点を原点にする。
- 馬上歩行旋回_真田幸村_主武器_6コマ_v1.png (576x416 x6) -> atlas_mountwhirl1_yuki.webp / sprmeta 'mountwhirl1_yuki' {'whirl':6}
  馬の大きさは mountwalk5(256セル x1.4)とほぼ同じなので倍率1。馬の中心と蹄の線(y=384)を原点にする。
- タイトル_真田幸村_十文字槍_v1.png (2048x512) -> gfx/title_spear1.webp(透過・余白詰め)。build.py が内容ハッシュ付きURLで渡す。
使い方: python3 game/tools/pack_yuki_new_moves.py"""
import io, json, os, sys
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SPRITES = ROOT / 'game' / 'sprites'
SRC = ROOT / 'assets' / 'sprites'
sys.path.insert(0, str(SPRITES))
sys.argv = sys.argv[:1]
import mk  # noqa: E402


def cells(name, n):
    a = mk.keyim(Image.open(SRC / name))
    w = a.shape[1] // n
    return [mk.clean(a[:, i * w:(i + 1) * w]) for i in range(n)]


def union_bbox(cs):
    x0 = y0 = 1 << 30; x1 = y1 = 0
    for c in cs:
        ys, xs = np.where(c[..., 3] > 40)
        x0, y0, x1, y1 = min(x0, xs.min()), min(y0, ys.min()), max(x1, xs.max() + 1), max(y1, ys.max() + 1)
    return x0, y0, x1, y1


def save_webp(img, path, lossless=False):
    b = io.BytesIO()
    img.save(b, 'WEBP', lossless=lossless, quality=80 if not lossless else 100, method=6)
    path.write_bytes(b.getvalue())
    return len(b.getvalue()) // 1024


meta = json.loads((SPRITES / 'sprmeta.json').read_text(encoding='utf-8'))

# 六段突き
cs = cells('真田幸村_六段突き_12コマ_v1.png', 12)
x0, y0, x1, y1 = union_bbox(cs)
s = 190 / (y1 - y0)
# 接地点: 1コマ目の最下段付近の不透明画素の左右中央(両足の間)
c0 = cs[0][..., 3] > 40
ys, xs = np.where(c0)
fy = ys.max() + 1
fxs = xs[ys >= fy - 8]
fx = (fxs.min() + fxs.max()) / 2
W, H = round((x1 - x0) * s), round((y1 - y0) * s)
atlas = Image.new('RGBA', ((W + 2) * 12, H), (0, 0, 0, 0))
arr = []
for i, c in enumerate(cs):
    im = Image.fromarray(c[y0:y1, x0:x1], 'RGBA').resize((W, H), Image.LANCZOS)
    atlas.paste(im, (i * (W + 2), 0))
    arr.append([i * (W + 2), 0, W, H, float(round(-(fx - x0) * s, 2)), float(round(-(fy - y0) * s, 2)), 1])
meta['yukirokudan1'] = {'thrust': arr}
print('yukirokudan1', atlas.size, 'scale', round(s, 3), 'origin', arr[0][4:6], save_webp(atlas, SPRITES / 'atlas_yukirokudan1.webp'), 'KB')

# 馬上歩行旋回
cs = cells('馬上歩行旋回_真田幸村_主武器_6コマ_v1.png', 6)
lo = cs[0][250:, :, 3] > 40
_, xs = np.where(lo)
cx = (xs.min() + xs.max()) / 2
x0, y0, x1, y1 = union_bbox(cs)
atlas = Image.new('RGBA', ((x1 - x0 + 2) * 6, y1 - y0), (0, 0, 0, 0))
arr = []
for i, c in enumerate(cs):
    atlas.paste(Image.fromarray(c[y0:y1, x0:x1], 'RGBA'), (i * (x1 - x0 + 2), 0))
    arr.append([int(i * (x1 - x0 + 2)), 0, int(x1 - x0), int(y1 - y0), float(round(-(cx - x0), 2)), int(y0) - 384, 1])
meta['mountwhirl1_yuki'] = {'whirl': arr}
print('mountwhirl1_yuki', atlas.size, 'origin', arr[0][4:6], save_webp(atlas, SPRITES / 'atlas_mountwhirl1_yuki.webp'), 'KB')

# タイトル用 十文字槍
a = mk.keyim(Image.open(SRC / 'タイトル_真田幸村_十文字槍_v1.png'))
ys, xs = np.where(a[..., 3] > 40)
sp = Image.fromarray(a[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 'RGBA')
sp = sp.resize((sp.width // 2, sp.height // 2), Image.LANCZOS)
print('title_spear1', sp.size, save_webp(sp, ROOT / 'gfx' / 'title_spear1.webp'), 'KB')

(SPRITES / 'sprmeta.json').write_text(json.dumps(meta), encoding='utf-8')

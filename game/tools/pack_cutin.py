"""2026-10-12 画像担当の細帯カットイン6枚(カットイン_<武将>_細帯_v1.png 1024x160、背景マゼンタ)を1枚のアトラスにする。元PNGは変更しない。
atlas_cutin.webp / sprmeta 'cutin' {hero:[[x,y,w,h,0,0,1]]}。幅は512へ半分に縮める(画面では幅の約半分で表示するため)。
使い方: python3 game/tools/pack_cutin.py"""
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
HERO = {'yuki': '真田幸村', 'kage': '上杉景勝', 'mitsu': '石田三成', 'nobu': '織田信長', 'shin': '武田信玄', 'musashi': '宮本武蔵'}
meta = json.loads((SPRITES / 'sprmeta.json').read_text(encoding='utf-8'))
ims, W, H = [], 512, 80
for h, jp in HERO.items():
    a = mk.clean(mk.keyim(Image.open(SRC / f'カットイン_{jp}_細帯_v1.png')))
    im = Image.fromarray(a, 'RGBA').resize((W, H), Image.LANCZOS)
    ims.append((h, im))
atlas = Image.new('RGBA', (W, (H + 2) * len(ims)), (0, 0, 0, 0))
out = {}
for i, (h, im) in enumerate(ims):
    atlas.paste(im, (0, i * (H + 2)))
    out[h] = [[0, i * (H + 2), W, H, 0, 0, 1]]
b = io.BytesIO(); atlas.save(b, 'WEBP', quality=85, method=6)
(SPRITES / 'atlas_cutin.webp').write_bytes(b.getvalue())
meta['cutin'] = out
(SPRITES / 'sprmeta.json').write_text(json.dumps(meta), encoding='utf-8')
print('cutin', atlas.size, len(b.getvalue()) // 1024, 'KB')

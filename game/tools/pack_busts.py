"""2026-10-12 画像担当の「兜なし」会話肖像6枚(1254角、背景マゼンタ)を、ストーリー(ステージ外の会話)用の胸像 gfx/bust_<hero>.webp にする。元PNGは変更しない。
900x900の透過。内容の外接矩形を、幅か高さに合わせて(余白なし)縮め、横は中央・下は端にそろえる(既存の yk_bust.webp と同じ使い方: 560px角で描く)。
使い方: python3 game/tools/pack_busts.py"""
import sys, io
from pathlib import Path
import numpy as np
from PIL import Image
ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'assets' / 'sprites'
sys.path.insert(0, str(ROOT / 'game' / 'sprites'))
sys.argv = sys.argv[:1]
import mk  # noqa: E402
FILES = {'yuki': '会話肖像_真田幸村_兜なし_v1.png', 'kage': '会話肖像_上杉景勝_兜なし_v1.png', 'mitsu': '会話肖像_石田三成_兜なし_v1.png',
         'nobu': '会話肖像_織田信長_兜なし_v1.png', 'shin': '会話肖像_武田信玄_兜なし_v1.png', 'musashi': '会話肖像_宮本武蔵_決意_v1.png'}
N = 900
for h, fn in FILES.items():
    a = mk.clean(mk.keyim(Image.open(SRC / fn)))
    ys, xs = np.where(a[..., 3] > 40)
    im = Image.fromarray(a[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 'RGBA')
    s = min(N / im.width, (N - 10) / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    out = Image.new('RGBA', (N, N), (0, 0, 0, 0))
    out.paste(im, ((N - im.width) // 2, N - im.height))
    b = io.BytesIO(); out.save(b, 'WEBP', quality=86, method=6)
    (ROOT / 'gfx' / f'bust_{h}.webp').write_bytes(b.getvalue())
    print(h, im.size, len(b.getvalue()) // 1024, 'KB')

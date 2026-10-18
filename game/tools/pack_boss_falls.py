"""A-028 武将ボスの転倒・起き上がり(画像担当の候補 game/experiments/a028-bossfalls-*/)を、新しいアトラス bfall_<boss> にする。元PNGは変更しない。
- 入力: <武将名>_転倒_4コマ_v1.png・<武将名>_起き上がり_4コマ_v1.png(1コマ384x384、純マゼンタ、接地線 y=363)
- 原点: セルの中央(x=192)・接地線(y=363+1)。縮尺 1.0(画像担当が待機の人物の高さ約188pxに合わせてある。ゲームの待機は約190px)
- 描画は game_src.html の drawSprite で、ボスが down/getup の間だけ bfall_<boss> の down/getup 行に差し替える(ジャンプの bjump_ と同じ方式)
使い方: python3 game/tools/pack_boss_falls.py boss1 井伊直政 game/experiments/a028-bossfalls-20261017"""
import io, json, sys
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SPRITES = ROOT / 'game' / 'sprites'
key, name, src = sys.argv[1], sys.argv[2], ROOT / sys.argv[3]
CW, GROUND, SCALE = 384, 364, 1.0


def cells(fn):
    a = np.asarray(Image.open(src / fn).convert('RGB')).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    bg = (r > 200) & (g < 80) & (b > 200)
    edge = (r > 150) & (b > 150) & (r - g > 60) & (b - g > 60) & ~bg  # 縁のにじみ
    rgb = a.copy()
    rgb[..., 0] = np.where(edge, np.minimum(r, g + 40), r)
    rgb[..., 2] = np.where(edge, np.minimum(b, g + 40), b)
    alpha = np.where(bg, 0, np.where(edge, 140, 255))
    rgba = np.dstack([rgb, alpha]).astype(np.uint8)
    n = rgba.shape[1] // CW
    return [rgba[:, i * CW:(i + 1) * CW] for i in range(n)]


def pack_row(cs):
    bs = []
    for c in cs:
        ys, xs = np.where(c[..., 3] > 0)
        bs.append((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    x0, y0 = min(b[0] for b in bs), min(b[1] for b in bs)
    x1, y1 = max(b[2] for b in bs), max(b[3] for b in bs)
    W, H = round((x1 - x0) * SCALE), round((y1 - y0) * SCALE)
    row = Image.new('RGBA', ((W + 2) * len(cs), H), (0, 0, 0, 0))
    arr = []
    for i, c in enumerate(cs):
        im = Image.fromarray(c[y0:y1, x0:x1], 'RGBA').resize((W, H), Image.LANCZOS)
        row.paste(im, (i * (W + 2), 0))
        arr.append([i * (W + 2), 0, W, H, float(round(-(CW / 2 - x0) * SCALE, 2)), float(round(-(GROUND - y0) * SCALE, 2)), 1])
    return row, arr


rows = [('down', *pack_row(cells(f'{name}_転倒_4コマ_v1.png'))), ('getup', *pack_row(cells(f'{name}_起き上がり_4コマ_v1.png')))]
AW = max(r.width for _, r, _ in rows)
AH = sum(r.height + 2 for _, r, _ in rows)
big = Image.new('RGBA', (AW, AH), (0, 0, 0, 0))
out, y = {}, 0
for nm, r, arr in rows:
    big.paste(r, (0, y))
    out[nm] = [[q[0], q[1] + y, q[2], q[3], q[4], q[5], q[6]] for q in arr]
    y += r.height + 2
meta_p = SPRITES / 'sprmeta.json'
meta = json.loads(meta_p.read_text(encoding='utf-8'))
meta['bfall_' + key] = out
meta_p.write_text(json.dumps(meta, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
b = io.BytesIO()
big.save(b, 'WEBP', quality=86, method=6)
(SPRITES / f'atlas_bfall_{key}.webp').write_bytes(b.getvalue())
print('bfall_' + key, big.size, len(b.getvalue()) // 1024, 'KB', {k: len(v) for k, v in out.items()})

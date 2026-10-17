"""A-031 武将ボスの「跳び込み攻撃」など1行の攻撃(画像担当の候補 game/experiments/a031-bossatk-*/)を、新しいアトラス b<種類>_<boss> にする。元PNGは変更しない。
- 入力: 1行(または8コマずつ複数行)に並べたPNG(1コマ512x384、純マゼンタ、足元 x=256・接地線 y=363)。縮尺 1.0(立ち姿は待機と同じ約188px)
- 出力: game/sprites/atlas_<kind>_<key>.webp と sprmeta の <kind>_<key>(行名 row)
- 描画は game_src.html の drawSprite で、該当の技(k:'leap'+dive:true)の間だけ差し替える
使い方: python3 game/tools/pack_boss_atk.py bdive boss5 dive game/experiments/a031-bossatk-20261017/徳川秀忠_跳び込み攻撃_16コマ_v2.png
        python3 game/tools/pack_boss_atk.py bguard boss5 ready=<構え.png> block=<受け止め.png> parry=<受け流し.png> crash=<崩れ.png>"""
import io, json, sys
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SPRITES = ROOT / 'game' / 'sprites'
kind, key = sys.argv[1], sys.argv[2]
# 行は「行名=PNG」を並べる(例: ready=構え.png block=受け止め.png)。旧形式「行名 PNG」(1行だけ)も使える
args = sys.argv[3:]
JOBS = [(r.split('=', 1)[0], ROOT / r.split('=', 1)[1]) for r in args] if all('=' in r for r in args) else [(args[0], ROOT / args[1])]
CW, CH, GROUND = 512, 384, 364


def cells(path):
    a = np.asarray(Image.open(path).convert('RGB')).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    bg = (r > 200) & (g < 80) & (b > 200)
    edge = (r > 150) & (b > 150) & (r - g > 60) & (b - g > 60) & ~bg  # 縁のにじみ
    rgb = a.copy()
    rgb[..., 0] = np.where(edge, np.minimum(r, g + 40), r)
    rgb[..., 2] = np.where(edge, np.minimum(b, g + 40), b)
    alpha = np.where(bg, 0, np.where(edge, 140, 255))
    rgba = np.dstack([rgb, alpha]).astype(np.uint8)
    # 1行でも複数行(上の行から左→右の順)でもよい。16コマなら 4096x768(8コマx2行)
    return [rgba[r * CH:(r + 1) * CH, i * CW:(i + 1) * CW] for r in range(rgba.shape[0] // CH) for i in range(rgba.shape[1] // CW)]


rows = []
for row, src in JOBS:
    cs = cells(src)
    bs = []
    for c in cs:
        ys, xs = np.where(c[..., 3] > 0)
        bs.append((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    x0, y0 = int(min(b[0] for b in bs)), int(min(b[1] for b in bs))
    x1, y1 = int(max(b[2] for b in bs)), int(max(b[3] for b in bs))
    W, H = x1 - x0, y1 - y0
    # 古い端末のテクスチャ上限(4096)を超えないよう、1行を最大 MAXW 幅で折り返して段にする(20コマの連撃など)
    per = max(1, 4000 // (W + 2))
    nrow = (len(cs) + per - 1) // per
    img = Image.new('RGBA', ((W + 2) * min(per, len(cs)), H * nrow), (0, 0, 0, 0))
    arr = []
    for i, c in enumerate(cs):
        cx, cy = (i % per) * (W + 2), (i // per) * H
        img.paste(Image.fromarray(c[y0:y1, x0:x1], 'RGBA'), (cx, cy))
        arr.append([cx, cy, W, H, float(-(CW / 2 - x0)), float(-(GROUND - y0)), 1])
    rows.append((row, img, arr))
AW = max(r[1].width for r in rows)
AH = sum(r[1].height + 2 for r in rows)
big = Image.new('RGBA', (AW, AH), (0, 0, 0, 0))
out, y = {}, 0
for row, img, arr in rows:
    big.paste(img, (0, y))
    out[row] = [[q[0], q[1] + y, q[2], q[3], q[4], q[5], q[6]] for q in arr]
    y += img.height + 2
meta_p = SPRITES / 'sprmeta.json'
meta = json.loads(meta_p.read_text(encoding='utf-8'))
meta[f'{kind}_{key}'] = out
meta_p.write_text(json.dumps(meta, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
b = io.BytesIO()
big.save(b, 'WEBP', quality=86, method=6)
(SPRITES / f'atlas_{kind}_{key}.webp').write_bytes(b.getvalue())
print(f'{kind}_{key}', big.size, len(b.getvalue()) // 1024, 'KB', {k: len(v) for k, v in out.items()})

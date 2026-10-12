"""2026-10-12 猿飛佐助(幸村のパートナー)用アトラス atlas_sasuke.webp(新キー)。元PNGは変更しない。
納品済みの 待機4・歩き8・武器別攻撃6(a1)・短刀切り返し6(a2)・被弾2・起き上がり4・やられ4・低姿勢回避6 を使う。
ダウンは未納品: 被弾の2コマ目と起き上がりの1コマ目(寝姿)で代用している(納品されたら差し替える)。ジャンプ・手裏剣投げ・必殺の専用絵は未納品:
ジャンプ=低姿勢回避のコマ、手裏剣投げ・必殺=短刀切り返しのコマで代用している(A-009/A-010/A-011 で依頼済み)。
やられは4コマが立ち姿のため、ダウンの寝姿(3・4コマ目)を足して倒れ切るまでにしている。
原点: x=128、y=待機と歩きの下端の平均(接地線)。縮尺は SCALE の1つだけ。
使い方: python3 game/tools/pack_saizo.py"""
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

SCALE = 0.9
SPEC = [('idle', '猿飛佐助_待機_4コマ_v1.png', 4), ('walk', '猿飛佐助_低姿勢歩き_8コマ_v1.png', 8), ('a1', '猿飛佐助_武器別攻撃_6コマ_v1.png', 6),
        ('a2', '猿飛佐助_短刀切り返し_6コマ_v1.png', 6), ('hit', '猿飛佐助_被弾_2コマ_v1.png', 2), ('getup', '猿飛佐助_起き上がり_4コマ_v1.png', 4),
        ('dead', '猿飛佐助_やられ_4コマ_v1.png', 4), ('dodgeB', '猿飛佐助_低姿勢回避_6コマ_v1.png', 6)]
meta = json.loads((SPRITES / 'sprmeta.json').read_text(encoding='utf-8'))


def cells(name, n):
    a = mk.keyim(Image.open(SRC / name))
    w = a.shape[1] // n
    return [mk.clean(a[:, i * w:(i + 1) * w]) for i in range(n)]


def bottoms(cs):
    return [np.where(c[..., 3] > 40)[0].max() + 1 for c in cs]


def pack_row(cs, origin, s):
    bs = []
    for c in cs:
        ys, xs = np.where(c[..., 3] > 40)
        bs.append((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    x0, y0 = min(b[0] for b in bs), min(b[1] for b in bs)
    x1, y1 = max(b[2] for b in bs), max(b[3] for b in bs)
    W, H = max(1, round((x1 - x0) * s)), max(1, round((y1 - y0) * s))
    row = Image.new('RGBA', ((W + 2) * len(cs), H), (0, 0, 0, 0))
    arr = []
    for i, c in enumerate(cs):
        im = Image.fromarray(c[y0:y1, x0:x1], 'RGBA').resize((W, H), Image.LANCZOS)
        row.paste(im, (i * (W + 2), 0))
        arr.append([i * (W + 2), 0, W, H, float(round(-(origin[0] - x0) * s, 2)), float(round(-(origin[1] - y0) * s, 2)), 1])
    return row, arr


loaded = {nm: cells(fn, n) for nm, fn, n in SPEC}
ground = float(np.mean(bottoms(loaded['idle']) + bottoms(loaded['walk'])))
rows = []
for nm, fn, n in SPEC:
    g = float(np.mean(bottoms(loaded[nm]))) if nm in ('getup', 'dead') else ground
    row, arr = pack_row(loaded[nm], (128, g), SCALE)
    rows.append((nm, row, arr))
AW = max(r.width for _, r, _ in rows)
AH = sum(r.height + 2 for _, r, _ in rows)
big = Image.new('RGBA', (AW, AH), (0, 0, 0, 0))
out, y = {}, 0
for nm, r, arr in rows:
    big.paste(r, (0, y))
    out[nm] = [[q[0], q[1] + y, q[2], q[3], q[4], q[5], q[6]] for q in arr]
    y += r.height + 2
# 代用(同じコマの座標を別名で参照するだけ。画像は増えない)
# ダウン(未納品)は、被弾の2コマ目(のけぞり)と起き上がりの1コマ目(寝姿)で代用。やられ(納品の4コマは立ち姿)の後に寝姿をつないで倒れ切るまで見せる
out['down'] = [out['hit'][1], out['hit'][1], out['getup'][0]]
out['dead'] = out['dead'] + [out['getup'][0], out['getup'][0]]
out['jump'] = [out['dodgeB'][0], out['dodgeB'][1], out['dodgeB'][2], out['dodgeB'][3]]
out['dash'] = [out['a2'][1], out['a2'][2], out['a2'][3], out['a2'][4], out['a2'][5]]
out['spc'] = out['a2'][:]
out['jatk'] = [out['a2'][1], out['a2'][2], out['a2'][3], out['a2'][4]]
meta['sasuke'] = out
b = io.BytesIO()
big.save(b, 'WEBP', lossless=False, quality=82, method=6)
(SPRITES / 'atlas_sasuke.webp').write_bytes(b.getvalue())
(SPRITES / 'sprmeta.json').write_text(json.dumps(meta), encoding='utf-8')
print('sasuke', big.size, 'ground', round(ground, 1), len(b.getvalue()) // 1024, 'KB')

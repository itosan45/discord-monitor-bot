"""2026-10-14 鉄球大僧の転倒8コマ(v3)と叩きつけ12コマ(v2)を atlas_monk.webp に足す。元PNGは変更しない。
- 旧アトラスは新キー monk_v1 として gfx/atlas_monk_v1.webp と sprmeta['monk_v1'] に保持する(初回のみ作る)。
- 新アトラス monk: pack_a006.py と同じ縮尺0.86・原点(x=128, y=待機と歩きの下端平均)。そこへ
  'walk'=歩き16コマ(2026-10-14納品。旧8コマv2と置き換え。旧は monk_v1 に残る。人物の高さが旧歩きより約4%小さいため、この行だけ縮尺を×1.035して旧歩きの高さにそろえる=ROW_SCALE)、
  'smash'=叩きつけ12コマ(通常攻撃1段目が使う。旧 'a1' 6コマは跳躍攻撃が引き続き使う)、
  'down'=転倒8コマ(旧4コマに置き換え。接地線y360を原点にして、空中のコマは自然に浮く)。
  転倒8コマの使い方: 0・1=のけぞり、2=離地、3=後方へ吹き飛ぶ、4=落下、5=初接地、6=小さな弾み、7=寝姿。
使い方: python3 game/tools/pack_monk_v3.py  → cd game && python3 build.py"""
import io, json, shutil, sys
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SPRITES = ROOT / 'game' / 'sprites'
SRC = ROOT / 'assets' / 'sprites'
GFX = ROOT / 'gfx'
sys.path.insert(0, str(SPRITES))
sys.argv = sys.argv[:1]
import mk  # noqa: E402

SCALE = 0.86
ROW_SCALE = {'walk': 1.035}   # 歩き16コマは人物の高さが旧歩き8コマv2より約4%小さい(197〜205px対207〜209px)ので、旧歩きの高さへそろえる
SPEC = [('idle', '鉄球大僧_待機_4コマ_v1.png', 4), ('walk', '鉄球大僧_歩き_16コマ_v1.png', 16), ('a1', '鉄球大僧_攻撃_6コマ_v1.png', 6),
        ('smash', '鉄球大僧_攻撃_12コマ_v2.png', 12), ('a2', '鉄球大僧_ダッシュタックル_8コマ_v1.png', 8), ('hit', '鉄球大僧_被弾_2コマ_v1.png', 2),
        ('down', '鉄球大僧_ダウン_8コマ_v3.png', 8), ('getup', '鉄球大僧_起き上がり_4コマ_v1.png', 4), ('dead', '鉄球大僧_やられ_6コマ_v1.png', 6)]
meta = json.loads((SPRITES / 'sprmeta.json').read_text(encoding='utf-8'))

# 旧アトラスの保持(まだ無いときだけ)
if 'monk_v1' not in meta:
    meta['monk_v1'] = json.loads(json.dumps(meta['monk']))
    src = GFX / 'atlas_monk.webp'
    if not src.exists():
        src = SPRITES / 'atlas_monk.webp'
    shutil.copyfile(src, GFX / 'atlas_monk_v1.webp')
    shutil.copyfile(src, SPRITES / 'atlas_monk_v1.webp')


def cells(name, n):
    a = mk.keyim(Image.open(SRC / name))
    w = a.shape[1] // n
    return [mk.clean(a[:, i * w:(i + 1) * w]) for i in range(n)]


def bottoms(cs):
    return [int(np.where(c[..., 3] > 40)[0].max() + 1) for c in cs]


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
    if nm == 'down':
        g = float(max(bottoms(loaded[nm])))      # 接地線(原画y360)を原点にする。空中のコマは平均でなく地面からの高さで浮かせる
    elif nm in ('getup', 'dead'):
        g = float(np.mean(bottoms(loaded[nm])))
    else:
        g = ground
    row, arr = pack_row(loaded[nm], (128, g), SCALE * ROW_SCALE.get(nm, 1.0))
    rows.append((nm, row, arr))
AW = max(r.width for _, r, _ in rows)
AH = sum(r.height + 2 for _, r, _ in rows)
big = Image.new('RGBA', (AW, AH), (0, 0, 0, 0))
out, y = {}, 0
for nm, r, arr in rows:
    big.paste(r, (0, y))
    out[nm] = [[q[0], q[1] + y, q[2], q[3], q[4], q[5], q[6]] for q in arr]
    y += r.height + 2
meta['monk'] = out
b = io.BytesIO()
big.save(b, 'WEBP', lossless=False, quality=82, method=6)
(SPRITES / 'atlas_monk.webp').write_bytes(b.getvalue())
(SPRITES / 'sprmeta.json').write_text(json.dumps(meta), encoding='utf-8')
print('monk', big.size, 'ground', round(ground, 1), len(b.getvalue()) // 1024, 'KB', {k: len(v) for k, v in out.items()})

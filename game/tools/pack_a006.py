"""2026-10-12 画像担当のA-006納品(鉄球大僧・仮面くのいち・鎧武者薙刀・赤備槍武者)を、ゲーム用のアトラス(新キー)にする。元PNGは変更しない。
- atlas_monk.webp / atlas_kunoichi.webp / atlas_yoroi.webp / atlas_akabi.webp: 敵の動作配列(idle/walk/a1/a2/hit/down/getup/dead ほか)。
  256x384のコマ。原点は x=128(セル中央)・y=その人物の接地線(待機と歩きの下端の平均)。縮尺は人物ごとに1つだけ(SCALE)。動作ごとに別の倍率・中心補正はしない。
- atlas_monkfx.webp: 鉄球の回転6コマ(球の中心が原点)・叩きつけ衝撃4コマ(地面の発生点が原点)・クナイ1枚(中心が原点)。
使い方: python3 game/tools/pack_a006.py"""
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

# 人物ごとの縮尺(既存の足軽の立ち絵は高さ約170〜195px。大僧は一回り大きく、くのいちは足軽並み)
SCALE = {'monk': 0.86, 'kunoichi': 0.9, 'yoroi': 0.84, 'akabi': 0.84}
SETS = {
    'monk': [('idle', '鉄球大僧_待機_4コマ_v1.png', 4), ('walk', '鉄球大僧_歩き_8コマ_v2.png', 8), ('a1', '鉄球大僧_攻撃_6コマ_v1.png', 6),
             ('a2', '鉄球大僧_ダッシュタックル_8コマ_v1.png', 8), ('hit', '鉄球大僧_被弾_2コマ_v1.png', 2), ('down', '鉄球大僧_ダウン_4コマ_v2.png', 4),
             ('getup', '鉄球大僧_起き上がり_4コマ_v1.png', 4), ('dead', '鉄球大僧_やられ_6コマ_v1.png', 6)],
    'kunoichi': [('idle', '仮面くのいち_待機_4コマ_v1.png', 4), ('walk', '仮面くのいち_歩き_8コマ_v2.png', 8), ('run', '仮面くのいち_走り_8コマ_v1.png', 8),
                 ('a1', '仮面くのいち_攻撃_6コマ_v1.png', 6), ('a2', '仮面くのいち_ジャンプクナイ投げ_8コマ_v1.png', 8), ('hit', '仮面くのいち_被弾_2コマ_v1.png', 2),
                 ('down', '仮面くのいち_ダウン_4コマ_v1.png', 4), ('getup', '仮面くのいち_起き上がり_4コマ_v1.png', 4), ('dead', '仮面くのいち_やられ_6コマ_v1.png', 6),
                 ('dodgeB', '仮面くのいち_低い回避_4コマ_v1.png', 4)],
    'yoroi': [('idle', '敵_鎧武者薙刀_待機_4コマ_v1.png', 4), ('walk', '敵_鎧武者薙刀_歩き_8コマ_v1.png', 8), ('a1', '敵_鎧武者薙刀_攻撃_6コマ_v1.png', 6),
              ('hit', '敵_鎧武者薙刀_被弾_2コマ_v1.png', 2), ('down', '敵_鎧武者薙刀_ダウン_4コマ_v1.png', 4), ('getup', '敵_鎧武者薙刀_起き上がり_4コマ_v1.png', 4),
              ('dead', '敵_鎧武者薙刀_やられ_6コマ_v1.png', 6)],
    'akabi': [('idle', '敵_赤備槍武者_待機_4コマ_v1.png', 4), ('walk', '敵_赤備槍武者_歩き_8コマ_v1.png', 8), ('a1', '敵_赤備槍武者_攻撃_6コマ_v1.png', 6),
              ('hit', '敵_赤備槍武者_被弾_2コマ_v1.png', 2), ('down', '敵_赤備槍武者_ダウン_4コマ_v1.png', 4), ('getup', '敵_赤備槍武者_起き上がり_4コマ_v1.png', 4),
              ('dead', '敵_赤備槍武者_やられ_6コマ_v1.png', 6)],
}
meta = json.loads((SPRITES / 'sprmeta.json').read_text(encoding='utf-8'))


def webp(img, path):
    b = io.BytesIO()
    img.save(b, 'WEBP', lossless=False, quality=82, method=6)
    path.write_bytes(b.getvalue())
    return len(b.getvalue()) // 1024


def cells(name, n, w=None):
    a = mk.keyim(Image.open(SRC / name))
    w = w or a.shape[1] // n
    return [mk.clean(a[:, i * w:(i + 1) * w]) for i in range(n)]


def bottoms(cs):
    out = []
    for c in cs:
        ys, _ = np.where(c[..., 3] > 40)
        out.append(ys.max() + 1)
    return out


def pack_row(cs, origin, s):
    """各コマを自分の不透明範囲で切り、原点(セル内の基準点)からの位置を保ったまま縮尺sで詰める。"""
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
        im = Image.fromarray(c[y0:y1, x0:x1], 'RGBA')
        if s != 1.0:
            im = im.resize((W, H), Image.LANCZOS)
        row.paste(im, (i * (W + 2), 0))
        arr.append([i * (W + 2), 0, W, H, float(round(-(origin[0] - x0) * s, 2)), float(round(-(origin[1] - y0) * s, 2)), 1])
    return row, arr


def stack(rows):
    AW = max(r.width for _, r, _ in rows)
    AH = sum(r.height + 2 for _, r, _ in rows)
    big = Image.new('RGBA', (AW, AH), (0, 0, 0, 0))
    out, y = {}, 0
    for nm, r, arr in rows:
        big.paste(r, (0, y))
        out[nm] = [[q[0], q[1] + y, q[2], q[3], q[4], q[5], q[6]] for q in arr]
        y += r.height + 2
    return big, out


for key, spec in SETS.items():
    s = SCALE[key]
    loaded = {nm: cells(fn, n) for nm, fn, n in spec}
    # 接地線: 待機と歩きの下端の平均(立ち姿どうしで足が上下しないように)
    ground = float(np.mean(bottoms(loaded['idle']) + bottoms(loaded['walk'])))
    rows = []
    for nm, fn, n in spec:
        g = ground
        if nm in ('down', 'dead', 'getup'):
            g = float(np.mean(bottoms(loaded[nm])))  # 寝姿は自分の下端が地面(原画も360で統一)
        row, arr = pack_row(loaded[nm], (128, g), s)
        rows.append((nm, row, arr))
    big, out = stack(rows)
    meta[key] = out
    print(key, big.size, 'scale', s, 'ground', round(ground, 1), webp(big, SPRITES / f'atlas_{key}.webp'), 'KB')

# 効果: 鉄球回転・叩きつけ衝撃・クナイ
fx_rows = []
cs = cells('武器_鉄球大僧_鉄球回転_6コマ_v1.png', 6)
row, arr = pack_row(cs, (128, 155), 0.28)
fx_rows.append(('ball', row, arr))
cs = cells('エフェクト_鉄球大僧_叩きつけ衝撃_4コマ_v1.png', 4)
row, arr = pack_row(cs, (128, 232), 0.9)
fx_rows.append(('quake', row, arr))
kc = cells('飛び道具_仮面くのいち_クナイ_v1.png', 1)
ys, xs = np.where(kc[0][..., 3] > 40)
cx, cy = (xs.min() + xs.max() + 1) / 2, (ys.min() + ys.max() + 1) / 2
ks = 56 / (xs.max() + 1 - xs.min())
row, arr = pack_row(kc, (cx, cy), ks)
fx_rows.append(('kunai', row, arr))
big, out = stack(fx_rows)
meta['monkfx'] = out
print('monkfx', big.size, webp(big, SPRITES / 'atlas_monkfx.webp'), 'KB')

(SPRITES / 'sprmeta.json').write_text(json.dumps(meta), encoding='utf-8')

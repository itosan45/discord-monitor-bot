"""2026-10-11 画像担当が納品した新素材を、ゲーム用のアトラス(新キー)にする。元PNGは変更しない。
1. 馬上旋風_<武将>_主武器_8コマ_v1.png (576x416 x8) -> atlas_mountwhirl2_<hero>.webp  meta {'whirl':[8コマ]}
   原点は馬のひづめの線(y=384)・セルの中央(x=288)。余白は詰める。馬の大きさはmountfull/mountbody3と同じ描き方なので倍率1。
2. 各武将の新しい攻撃(256x256のコマ) -> atlas_atk3_<hero>.webp  meta {name:[コマ...]}
   身長は、その武将の既存の通常1の1コマ目(構え)の描画高さにそろえる。原点は足元(接地)。コマごとの位置関係は原画のセルのまま(踏み込みも保つ)。
   上杉景勝: iai=居合斬り, ichi=踏み込み一文字 / 宮本武蔵: nito=左右交互二刀連撃 / 武田信玄: push=軍配押し打ち / 織田信長: sweep=片手大薙ぎ
3. 石田三成 鉄扇空中回転(扇だけ8コマ) -> atlas_atk3_mitsu.webp meta {'fan':[8コマ]} 扇の中心を原点にする(幅64pxへ縮める)
使い方: python3 game/tools/pack_new_art_v2.py"""
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


def webp(img, path, lossless=False):
    b = io.BytesIO()
    img.save(b, 'WEBP', lossless=lossless, quality=82, method=6)
    path.write_bytes(b.getvalue())
    return len(b.getvalue()) // 1024


def cells(name, n):
    a = mk.keyim(Image.open(SRC / name))
    w = a.shape[1] // n
    return [mk.clean(a[:, i * w:(i + 1) * w]) for i in range(n)]


def bbox(c):
    ys, xs = np.where(c[..., 3] > 40)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def union(cs):
    bs = [bbox(c) for c in cs]
    return min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs)


def pack(cs, origin, scale=1.0, crop=None):
    """cs: RGBAコマ配列。origin=(ox,oy) はセル内の基準点(足元など)。縮尺scaleで縮めた画像を詰めて並べ、各コマを [x,y,w,h,-ox*s,-oy*s,1] で返す。"""
    x0, y0, x1, y1 = crop or union(cs)
    W, H = max(1, round((x1 - x0) * scale)), max(1, round((y1 - y0) * scale))
    atlas = Image.new('RGBA', ((W + 2) * len(cs), H), (0, 0, 0, 0))
    arr = []
    for i, c in enumerate(cs):
        im = Image.fromarray(c[y0:y1, x0:x1], 'RGBA')
        if scale != 1.0:
            im = im.resize((W, H), Image.LANCZOS)
        atlas.paste(im, (i * (W + 2), 0))
        arr.append([i * (W + 2), 0, W, H, float(round(-(origin[0] - x0) * scale, 2)), float(round(-(origin[1] - y0) * scale, 2)), 1])
    return atlas, arr


# 1. 旋風突撃(馬上、8コマ、全6人)
for h, jp in HERO.items():
    cs = cells(f'馬上旋風_{jp}_主武器_8コマ_v1.png', 8)
    atlas, arr = pack(cs, (288, 384))
    meta[f'mountwhirl2_{h}'] = {'whirl': arr}
    print(f'mountwhirl2_{h}', atlas.size, webp(atlas, SPRITES / f'atlas_mountwhirl2_{h}.webp'), 'KB')

# 2. 新しい攻撃(徒歩)
JOBS = {
    'kage': [('iai', '上杉景勝_居合斬り_6コマ_v1.png', 6), ('ichi', '上杉景勝_踏み込み一文字_6コマ_v1.png', 6)],
    'musashi': [('nito', '宮本武蔵_左右交互二刀連撃_6コマ_v1.png', 6)],
    'shin': [('push', '武田信玄_軍配押し打ち_6コマ_v1.png', 6)],
    'nobu': [('sweep', '織田信長_片手大薙ぎ_6コマ_v1.png', 6)],
}
for h, jobs in JOBS.items():
    ref = meta[h]['a1'][0]
    target = ref[3] * ref[6]   # 既存の通常1の1コマ目の描画高さ(構えの背の高さ)
    out = {}
    pieces = []
    for nm, fn, n in jobs:
        cs = cells(fn, n)
        b0 = bbox(cs[0])
        s = target / (b0[3] - b0[1])
        # 足元: 1コマ目の最下段(下8px)の左右中央
        a0 = cs[0][..., 3] > 40
        ys, xs = np.where(a0)
        fy = ys.max() + 1
        fxs = xs[ys >= fy - 8]
        fx = (fxs.min() + fxs.max()) / 2
        pieces.append((nm, cs, (fx, fy), s))
        print(h, nm, 'scale', round(s, 3), 'foot', (round(fx), int(fy)))
    # 1つのアトラスに縦に積む
    rows = []
    for nm, cs, origin, s in pieces:
        atlas, arr = pack(cs, origin, s)
        rows.append((nm, atlas, arr))
    AW = max(a.width for _, a, _ in rows)
    AH = sum(a.height + 2 for _, a, _ in rows)
    big = Image.new('RGBA', (AW, AH), (0, 0, 0, 0))
    y = 0
    for nm, a, arr in rows:
        big.paste(a, (0, y))
        out[nm] = [[q[0], q[1] + y, q[2], q[3], q[4], q[5], q[6]] for q in arr]
        y += a.height + 2
    meta[f'atk3_{h}'] = out
    print(f'atk3_{h}', big.size, webp(big, SPRITES / f'atlas_atk3_{h}.webp'), 'KB')

# 3. 鉄扇の空中回転(三成の扇ブーメラン用、扇だけ)
cs = cells('石田三成_鉄扇空中回転_8コマ_v1.png', 8)
x0, y0, x1, y1 = union(cs)
sc = 64 / max(x1 - x0, y1 - y0)
# 扇の中心 = 各コマの不透明部の重心(のコマ間平均)。コマごとに中心を合わせて回転が軸ぶれしないようにする
arr = []
S = 72
atlas = Image.new('RGBA', (S * 8, S), (0, 0, 0, 0))
for i, c in enumerate(cs):
    ys, xs = np.where(c[..., 3] > 40)
    cx, cy = (xs.min() + xs.max() + 1) / 2, (ys.min() + ys.max() + 1) / 2
    im = Image.fromarray(c, 'RGBA')
    sm = im.resize((round(256 * sc), round(256 * sc)), Image.LANCZOS)
    ox = round(cx * sc - S / 2)
    oy = round(cy * sc - S / 2)
    tile = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    tile.paste(sm, (-ox, -oy))
    atlas.paste(tile, (i * S, 0))
    arr.append([i * S, 0, S, S, -S / 2, -S / 2, 1])
meta.setdefault('atk3_mitsu', {})['fan'] = arr
print('atk3_mitsu', atlas.size, webp(atlas, SPRITES / 'atlas_atk3_mitsu.webp'), 'KB')

# 4. 馬上の通常攻撃1〜3段(主武器、6コマ×3、全6人) -> mountnorm_<hero> {n1,n2,n3}。原点は旋風と同じ(ひづめの線y=384・セル中央x=288)
for h, jp in HERO.items():
    seq = [cells(f'馬上通常{n}_{jp}_主武器_6コマ_v1.png', 6) for n in (1, 2, 3)]
    crop = union([c for cs in seq for c in cs])
    out, rows = {}, []
    for n, cs in enumerate(seq, 1):
        atlas, arr = pack(cs, (288, 384), crop=crop)
        rows.append((f'n{n}', atlas, arr))
    big = Image.new('RGBA', (rows[0][1].width, sum(a.height + 2 for _, a, _ in rows)), (0, 0, 0, 0))
    y = 0
    for nm, a, arr in rows:
        big.paste(a, (0, y))
        out[nm] = [[q[0], q[1] + y, q[2], q[3], q[4], q[5], q[6]] for q in arr]
        y += a.height + 2
    meta[f'mountnorm_{h}'] = out
    print(f'mountnorm_{h}', big.size, webp(big, SPRITES / f'atlas_mountnorm_{h}.webp'), 'KB')

# 5. 敵の新しい動き(足軽): 受け流し反撃(刀)・横薙ぎ(槍)・装填(鉄砲)。256x384のコマ、原点は足元(128,360)。
#    身長は既存の敵の通常攻撃1コマ目の描画高さにそろえる。
ENEMY = [('sword', 'parry', '敵_足軽刀_受け流し反撃_6コマ_v1.png', 6), ('spear', 'sweep', '敵_足軽槍_横薙ぎ_6コマ_v1.png', 6), ('gun', 'reload', '敵_鉄砲足軽_装填_8コマ_v1.png', 8)]
out, rows = {}, []
for ty, nm, fn, n in ENEMY:
    ref = meta[ty]['a1'][0]
    cs = cells(fn, n)
    b0 = bbox(cs[0])
    sc = ref[3] * ref[6] / (b0[3] - b0[1])
    atlas, arr = pack(cs, (128, 360), sc)
    rows.append((nm, atlas, arr))
    print('enemy', ty, nm, 'scale', round(sc, 3))
AW = max(a.width for _, a, _ in rows)
big = Image.new('RGBA', (AW, sum(a.height + 2 for _, a, _ in rows)), (0, 0, 0, 0))
y = 0
for nm, a, arr in rows:
    big.paste(a, (0, y))
    out[nm] = [[q[0], q[1] + y, q[2], q[3], q[4], q[5], q[6]] for q in arr]
    y += a.height + 2
meta['enemyx1'] = out
print('enemyx1', big.size, webp(big, SPRITES / 'atlas_enemyx1.webp'), 'KB')

# 6. 戦場の仕掛け: 竹柵・木盾(健全/損傷/崩壊)、焚火(3コマの揺れ)。512x384のコマ、原点(256,360)、倍率0.63(足軽と同じ縮尺)
PROPS = [('fence', '戦場_竹柵_破壊_3コマ_v1.png', 3), ('mshield', '戦場_木盾_破壊_3コマ_v1.png', 3), ('fire', '戦場_焚火_燃焼_3コマ_v1.png', 3)]
out, rows = {}, []
for nm, fn, n in PROPS:
    cs = cells(fn, n)
    atlas, arr = pack(cs, (256, 360), 0.63)
    rows.append((nm, atlas, arr))
AW = max(a.width for _, a, _ in rows)
big = Image.new('RGBA', (AW, sum(a.height + 2 for _, a, _ in rows)), (0, 0, 0, 0))
y = 0
for nm, a, arr in rows:
    big.paste(a, (0, y))
    out[nm] = [[q[0], q[1] + y, q[2], q[3], q[4], q[5], q[6]] for q in arr]
    y += a.height + 2
meta['props1'] = out
print('props1', big.size, webp(big, SPRITES / 'atlas_props1.webp'), 'KB')

(SPRITES / 'sprmeta.json').write_text(json.dumps(meta), encoding='utf-8')

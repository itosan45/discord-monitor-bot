"""2026-10-16 オーナー作の「黒具足の薙刀武者」(家康の親衛隊)のシートを、ゲーム用のアトラス(新キー kurogusoku)にする。元のJPEGは変更しない。
元: game/experiments/owner_naginata_20261016/naginata_sheet_A_*.jpg・_B_*.jpg(2752x1536、左に文字の列、11列x6行のマス目、マゼンタ背景のJPEG)。
- マス目: x=264から幅223で11列。行は人物の切れ目で分ける(B: 待機・走り・攻撃1・居合い・ダメージ・死亡 / A: ジャンプ攻撃・走り・防御・必殺・ダメージ・死亡)。
- マゼンタとうすい格子線を透明にし、縁のマゼンタのにじみを抜く。マスの外から入り込んだ小さな欠片は捨てる。
- 原点: マスの中央・その行の接地線(コマの下端の中央値。死亡は自分の下端)。縮尺は全行で1つ(SCALE)。
- 歩きの絵は無いので、走りの11コマを歩きの行に入れる(仮。A-026 で歩きを依頼中)。転倒・起き上がりは死亡の前半を使う(ボスと同じ描き方)。
使い方: python3 game/tools/pack_owner_kurogusoku.py"""
import io, json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[2]
SPRITES = ROOT / 'game' / 'sprites'
SRC = ROOT / 'game' / 'experiments' / 'owner_naginata_20261016'
SCALE = 0.8  # 待機の人物(約220px)を鎧武者(約175px)と同じ高さに
X0, CW, NCOL = 264, 223, 11
SHEETS = {
    'B': ('naginata_sheet_B_idle_run_atk1_atk2_hurt_dead.jpg', [0, 296, 551, 813, 1074, 1318, 1536]),
    'A': ('naginata_sheet_A_jump_block_ult_hurt_dead.jpg', [0, 296, 550, 817, 1092, 1318, 1536]),
}
# 行名: (シート, 行番号, コマ数)
ROWS = [('idle', 'B', 0, 5), ('walk', 'B', 1, 11), ('hit', 'B', 4, 5), ('a1', 'B', 2, 11), ('iai', 'B', 3, 11),
        ('leap', 'A', 0, 11), ('guard', 'A', 2, 11), ('big', 'A', 3, 11), ('dead', 'B', 5, 5)]


def key(a):
    r, g, b = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
    bg = (r > 120) & (b > 120) & (r - g > 25) & (b - g > 25)  # マゼンタ・格子線・桃色の光
    alpha = np.where(bg, 0, 255).astype(np.uint8)
    # 縁のにじみ: マゼンタ寄りの色は赤と青を緑の近くまで下げる
    sp = (r - g > 12) & (b - g > 12) & ~bg
    r2 = np.where(sp, g + (r - g) * 0.35, r)
    b2 = np.where(sp, g + (b - g) * 0.35, b)
    out = np.dstack([r2, g, b2, alpha]).astype(np.uint8)
    # 1px 削って縁を締める
    m = ndimage.binary_erosion(alpha > 0, iterations=1)
    out[..., 3] = np.where(m, 255, 0)
    return out


def keep_main(c):
    m = c[..., 3] > 0
    lab, n = ndimage.label(m)
    if n == 0:
        return c
    sizes = ndimage.sum(m, lab, range(1, n + 1))
    big = sizes.max()
    keep = np.zeros_like(m)
    H = m.shape[0]
    for i, s in enumerate(sizes, 1):
        ys, xs = np.where(lab == i)
        edge = ys.min() == 0 or ys.max() == H - 1
        if s >= big * 0.06 and not (edge and s < big * 0.5):
            keep |= lab == i
    c = c.copy()
    c[..., 3] = np.where(keep, c[..., 3], 0)
    # マスの左右の端で切れた斬撃の弧が直線に見えないよう、端の18pxを薄くする
    W = c.shape[1]
    d = np.minimum(np.arange(W), W - 1 - np.arange(W)).astype(float)
    c[..., 3] = (c[..., 3] * np.clip(d / 18.0, 0, 1)[None, :]).astype(np.uint8)
    return c


def cells(sheet, row, n):
    fn, bands = SHEETS[sheet]
    im = np.asarray(Image.open(SRC / fn).convert('RGB'))
    y0, y1 = bands[row], bands[row + 1]
    return [keep_main(key(im[y0:y1, X0 + i * CW:X0 + (i + 1) * CW])) for i in range(n)]


def bottom(c):
    ys, _ = np.where(c[..., 3] > 0)
    return ys.max() + 1


def pack_row(cs, origin, s):
    bs = []
    for c in cs:
        ys, xs = np.where(c[..., 3] > 0)
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


rows = []
for nm, sh, ri, n in ROWS:
    cs = cells(sh, ri, n)
    g = float(np.median([bottom(c) for c in cs])) if nm != 'dead' else float(max(bottom(c) for c in cs))
    if nm == 'leap':  # 跳んでいるコマ(前半)が多いので、着地しているコマ(後半)の下端を接地線に
        g = float(np.median([bottom(c) for c in cs[5:]]))
    row, arr = pack_row(cs, (CW / 2, g), SCALE)
    if nm == 'leap':  # 空中のコマは絵の中で足が浮いている。ゲーム側でも跳ぶ(z)ので、各コマの足元を原点にして高さが二重にならないように
        for q, c in zip(arr, cs):
            q[5] = float(round(q[5] + (g - bottom(c)) * SCALE, 2))
    rows.append((nm, row, arr))
AW = max(r.width for _, r, _ in rows)
AH = sum(r.height + 2 for _, r, _ in rows)
big = Image.new('RGBA', (AW, AH), (0, 0, 0, 0))
out, y = {}, 0
for nm, r, arr in rows:
    big.paste(r, (0, y))
    out[nm] = [[q[0], q[1] + y, q[2], q[3], q[4], q[5], q[6]] for q in arr]
    y += r.height + 2
meta = json.loads((SPRITES / 'sprmeta.json').read_text(encoding='utf-8'))
meta['kurogusoku'] = out
(SPRITES / 'sprmeta.json').write_text(json.dumps(meta, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
b = io.BytesIO()
big.save(b, 'WEBP', quality=84, method=6)
(SPRITES / 'atlas_kurogusoku.webp').write_bytes(b.getvalue())
print('kurogusoku', big.size, len(b.getvalue()) // 1024, 'KB', {k: len(v) for k, v in out.items()})

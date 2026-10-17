#!/usr/bin/env python3
"""天海の体だけの攻撃候補(画像担当 game/experiments/tenkai-attack-redraw-*/、300x430のコマ・純マゼンタ背景・鎖鉄球なし)を、
アトラス bten_tenkai(行 a1=通常攻撃6コマ / leap=跳躍叩きつけ5コマ)にする。鎖と鉄球はゲームがコードで描く(手の位置と鉄球の位置は下の表。コマ内の画素座標)。
使い方: python3 game/tools/pack_tenkai_body.py <通常攻撃.png> <跳躍叩きつけ.png>
 出力: game/sprites/atlas_bten_tenkai.webp, sprmeta.json の bten_tenkai, game/sprites/tenkai_ball.json(手→鉄球の表。体の座標系=足元中心・上が負)"""
import io, json, sys
from pathlib import Path
import numpy as np
from PIL import Image
ROOT = Path(__file__).resolve().parents[2]
SP = ROOT / 'game' / 'sprites'
CW, CH = 300, 430
S = 0.76  # 立ち姿の高さを待機(約190)に合わせる縮尺
# コマ内の画素座標: 手(鎖を持つ前の手) と 鉄球の位置。向きは右向き
BALL = {
 'a1': [((230, 245), (95, 350)), ((115, 175), (60, 80)), ((280, 205), (480, 215)), ((285, 215), (500, 240)), ((240, 265), (80, 135)), ((230, 245), (100, 355))],
 'leap': [((250, 265), (60, 350)), ((115, 100), (110, 20)), ((110, 30), (150, -50)), ((230, 150), (330, 270)), ((60, 175), (300, 395))],
}
def cells(path, n):
    a = np.asarray(Image.open(path).convert('RGB')).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    bg = (r > 190) & (g < 90) & (b > 190)
    edge = (r > 140) & (b > 140) & (r - g > 55) & (b - g > 55)
    al = (~(bg | edge)).astype(np.uint8) * 255
    rgba = np.dstack([a.astype(np.uint8), al])
    return [rgba[:, i * CW:(i + 1) * CW] for i in range(n)]
meta = {}; tiles = []; ballout = {}
for row, path, n in (('a1', sys.argv[1], 6), ('leap', sys.argv[2], 5)):
    meta[row] = []; ballout[row] = []
    for i, c in enumerate(cells(path, n)):
        ys, xs = np.nonzero(c[..., 3] > 40)
        x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        im = Image.fromarray(c[y0:y1, x0:x1]).resize((max(1, round((x1 - x0) * S)), max(1, round((y1 - y0) * S))), Image.LANCZOS)
        # 足元(絵の一番下)を接地線に。左右は足元の中心ではなくコマの中心(150)を原点にする
        offx = round((x0 - 150) * S, 2); offy = round(-(y1 - y0) * S, 2)
        meta[row].append([None, None, im.width, im.height, offx, offy, 1])
        tiles.append((row, i, im))
        (hx, hy), (bx, by) = BALL[row][i]
        ballout[row].append([round((hx - 150) * S, 1), round((hy - y1) * S, 1), round((bx - 150) * S, 1), round((by - y1) * S, 1)])
AW = 1024; x = y = rh = 0; pos = {}
for row, i, im in tiles:
    if x + im.width > AW: x = 0; y += rh + 2; rh = 0
    pos[(row, i)] = (x, y); x += im.width + 2; rh = max(rh, im.height)
H = y + rh + 2
atl = Image.new('RGBA', (AW, H), (0, 0, 0, 0))
for row, i, im in tiles: atl.alpha_composite(im, pos[(row, i)])
for row in meta:
    for i, q in enumerate(meta[row]): q[0], q[1] = int(pos[(row, i)][0]), int(pos[(row, i)][1])
atl.save(SP / 'atlas_bten_tenkai.webp', 'WEBP', quality=85, method=6)
m = json.load(open(SP / 'sprmeta.json')); m['bten_tenkai'] = meta
json.dump(m, open(SP / 'sprmeta.json', 'w'), ensure_ascii=False, separators=(',', ':'))
json.dump(ballout, open(SP / 'tenkai_ball.json', 'w'), ensure_ascii=False)
print('bten_tenkai', atl.size, {k: len(v) for k, v in meta.items()})

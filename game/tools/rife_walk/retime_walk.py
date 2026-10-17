"""歩きシートを「コマ間の脚の動きが一定」になるように取り直す(RIFE補間+経路長で再配分)。
使い方: python game/tools/rife_walk/retime_walk.py <入力PNG> <入力コマ数> <出力PNG> <出力コマ数> [--gif プレビュー.gif]
- 入力: 純マゼンタ背景の横並びシート(セル幅=シート幅/コマ数、高さ=シート高)。歩きは循環するので最後→最初も補間する。
- 出力: 同じセルの大きさで出力コマ数に取り直したシート。各組を細かく補間して脚(下半分)の経路長を測り、その長さが等間隔になる位置のコマを取る。
- 重み: game/tools/rife_walk/models/flownet_v4.25.pkl (README.md の手順で取得。リポジトリには入れない)。
- 結果はAI補間なので、槍の石突きの二重像・小さなゴミ点・縁のピンク残りが出ることがある。必ず目視して、ひどい所は手で直すか別コマにする。元PNGは上書きしない。
"""
import argparse
import os
import sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
import rife_core as R  # noqa: E402
import check_walk_evenness as C  # noqa: E402

GRID = 24  # 各組を何分割して経路長を測るか


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('n', type=int)
    ap.add_argument('dst')
    ap.add_argument('N', type=int)
    ap.add_argument('--weights', default=os.path.join(HERE, 'models', 'flownet_v4.25.pkl'))
    ap.add_argument('--gif', default=None)
    a = ap.parse_args()
    if os.path.exists(a.dst):
        sys.exit('出力先が既にあります。上書きしません: ' + a.dst)
    sheet = Image.open(a.src).convert('RGB')
    cw = sheet.size[0] // a.n
    assert cw * a.n == sheet.size[0], '幅がコマ数で割り切れません'
    frames = [np.asarray(sheet.crop((i * cw, 0, (i + 1) * cw, sheet.size[1]))) for i in range(a.n)]
    net = R.load(a.weights, 1.0)
    fine = []
    for i in range(a.n):
        for g in range(GRID):
            fine.append((i, g / GRID, frames[i] if g == 0 else R.interp(net, frames[i], frames[(i + 1) % a.n], g / GRID)))
    feats = [C.leg_feature(Image.fromarray(x[2])) for x in fine]
    seg = [float(np.sqrt(((feats[k] - feats[(k + 1) % len(feats)]) ** 2).sum())) for k in range(len(feats))]
    cum = np.concatenate([[0], np.cumsum(seg)])
    total = cum[-1]
    out = []
    for k in range(a.N):
        s = k * total / a.N
        kk = min(int(np.searchsorted(cum, s, side='right') - 1), len(fine) - 1)
        i, t, img = fine[kk]
        frac = (s - cum[kk]) / max(seg[kk], 1e-6)
        tt = min(t + frac / GRID, 0.999)
        out.append(frames[i] if (t == 0 and frac < 0.03) else R.interp(net, frames[i], frames[(i + 1) % a.n], tt))
    Image.fromarray(np.concatenate(out, axis=1)).save(a.dst)
    print('保存:', a.dst, f'{a.N}コマ')
    if a.gif:
        bg = np.array([92, 78, 62])
        gif = []
        for f in out:
            x = f.astype(int)
            m = np.clip(((x[..., 0] + x[..., 2]) / 2 - x[..., 1] - 60) / 120, 0, 1)
            gif.append(Image.fromarray((x * (1 - m[..., None]) + bg * m[..., None]).astype(np.uint8)))
        gif[0].save(a.gif, save_all=True, append_images=gif[1:], duration=int(800 / a.N), loop=0)
        print('プレビューGIF:', a.gif)
    print('--- 取り直し後の確認(目安) ---')
    sys.argv = ['check', a.dst, str(a.N), str(cw)]
    C.main()


if __name__ == '__main__':
    main()

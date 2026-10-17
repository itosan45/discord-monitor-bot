"""retime_walk.py の改良版。背景のマゼンタを色に混ぜずに補間する(縁・脚のピンク/紫の滲みを出さない)。
使い方: python game/tools/rife_walk/retime_walk_clean.py <入力PNG> <入力コマ数> <出力PNG> <出力コマ数> [--no-copy]
- 各コマを「色(背景を輪郭の外へ延ばして埋めたもの)」と「形(アルファ)」に分け、色から動きを求めて形も同じ動きで補間する。
- 出力は純マゼンタ背景に戻す。元の8コマそのもの(位置がほぼ一致するコマ)は元の絵をそのまま使う。
- 取り直す位置(脚の経路長が等間隔)は retime_walk.py と同じ方法。元PNGは上書きしない。
"""
import argparse
import os
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'sprites'))
import rife_core as R  # noqa: E402
import check_walk_evenness as C  # noqa: E402
from mk import keyim  # noqa: E402

GRID = 24


def prep(cell_rgb):
    k = keyim(Image.fromarray(cell_rgb)).astype(float)
    al = k[..., 3] / 255
    rgb = k[..., :3]
    fg = al >= 0.5
    idx = ndi.distance_transform_edt(~fg, return_distances=False, return_indices=True)
    ext = rgb[idx[0], idx[1]]
    return np.clip(ext, 0, 255).astype(np.uint8), al.astype(np.float32)


def unpurple(col, y0=130):
    """補間で脚に出る紫/ピンクを、赤〜茶に寄せる(青成分を緑の近くまで下げる)。元の絵にある色は脚の高さでは通常この条件に入らない。"""
    c = col.astype(int)
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    ex = np.minimum(r, b) - g
    m = (ex > 10) & (r > g + 10)
    m[:y0] = False
    c[..., 2] = np.where(m, np.minimum(b, g + 8), b)
    return c.astype(np.uint8)


def compose(col, al):
    a = np.clip((al - 0.4) / 0.2, 0, 1)
    lab, k = ndi.label(a > 0.5)  # 本体から離れた小さなゴミ点を消す(槍の穂先・旗の先などは本体と同じ塊か、十分大きい)
    if k > 1:
        sizes = ndi.sum(a > 0.5, lab, range(1, k + 1))
        for j in range(k):
            if sizes[j] < 40:
                a[lab == j + 1] = 0
    a = a[..., None]
    mag = np.array([255, 0, 255], float)
    return np.clip(col * a + mag * (1 - a), 0, 255).round().astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('n', type=int)
    ap.add_argument('dst')
    ap.add_argument('N', type=int)
    ap.add_argument('--weights', default=os.path.join(HERE, 'models', 'flownet_v4.25.pkl'))
    a = ap.parse_args()
    if os.path.exists(a.dst):
        sys.exit('出力先が既にあります。上書きしません: ' + a.dst)
    sheet = Image.open(a.src).convert('RGB')
    cw = sheet.size[0] // a.n
    raw = [np.asarray(sheet.crop((i * cw, 0, (i + 1) * cw, sheet.size[1]))) for i in range(a.n)]
    pre = [prep(f) for f in raw]
    net = R.load(a.weights, 1.0)

    def at(i, t):
        j = (i + 1) % a.n
        col, al = R.interp_rgba(net, pre[i][0], pre[j][0], pre[i][1], pre[j][1], t)
        return compose(unpurple(col), al)

    # 取り直す位置の測定は retime_walk.py と同じ(背景ごと補間した絵の脚の動き)。表示用の絵だけ at() で作り直す
    fine = []
    for i in range(a.n):
        for g in range(GRID):
            fine.append((i, g / GRID, raw[i] if g == 0 else R.interp(net, raw[i], raw[(i + 1) % a.n], g / GRID)))
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
        out.append(raw[i] if (t == 0 and frac < 0.03) else at(i, tt))
    Image.fromarray(np.concatenate(out, axis=1)).save(a.dst)
    print('保存:', a.dst, f'{a.N}コマ')
    sys.argv = ['check', a.dst, str(a.N), str(cw)]
    C.main()


if __name__ == '__main__':
    main()

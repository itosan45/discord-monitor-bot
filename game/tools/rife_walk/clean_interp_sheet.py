"""補間で作った歩きシートの「手直し」を自動でやる後処理(元のコマは一切触らない)。
使い方: python game/tools/rife_walk/clean_interp_sheet.py <補間シートPNG> <コマ数> <元シートPNG> <元コマ数> <出力PNG> [接地線y]
- 元シートのコマと完全に同じコマはそのまま。補間コマだけ次を行う:
  ①脚の高さで紫/ピンクに寄った色を赤〜茶へ寄せる(補間で背景のマゼンタが混ざった所)
  ②半透明のゴーストを、はっきりした形(あり/なし)にする
  ③本体から離れた小さなゴミ点を消す
  ④接地線yを指定すると、足が浮いた補間コマ(最下端がyより1〜8px高い)をyまで下げる
- 出力は純マゼンタ背景(#FF00FF)。既存PNGは上書きしない。目視で確認すること。
"""
import os
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'sprites'))
from mk import keyim  # noqa: E402


def cells(path, n):
    im = Image.open(path).convert('RGB')
    cw = im.size[0] // n
    return [np.asarray(im.crop((i * cw, 0, (i + 1) * cw, im.size[1]))) for i in range(n)]


def clean_cell(cell, y0=130):
    k = keyim(Image.fromarray(cell)).astype(float)
    al = k[..., 3] / 255
    col = k[..., :3]
    r, g, b = col[..., 0], col[..., 1], col[..., 2]
    m = (np.minimum(r, b) - g > 10) & (r > g + 10)
    m[:y0] = False
    col[..., 2] = np.where(m, np.minimum(b, g + 8), b)
    shoe = m & (np.arange(m.shape[0])[:, None] >= 205) & (r < 175)  # 足先の暗い紫は茶(わらじ)へ
    col[..., 1] = np.where(shoe, np.maximum(g, 0.6 * r), g)
    col[..., 2] = np.where(shoe, np.minimum(col[..., 2], 0.45 * r), col[..., 2])
    a = np.clip((al - 0.4) / 0.2, 0, 1)
    lab, kk = ndi.label(a > 0.5)
    if kk > 1:
        sizes = ndi.sum(a > 0.5, lab, range(1, kk + 1))
        for j in range(kk):
            if sizes[j] < 40:
                a[lab == j + 1] = 0
    a = a[..., None]
    mag = np.array([255, 0, 255], float)
    return np.clip(col * a + mag * (1 - a), 0, 255).round().astype(np.uint8)


def ground(cell, y):
    """足元(最下端)がyより高い(浮いている)コマを、yまで下げる。補間で足が数px浮いたコマの接地線を揃える。"""
    a = keyim(Image.fromarray(cell))[..., 3] > 128
    ys = np.where(a.any(1))[0]
    d = y - int(ys.max())
    if d <= 0 or d > 8:
        return cell
    out = np.empty_like(cell)
    out[:d] = np.array([255, 0, 255], np.uint8)
    out[d:] = cell[:-d]
    return out


def main():
    src, n, orig, n0, dst = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), sys.argv[5]
    gy = int(sys.argv[6]) if len(sys.argv) > 6 else None  # 接地線(武器あり238、素手229)
    if os.path.exists(dst):
        sys.exit('出力先が既にあります。上書きしません: ' + dst)
    cs = cells(src, n)
    os_ = cells(orig, n0)
    out = []
    for i, c in enumerate(cs):
        same = any(np.abs(c.astype(int) - o.astype(int)).max() == 0 for o in os_)
        o = c if same else clean_cell(c)
        out.append(ground(o, gy) if (gy and not same) else o)
        print(i + 1, '元のまま' if same else '手直し')
    Image.fromarray(np.concatenate(out, axis=1)).save(dst)
    print('保存:', dst)


if __name__ == '__main__':
    main()

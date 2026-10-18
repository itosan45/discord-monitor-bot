"""歩きシートの「コマ間の脚の動きが一定か」を数値で見る目安ツール(numpy+PIL のみ)。
使い方: python game/tools/check_walk_evenness.py <シートPNG> <コマ数> [セル幅=高さ256]
純マゼンタ背景の横並びシートを想定。各コマの下半分(脚)の輪郭をぼかして縮小し、隣のコマ(最後→最初も)との差を測る。
- CV(ばらつき)は小さいほど等速に近い。目安: CV <= 0.20 かつ 最大/最小 <= 2.5。
- 「ほぼ同じポーズが連続」(平均の0.4倍未満)と「急に動く」(平均の1.6倍超)を番号付きで出す。
- あくまで目安。最終判断は1周を10〜20fpsで再生した目視で行う。
"""
import sys
import numpy as np
from PIL import Image, ImageFilter


def leg_feature(cell):
    a = np.asarray(cell.convert('RGB')).astype(int)
    fg = ~(((a[..., 0] + a[..., 2]) / 2 - a[..., 1]) > 120)  # 純マゼンタ背景を除く
    m = fg.astype(np.uint8) * 255
    m[: m.shape[0] // 2] = 0  # 下半分(脚)だけ
    im = Image.fromarray(m).filter(ImageFilter.GaussianBlur(5)).resize((128, 128), Image.BILINEAR)
    return np.asarray(im, dtype=np.float32) / 255


def main():
    path, n = sys.argv[1], int(sys.argv[2])
    cell = int(sys.argv[3]) if len(sys.argv) > 3 else 256
    sheet = Image.open(path)
    assert sheet.size[0] == cell * n, f'幅が {cell}x{n} になっていません: {sheet.size}'
    f = [leg_feature(sheet.crop((i * cell, 0, (i + 1) * cell, sheet.size[1]))) for i in range(n)]
    st = np.array([float(np.sqrt(((f[k] - f[(k + 1) % n]) ** 2).sum())) for k in range(n)])
    mean = st.mean()
    cv, ratio = st.std() / mean, st.max() / max(st.min(), 1e-6)
    print(f'{path}  {n}コマ')
    print('隣のコマとの差(1→2, 2→3 ... 最後→1):', [round(float(x), 1) for x in st])
    print(f'ばらつきCV={cv:.2f}  最大/最小={ratio:.2f}')
    for k, x in enumerate(st):
        if x < mean * 0.4:
            print(f'  注意: コマ{k + 1}→{(k + 1) % n + 1} はほぼ同じポーズ({x:.1f})')
        if x > mean * 1.6:
            print(f'  注意: コマ{k + 1}→{(k + 1) % n + 1} で急に動く({x:.1f}、平均{mean:.1f})')
    print('判定(目安):', '合格' if cv <= 0.20 and ratio <= 2.5 else '要見直し')


if __name__ == '__main__':
    main()

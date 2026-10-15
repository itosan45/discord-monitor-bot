"""A-019 の11枚を一括で補間16コマ→自動手直しにする(下絵づくり)。使い方: python game/tools/rife_walk/batch_others.py <出力フォルダ>
各シートについて、元のCV→取り直し後のCVを表示する。出力は <出力フォルダ>/<元の名前>_16コマ_等速化_下絵_v1.png"""
import os, subprocess, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'game', 'sprites'))
from mk import keyim  # noqa: E402
NAMES = ['敵_足軽槍_歩き_8コマ_v2', '石田三成_歩き_8コマ_v2', '敵_足軽刀_歩き_8コマ_v2', '上杉景勝_手ぶら_歩き_8コマ_v2', '敵_忍者_歩き_8コマ_v2',
         '敵_鉄砲足軽_歩き_8コマ_v2', '井伊直政_歩き_8コマ_v2', '上杉景勝_歩き_8コマ_v2_再生成版', '宮本武蔵_歩き_8コマ_v2', '織田信長_歩き_8コマ_v2', '最上義光_歩き_8コマ_v2']
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
only = sys.argv[2:] 
for nm in NAMES:
    if only and not any(o in nm for o in only):
        continue
    src = os.path.join(ROOT, 'assets', 'sprites', nm + '.png')
    raw = os.path.join(out, nm + '_16コマ_RIFE生_tmp.png')
    dst = os.path.join(out, nm.replace('_8コマ', '_16コマ') + '_等速化_下絵_v1.png')
    im = Image.open(src).convert('RGB'); cw = im.size[0] // 8
    bots = []
    for i in range(8):
        a = keyim(im.crop((i * cw, 0, (i + 1) * cw, im.size[1])))[..., 3] > 128
        ys = np.where(a.any(1))[0]; bots.append(int(ys.max()))
    gy = int(np.median(bots))
    def cv(path, n):
        t = subprocess.run([sys.executable, os.path.join(ROOT, 'game/tools/check_walk_evenness.py'), path, str(n), str(cw)], capture_output=True, text=True).stdout
        return ' '.join(l.strip() for l in t.splitlines() if 'CV=' in l or '判定' in l)
    print('==', nm, 'セル幅', cw, '接地(中央値)', gy, '| 元', cv(src, 8), flush=True)
    if os.path.exists(dst):
        print('-> 既存', cv(dst, 16), flush=True); continue
    r = subprocess.run([sys.executable, os.path.join(HERE, 'retime_walk.py'), src, '8', raw, '16'], capture_output=True, text=True)
    if r.returncode:
        print('NG retime', r.stderr[-300:]); continue
    r = subprocess.run([sys.executable, os.path.join(HERE, 'clean_interp_sheet.py'), raw, '16', src, '8', dst, str(gy)], capture_output=True, text=True)
    os.remove(raw)
    if r.returncode:
        print('NG clean', r.stderr[-300:]); continue
    print('->', cv(dst, 16), flush=True)

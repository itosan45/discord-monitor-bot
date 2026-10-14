"""幸村の歩き(武器あり・素手)を差し替えた試験用アトラス walkx_yuki / walkx_yuki_u を作る。
既存のアトラス作成(game/sprites/mk.py, mku.py)と同じ処理・同じ倍率・同じ接地で、歩きだけを別のシートに置き換える。
- 既存の atlas_yuki.webp / atlas_yuki_u.webp / PNG は変更しない。新しい atlas_walkx_yuki.webp / atlas_walkx_yuki_u.webp と、
  sprmeta.json / hands.json に walkx_yuki / walkx_yuki_u を追加するだけ。
使い方(リポジトリ直下から):
  python game/tools/pack_yuki_walkx.py --armed <武器ありシートPNG> --unarmed <素手シートPNG> --n 16 [--validate]
  --validate: 作る前に、現行の8コマ(依頼仕様版・手ぶら_v2)で同じ処理を行い、既存の sprmeta と一致するか確認する(書き込みはしない)。
"""
import argparse, json, os, shutil, sys, tempfile
from pathlib import Path
import numpy as np
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument('--armed', type=Path, required=True)
ap.add_argument('--unarmed', type=Path, required=True)
ap.add_argument('--n', type=int, default=16)
ap.add_argument('--validate', action='store_true')
args = ap.parse_args()
args.armed = args.armed.resolve()
args.unarmed = args.unarmed.resolve()
ROOT = Path(__file__).resolve().parents[2]
SPR = ROOT / 'game' / 'sprites'
os.chdir(SPR)
sys.path.insert(0, str(SPR))
import mk  # noqa: E402

exec(open('bodyh.py').read().split("for h in sys.argv")[0].replace("M=json.load(open('sprmeta.json'))", ""))  # body()
M = json.load(open('sprmeta.json'))
orig_find = mk.find
tmp = Path(tempfile.mkdtemp())
SRCDIR = Path(mk.SRC)


def link(name, src):
    p = tmp / name
    shutil.copyfile(src, p)
    return name


def run(armed_png, unarmed_png, n, write):
    # --- 武器あり: 'yuki' の idle(倍率の基準) + 差し替えた歩き
    walk_a = link(f'walkx_{n}コマ_armed.png', armed_png)
    walk_u = link(f'walkx_{n}コマ_unarmed.png', unarmed_png)
    idle_a = orig_find('yuki', '待機_4')
    link(idle_a, SRCDIR / idle_a)
    idle_u = None
    for suf in ['_v3', '_v2', '']:
        c = mk.HERO['yuki'] + '_手ぶら_待機_4コマ' + suf + '.png'
        if (SRCDIR / c).exists():
            idle_u = c
            break
    link(idle_u, SRCDIR / idle_u)
    mk.SRC = str(tmp) + '/'

    def fnd(h, key):
        if key.startswith('歩き'):
            return walk_u if h.endswith('_u') else walk_a
        return idle_u if h.endswith('_u') else idle_a
    mk.find = fnd
    mk.REMAP = {}
    mk.ANIM = [('idle', '待機_4'), ('walk', '歩き_6')]
    at, meta, by = mk.build('yuki', Hg=190)
    armed = (at, meta, by)
    # --- 素手: mku.py と同じ。基準は現行の武器ありアトラスの idle+walk の体の面積
    mk.HERO['yuki_u'] = mk.HERO['yuki']
    mk.NAME['yuki_u'] = mk.HERO['yuki']
    img = Image.open(str(ROOT / 'gfx' / 'atlas_yuki.webp')).convert('RGBA')
    ref = np.median([body(img, q)[2] for q in M['yuki']['idle'] + M['yuki']['walk'] if q and body(img, q)])
    mk.KFIX = dict(mk.KFIX)
    for _ in range(2):
        at, meta, by = mk.build('yuki_u', Hg=190)
        ia = at.convert('RGBA')
        for an, fr in meta.items():
            a = np.median([body(ia, q)[2] for q in fr if q and body(ia, q)])
            k = float(np.sqrt(ref / a))
            mk.KFIX[('yuki_u', an)] = mk.KFIX.get(('yuki_u', an), 1.0) * max(0.6, min(1.6, k))
    at, meta, by = mk.build('yuki_u', Hg=190)
    unarmed = (at, meta, by)
    mk.find = orig_find
    return armed, unarmed


def compare(name, got, want):
    worst = 0
    for g, w in zip(got, want):
        if g is None or w is None:
            continue
        worst = max(worst, abs(g[4] - w[4]), abs(g[5] - w[5]), abs(g[2] - w[2]), abs(g[3] - w[3]), abs(g[6] - w[6]) * 100)
    print(f'  {name}: 位置・大きさ・倍率の最大差 {worst:.2f}(0〜1なら一致)')
    return worst


if args.validate:
    a = SRCDIR / '真田幸村_歩き_8コマ_依頼仕様版.png'
    u = SRCDIR / '真田幸村_手ぶら_歩き_8コマ_v2.png'
    armed, unarmed = run(a, u, 8, False)
    print('検証(現行8コマで同じ処理):')
    w1 = compare('武器あり walk', armed[1]['walk'], M['yuki']['walk'])
    w2 = compare('素手 walk', unarmed[1]['walk'], M['yuki_u']['walk'])
    sys.exit(0 if max(w1, w2) <= 2.0 else 'NG: 既存と一致しない')

armed, unarmed = run(args.armed, args.unarmed, args.n, True)
hands = json.load(open('hands.json'))
for key, (at, meta, by) in (('walkx_yuki', armed), ('walkx_yuki_u', unarmed)):
    open(f'atlas_{key}.webp', 'wb').write(by)
    M[key] = {'walk': meta['walk']}
    hy = hands['yuki_u']['walk'][0] if key.endswith('_u') else None
    if key.endswith('_u'):
        hands[key] = {'walk': [list(hy) for _ in meta['walk']]}
    print(key, at.size, len(by) // 1024, 'KB', len(meta['walk']), 'コマ')
json.dump(M, open('sprmeta.json', 'w'), ensure_ascii=False, separators=(',', ':'))
json.dump(hands, open('hands.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print('書き込み: atlas_walkx_yuki.webp, atlas_walkx_yuki_u.webp, sprmeta.json, hands.json')

"""2026-10-14 鉄球大僧の色違い(オーナー「この見た目で3体出てくると違和感がすごい。服の色か肌の色で違いをつけて」)。
atlas_monk.webp(pack_monk_v3.py の後に)から、同じコマ配置の色違い2枚 atlas_monk_b.webp(緑の袈裟) / atlas_monk_c.webp(朱赤の袈裟+日に焼けた肌)を作る。
コマの座標は元と同じなので sprmeta['monk_b'] / ['monk_c'] は ['monk'] の複製。元PNGと元の atlas_monk.webp は変更しない。
色の決め方(HSV): 袈裟は色相240〜360°(青紫〜赤紫)の彩度のある部分 → 目標の色相へ回す。肌は色相12〜42°・彩度0.45以上・明度0.55以上の部分(濃い茶の袴・巻き布は含まない)を、c は明るさ0.80倍・彩度1.15倍で日焼けさせる。
使い方: python3 game/tools/pack_monk_v3.py && python3 game/tools/pack_monk_variants.py  → cd game && python3 build.py"""
import io, json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SPRITES = ROOT / 'game' / 'sprites'
src = Image.open(SPRITES / 'atlas_monk.webp').convert('RGBA')
a = np.array(src)
rgb = Image.fromarray(a[..., :3], 'RGB').convert('HSV')
hsv = np.array(rgb).astype(float)
H, S, V = hsv[..., 0] * 360 / 255, hsv[..., 1] / 255, hsv[..., 2] / 255
vest = (H >= 240) & (H <= 360) & (S > 0.10)
skin = (H >= 12) & (H <= 42) & (S >= 0.45) & (V >= 0.55)


def make(name, vest_hue, vest_sat, skin_v, skin_s):
    h, s, v = H.copy(), S.copy(), V.copy()
    h[vest] = (vest_hue + (h[vest] - 290) * 0.35) % 360   # 元の袈裟の中心(約290°)を目標の色相へ。もとの色相のばらつき(250〜350°)は0.35倍に縮めて、1色に見えるようにする
    s[vest] = np.clip(s[vest] * vest_sat, 0, 1)
    v[vest] = np.clip(v[vest] * (1.08 if vest_hue < 200 else 1.0), 0, 1)
    s[skin] = np.clip(s[skin] * skin_s, 0, 1)
    v[skin] = np.clip(v[skin] * skin_v, 0, 1)
    out = np.dstack([h / 360 * 255, s * 255, v * 255]).round().clip(0, 255).astype('uint8')
    rgb2 = np.array(Image.fromarray(out, 'HSV').convert('RGB'))
    res = np.dstack([rgb2, a[..., 3]])
    b = io.BytesIO()
    Image.fromarray(res, 'RGBA').save(b, 'WEBP', lossless=False, quality=82, method=6)
    (SPRITES / f'atlas_{name}.webp').write_bytes(b.getvalue())
    return len(b.getvalue()) // 1024


kb = make('monk_b', vest_hue=135, vest_sat=1.15, skin_v=1.0, skin_s=1.0)
kc = make('monk_c', vest_hue=6, vest_sat=2.3, skin_v=0.80, skin_s=1.15)
meta = json.loads((SPRITES / 'sprmeta.json').read_text(encoding='utf-8'))
for k in ('monk_b', 'monk_c'):
    meta[k] = json.loads(json.dumps(meta['monk']))
(SPRITES / 'sprmeta.json').write_text(json.dumps(meta), encoding='utf-8')
print('vest px', int(vest.sum()), 'skin px', int(skin.sum()), 'monk_b', kb, 'KB', 'monk_c', kc, 'KB')

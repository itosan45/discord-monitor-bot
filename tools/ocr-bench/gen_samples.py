#!/usr/bin/env python3
"""カメラ撮影を模したOCRテスト画像を生成する。

実機写真が無い状態でもEasyOCRの精度を測れるように、
「印刷物をスマホで撮った」状況に近い劣化（傾き・射影変形・
手ブレ・照明ムラ・ノイズ・JPEG圧縮）を合成画像に加える。
"""
import json
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT_GOTHIC = "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"
FONT_PGOTHIC = "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf"

# (id, 説明, 行のリスト)
SAMPLES = [
    ("doc_form", "点検票のような日本語の帳票", [
        "床下点検報告書",
        "物件名  山田様邸",
        "点検日  2026年9月18日",
        "担当者  伊藤 太郎",
        "床下の湿度は62パーセントでした",
        "基礎に軽微なひび割れを確認",
    ]),
    ("label_mixed", "型番ラベル（英数字混在）", [
        "MODEL: DM-4520X",
        "S/N 8842-1170-093",
        "製造年月 2025/07",
        "定格電圧 AC100V 50/60Hz",
        "Made in Japan",
    ]),
    ("sign_large", "大きめの掲示・看板", [
        "関係者以外立入禁止",
        "安全第一",
        "STAFF ONLY",
    ]),
    ("receipt", "レシート風の細かい文字", [
        "ご利用明細",
        "コーヒー          480円",
        "サンドイッチ      620円",
        "合計             1100円",
        "お預り           2000円",
        "お釣り            900円",
    ]),
]

# (条件名, 説明, パラメータ)
CONDITIONS = [
    ("clean", "劣化なし（スキャナ相当の理想条件）",
     dict(blur=0.0, rot=0.0, persp=0.0, noise=0, jpeg=95, shading=0.0)),
    ("phone_good", "明るい室内で丁寧に撮影",
     dict(blur=0.6, rot=1.5, persp=0.012, noise=4, jpeg=85, shading=0.12)),
    ("phone_tilt", "斜めから手持ちで撮影",
     dict(blur=1.0, rot=5.0, persp=0.045, noise=7, jpeg=75, shading=0.25)),
    ("phone_dark", "暗所・手ブレあり（最悪条件）",
     dict(blur=2.0, rot=3.0, persp=0.03, noise=14, jpeg=60, shading=0.45)),
]

W, H = 1400, 900


def render_page(lines, font_size):
    img = Image.new("RGB", (W, H), (248, 247, 243))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_PGOTHIC, font_size)
    y = 90
    for ln in lines:
        d.text((110, y), ln, font=font, fill=(24, 24, 28))
        y += int(font_size * 1.8)
    return img


def perspective_coeffs(src, dst):
    a = []
    b = []
    for (xs, ys), (xd, yd) in zip(src, dst):
        a.append([xd, yd, 1, 0, 0, 0, -xs * xd, -xs * yd])
        b.append(xs)
        a.append([0, 0, 0, xd, yd, 1, -ys * xd, -ys * yd])
        b.append(ys)
    res = np.linalg.solve(np.array(a, dtype=float), np.array(b, dtype=float))
    return res.tolist()


def degrade(img, p, rng):
    w, h = img.size
    if p["persp"] > 0:
        k = p["persp"]
        src = [(0, 0), (w, 0), (w, h), (0, h)]
        dst = [
            (w * k * rng.uniform(0.5, 1.5), h * k * rng.uniform(0.5, 1.5)),
            (w * (1 - k * rng.uniform(0.5, 1.5)), h * k * rng.uniform(0.2, 1.0)),
            (w * (1 - k * rng.uniform(0.2, 1.0)), h * (1 - k * rng.uniform(0.5, 1.5))),
            (w * k * rng.uniform(0.2, 1.0), h * (1 - k * rng.uniform(0.5, 1.5))),
        ]
        img = img.transform((w, h), Image.PERSPECTIVE,
                            perspective_coeffs(src, dst),
                            Image.BICUBIC, fillcolor=(248, 247, 243))
    if p["rot"]:
        img = img.rotate(rng.uniform(-p["rot"], p["rot"]), resample=Image.BICUBIC,
                         fillcolor=(248, 247, 243))
    if p["shading"] > 0:
        gx = np.linspace(1.0, 1.0 - p["shading"], w)
        gy = np.linspace(1.0 - p["shading"] * 0.4, 1.0, h)
        mask = np.outer(gy, gx)[:, :, None]
        img = Image.fromarray(np.clip(np.asarray(img, float) * mask, 0, 255).astype(np.uint8))
    if p["blur"] > 0:
        img = img.filter(ImageFilter.GaussianBlur(p["blur"]))
    if p["noise"] > 0:
        arr = np.asarray(img, float) + rng.normal(0, p["noise"], (h, w, 3))
        img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    return img


def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples")
    os.makedirs(out, exist_ok=True)
    rng = np.random.default_rng(20260918)
    manifest = []
    for sid, sdesc, lines in SAMPLES:
        fsize = 64 if sid == "sign_large" else (34 if sid == "receipt" else 44)
        page = render_page(lines, fsize)
        for cid, cdesc, params in CONDITIONS:
            img = degrade(page.copy(), params, rng)
            name = f"{sid}__{cid}.jpg"
            img.save(os.path.join(out, name), quality=params["jpeg"])
            manifest.append(dict(file=name, sample=sid, sample_desc=sdesc,
                                 condition=cid, condition_desc=cdesc, lines=lines))
    with open(os.path.join(out, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"generated {len(manifest)} images in {out}")


if __name__ == "__main__":
    main()

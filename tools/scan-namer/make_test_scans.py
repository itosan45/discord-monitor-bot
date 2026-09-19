#!/usr/bin/env python3
"""事務機スキャナの出力を模した検証用PDFを作る。

A4・200dpi相当の帳票を描き、スキャン特有の劣化（わずかな傾き、
用紙の地色、紙送りによる縦スジ、粒状ノイズ、JPEG圧縮）を載せて
PDFに保存する。実際の原稿が無くても scan_namer.py を検証できる。
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT = "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf"
W, H = 1654, 2339  # A4 200dpi

# (出力名, 見出し, 取引先, 日付行, 明細)
DOCS = [
    ("scan_001", "請求書", "株式会社中部白蟻研究所", "令和8年4月1日", [
        "山田建設株式会社 御中",
        "下記の通りご請求申し上げます。",
        "ご請求金額   金 286,000 円 (税込)",
        "",
        "品名             数量    単価      金額",
        "シロアリ防除工事   1式   240,000   240,000",
        "床下換気扇設置     2台    13,000    26,000",
        "小計                            266,000",
        "消費税                           20,000",
        "合計                            286,000",
        "",
        "お振込期限 令和8年4月30日",
    ]),
    ("scan_002", "御見積書", "東海シロアリ防除サービス", "2026年5月12日", [
        "浜松住宅設備 御中",
        "件名 床下環境改善工事",
        "お見積金額   金 154,000 円 (税込)",
        "",
        "品名             数量    単価      金額",
        "調湿材敷設        30m2    3,500   105,000",
        "基礎補修          1式    35,000    35,000",
        "消費税                           14,000",
        "合計                            154,000",
        "",
        "有効期限 発行後30日間",
    ]),
    ("scan_003", "床下点検報告書", "中部白蟻研究所", "令和8年3月18日", [
        "物件名 佐藤様邸",
        "点検日時 令和8年3月18日 10時30分",
        "担当者 伊藤",
        "",
        "点検結果",
        "シロアリ被害     認められず",
        "木材の腐朽       軽微 (浴室north側土台)",
        "床下湿度         68 パーセント",
        "基礎のひび割れ   3箇所 確認",
        "",
        "所見 換気状況の改善を推奨します。",
    ]),
    ("scan_004", "納品書", "株式会社浜松住宅設備", "2026/06/03", [
        "山田建設株式会社 御中",
        "下記の通り納品いたしました。",
        "",
        "品名             数量    単価      金額",
        "ユニットバス      1台   420,000   420,000",
        "洗面化粧台        1台    88,000    88,000",
        "合計                            508,000",
    ]),
    # 取引先一覧に載っていない会社。要確認に回るのが正しい挙動。
    ("scan_005", "請求書", "株式会社アカツキ工業", "令和8年7月9日", [
        "山田建設株式会社 御中",
        "ご請求金額   金 99,000 円 (税込)",
        "外構工事一式",
    ]),
]


def render(title, company, datestr, body):
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    f_title = ImageFont.truetype(FONT, 78)
    f_body = ImageFont.truetype(FONT, 34)
    f_small = ImageFont.truetype(FONT, 30)

    tw = d.textlength(title, font=f_title)
    d.text(((W - tw) / 2, 190), title, font=f_title, fill=(0, 0, 0))
    d.line([(W / 2 - tw / 2, 285), (W / 2 + tw / 2, 285)], fill=(0, 0, 0), width=4)

    d.text((1080, 360), datestr, font=f_small, fill=(0, 0, 0))
    d.text((1080, 420), company, font=f_body, fill=(0, 0, 0))
    d.text((1080, 470), "〒430-0852 静岡県浜松市中央区領家2丁目25-20",
           font=ImageFont.truetype(FONT, 22), fill=(0, 0, 0))
    d.text((1080, 505), "TEL 053-464-6733", font=ImageFont.truetype(FONT, 22),
           fill=(0, 0, 0))

    y = 640
    for line in body:
        d.text((190, y), line, font=f_body, fill=(0, 0, 0))
        y += 62
    return img


def scan_noise(img, rng, strength=1.0):
    """スキャナ特有の劣化を載せる。"""
    # わずかな傾き（原稿のセット誤差）
    img = img.rotate(rng.uniform(-0.8, 0.8) * strength, resample=Image.BICUBIC,
                     fillcolor=(255, 255, 255), expand=False)
    arr = np.asarray(img, dtype=float)
    # 用紙の地色（わずかに黄ばむ）
    arr *= np.array([1.0, 0.995, 0.975])
    # 紙送りによる縦スジ
    stripes = rng.normal(0, 2.0 * strength, (1, arr.shape[1], 1))
    arr += stripes
    # CIS読み取りの粒状ノイズ
    arr += rng.normal(0, 3.5 * strength, arr.shape)
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    img = img.filter(ImageFilter.GaussianBlur(0.5 * strength))
    return img


def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "testscans")
    os.makedirs(out, exist_ok=True)
    rng = np.random.default_rng(20260919)
    for name, title, company, datestr, body in DOCS:
        img = scan_noise(render(title, company, datestr, body), rng)
        # スキャナはグレースケールJPEGでPDFに埋めることが多い
        img = img.convert("L")
        path = os.path.join(out, name + ".pdf")
        img.save(path, "PDF", resolution=200.0, quality=70)
        print("wrote", path)


if __name__ == "__main__":
    main()

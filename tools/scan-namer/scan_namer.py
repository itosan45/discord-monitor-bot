#!/usr/bin/env python3
"""スキャンした書類をOCRして、中身からファイル名を付ける。

事務機スキャナが吐いたPDF/画像を読み、日付・取引先・書類種別を取り出して
`20260401_中部白蟻研究所_請求書.pdf` のような名前に整える。

OCRは画数の多い漢字を平気で読み違える（確認→碑観、基礎→基礁）。
そのため取引先名は「読めた文字をそのまま使う」のではなく、
設定ファイルに列挙した取引先一覧と照合して最も近いものを選ぶ。
これで誤読があっても正しい名前に戻せる。

既定は dry-run。実際に改名するには --apply を付ける。
"""
import argparse
import csv
import json
import os
import re
import shutil
import sys
import unicodedata
from datetime import date

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"}
PDF_EXT = {".pdf"}

# Windowsのファイル名に使えない文字
BAD_FILENAME_CHARS = re.compile(r'[\\/:*?"<>|\r\n\t]')

# 元号 -> 西暦の開始年
ERAS = {"令和": 2018, "平成": 1988, "昭和": 1925, "R": 2018, "H": 1988, "S": 1925}

# OCRが数字と取り違えやすい文字。日付を読むときだけ数字に戻す。
# 実測で「令和8年」が「令和呂年」になる例が出たため。
DIGIT_LOOKALIKE = str.maketrans({
    "O": "0", "o": "0", "〇": "0", "○": "0", "D": "0", "Q": "0",
    "l": "1", "I": "1", "|": "1", "i": "1", "元": "1",
    "Z": "2", "己": "2", "乙": "2",
    "Ｅ": "3",
    "A": "4",
    "S": "5", "s": "5",
    "G": "6", "b": "6",
    "T": "7",
    "B": "8", "呂": "8",
    "g": "9", "q": "9",
})
# 日付の数字部分として許す文字（あとで数字に直す）
D = r"[0-9OoDQ〇○lIi|元Z己乙ＥASsGbTB呂gq]"

# この語が直前にある日付は発行日ではない。支払期限を発行日と取り違えないため。
NOT_ISSUE_DATE = re.compile(
    r"(期限|支払|振込|振替|納期|納入|有効|締切|締め切|完了|着工|予定|until|due)")


# ---------------------------------------------------------------- 文字列処理

def normalize(s):
    """比較用に正規化する。全角半角・空白・記号の揺れを吸収する。"""
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"[\s　]+", "", s)
    return s


def strip_corp(s):
    """株式会社・(株)などの法人格表記を落とす。照合の邪魔になるため。"""
    return re.sub(r"(株式会社|有限会社|合同会社|合資会社|一般社団法人|"
                  r"公益社団法人|一般財団法人|公益財団法人|医療法人|学校法人|"
                  r"\(株\)|\(有\)|㈱|㈲)", "", s)


def levenshtein(a, b):
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def similarity(a, b):
    """0.0〜1.0。1.0が完全一致。"""
    if not a or not b:
        return 0.0
    return 1.0 - levenshtein(a, b) / max(len(a), len(b))


# ---------------------------------------------------------------- 項目の抽出

def _to_int(s):
    """OCRが取り違えた文字を数字に戻して整数にする。戻せなければNone。"""
    s = s.translate(DIGIT_LOOKALIKE)
    return int(s) if s.isdigit() else None


def find_dates(text):
    """本文に出てくる日付を全部拾う。(位置, 日付, 発行日らしさ) を返す。"""
    t = normalize(text)
    found = []

    # 令和6年4月1日 / R6.4.1 / 令和元年…
    for m in re.finditer(r"(令和|平成|昭和|R|H|S)\s*(%s{1,2})\s*[年\.\-/]\s*"
                         r"(%s{1,2})\s*[月\.\-/]\s*(%s{1,2})" % (D, D, D), t):
        y, mo, dd = _to_int(m.group(2)), _to_int(m.group(3)), _to_int(m.group(4))
        if None in (y, mo, dd):
            continue
        try:
            found.append((m.start(), date(ERAS[m.group(1)] + y, mo, dd)))
        except ValueError:
            pass

    # 2026年4月1日 / 2026/4/1 / 2026-04-01
    # 年の4桁も誤読されうる（2026 -> 2O26）ので、桁だけ拾って後で範囲を見る。
    for m in re.finditer(r"(%s{4})\s*[年\.\-/]\s*(%s{1,2})\s*"
                         r"[月\.\-/]\s*(%s{1,2})" % (D, D, D), t):
        y, mo, dd = _to_int(m.group(1)), _to_int(m.group(2)), _to_int(m.group(3))
        if None in (y, mo, dd) or not (1900 <= y <= 2099):
            continue
        try:
            found.append((m.start(), date(y, mo, dd)))
        except ValueError:
            pass

    out = []
    for pos, d in sorted(found):
        # 直前の語が「支払期限」などなら発行日ではない
        context = t[max(0, pos - 14):pos]
        out.append((pos, d, NOT_ISSUE_DATE.search(context) is None))
    return out


def extract_date(text):
    """発行日を1つ取り出す。支払期限などのラベルが付いた日付は後回しにする。"""
    dates = find_dates(text)
    if not dates:
        return None
    for _, d, is_issue in dates:
        if is_issue:
            return d
    return dates[0][1]


def extract_doctype(lines, doctypes, threshold):
    """書類種別を判定する。設定の見出し語と曖昧一致させる。

    「請求書」のような見出しは大きな文字で書かれていてOCRも比較的当たるが、
    それでも1文字の誤読はあるので完全一致は要求しない。
    """
    best = (None, 0.0)
    for canonical, variants in doctypes.items():
        for v in variants:
            nv = normalize(v)
            for idx, line in enumerate(lines):
                nl = normalize(line)
                if nv in nl:
                    score = 1.0
                else:
                    score = best_window_similarity(nl, nv)
                # 見出しは上の方にあることが多い。わずかに優遇する。
                score -= min(idx, 20) * 0.002
                if score > best[1]:
                    best = (canonical, score)
    return best if best[1] >= threshold else (None, best[1])


def best_window_similarity(haystack, needle):
    """haystackの中からneedleに最も近い部分文字列を探す。"""
    n = len(needle)
    if not haystack or not n:
        return 0.0
    if n >= len(haystack):
        return similarity(haystack, needle)
    best = 0.0
    for width in (n - 1, n, n + 1):
        if width <= 0:
            continue
        for i in range(0, len(haystack) - width + 1):
            s = similarity(haystack[i:i + width], needle)
            if s > best:
                best = s
    return best


# 宛先を示す敬称。この語がある行の会社名は「差出人」ではない。
ADDRESSEE_MARK = re.compile(r"(御中|様|殿|宛|行$)")


def extract_party(lines, parties, aliases, threshold, role="issuer"):
    """取引先を一覧との照合で決める。

    OCRの誤読を許容するため、行そのものと隣接2行の連結を候補にして
    一覧の各社名と曖昧一致させる。

    請求書には差出人と宛先の両方に会社名が載る。どちらも取引先一覧に
    入っていることがあるため、敬称（御中・様・殿）の有無で役割を判定し、
    role で指定された側だけを候補にする。
    role="issuer"    … 差出人（書類を発行した側）。既定
    role="addressee" … 宛先
    role="any"       … 区別しない
    """
    cands = []
    for i, line in enumerate(lines):
        n1 = normalize(line)
        cands.append((i, n1, bool(ADDRESSEE_MARK.search(n1))))
        if i + 1 < len(lines):
            n2 = normalize(line + lines[i + 1])
            cands.append((i, n2, bool(ADDRESSEE_MARK.search(n2))))

    if role == "issuer":
        cands = [c for c in cands if not c[2]]
    elif role == "addressee":
        cands = [c for c in cands if c[2]]

    best = (None, 0.0, "")
    for canonical in parties:
        names = [canonical] + list(aliases.get(canonical, []))
        for name in names:
            nn = strip_corp(normalize(name))
            if not nn:
                continue
            for idx, cand, _ in cands:
                c = strip_corp(cand)
                if not c:
                    continue
                score = 1.0 if nn in c else best_window_similarity(c, nn)
                # 取引先名は上部にあることが多い
                score -= min(idx, 30) * 0.002
                if score > best[1]:
                    best = (canonical, score, cand)
    if best[1] >= threshold:
        return best
    return (None, best[1], best[2])


# ---------------------------------------------------------------- 入出力

def render_pages(path, dpi, max_pages):
    """PDFなら指定DPIで画像化、画像ならそのまま返す。"""
    import numpy as np
    from PIL import Image

    ext = os.path.splitext(path)[1].lower()
    if ext in PDF_EXT:
        import pypdfium2 as pdfium
        doc = pdfium.PdfDocument(path)
        try:
            out = []
            for i in range(min(len(doc), max_pages)):
                page = doc[i]
                pil = page.render(scale=dpi / 72).to_pil()
                out.append(np.asarray(pil.convert("RGB")))
                page.close()
            return out
        finally:
            doc.close()
    return [np.asarray(Image.open(path).convert("RGB"))]


def ocr_lines(reader, image, row_tol=None):
    """EasyOCRの結果を行単位にまとめて返す。"""
    res = reader.readtext(image)
    boxes = []
    for box, text, conf in res:
        cy = sum(p[1] for p in box) / 4
        cx = sum(p[0] for p in box) / 4
        h = max(p[1] for p in box) - min(p[1] for p in box)
        boxes.append((cy, cx, text, conf, h))
    if not boxes:
        return [], 0.0
    boxes.sort(key=lambda r: r[0])
    tol = row_tol if row_tol else max(8, sum(b[4] for b in boxes) / len(boxes) * 0.6)

    rows = []
    for cy, cx, text, conf, h in boxes:
        if rows and abs(cy - rows[-1][0]) <= tol:
            rows[-1][1].append((cx, text))
        else:
            rows.append((cy, [(cx, text)]))
    lines = []
    for _, parts in rows:
        parts.sort(key=lambda r: r[0])
        lines.append(" ".join(t for _, t in parts))
    mean_conf = sum(b[3] for b in boxes) / len(boxes)
    return lines, mean_conf


def sanitize(name):
    name = BAD_FILENAME_CHARS.sub("", name).strip(" .")
    return name or "無題"


def unique_path(directory, stem, ext):
    candidate = os.path.join(directory, stem + ext)
    n = 2
    while os.path.exists(candidate):
        candidate = os.path.join(directory, f"{stem}-{n}{ext}")
        n += 1
    return candidate


# ---------------------------------------------------------------- 本体

DEFAULT_CONFIG = {
    "filename_template": "{date}_{party}_{doctype}",
    "date_format": "%Y%m%d",
    "unknown_date": "日付不明",
    "unknown_party": "取引先不明",
    "unknown_doctype": "書類",
    "party_threshold": 0.62,
    "party_role": "issuer",
    "doctype_threshold": 0.70,
    "review_dir": "_要確認",
    "doctypes": {},
    "parties": [],
    "party_aliases": {},
}


def load_config(path):
    cfg = dict(DEFAULT_CONFIG)
    if path:
        with open(path, encoding="utf-8") as f:
            cfg.update(json.load(f))
    return cfg


def process(path, reader, cfg, dpi, max_pages):
    pages = render_pages(path, dpi, max_pages)
    lines, confs = [], []
    for img in pages:
        ls, c = ocr_lines(reader, img)
        lines.extend(ls)
        confs.append(c)
    text = "\n".join(lines)

    d = extract_date(text)
    doctype, dt_score = extract_doctype(lines, cfg["doctypes"], cfg["doctype_threshold"])
    party, p_score, p_raw = extract_party(lines, cfg["parties"], cfg["party_aliases"],
                                          cfg["party_threshold"], cfg["party_role"])

    fields = dict(
        date=d.strftime(cfg["date_format"]) if d else cfg["unknown_date"],
        party=party or cfg["unknown_party"],
        doctype=doctype or cfg["unknown_doctype"],
    )
    stem = sanitize(cfg["filename_template"].format(**fields))
    needs_review = (d is None) or (party is None) or (doctype is None)
    return dict(stem=stem, needs_review=needs_review, date=d, party=party,
                party_score=round(p_score, 3), party_raw=p_raw,
                doctype=doctype, doctype_score=round(dt_score, 3),
                mean_conf=round(sum(confs) / len(confs), 3) if confs else 0.0,
                pages=len(pages), text=text)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="スキャン済みファイル、またはそれが入ったフォルダ")
    ap.add_argument("--config", help="取引先一覧などの設定JSON")
    ap.add_argument("--out", help="改名したファイルの出力先。省略時は元の場所で改名")
    ap.add_argument("--apply", action="store_true",
                    help="実際に改名する。付けない限り何も変更しない")
    ap.add_argument("--copy", action="store_true", help="移動ではなく複製する")
    ap.add_argument("--dpi", type=int, default=200, help="PDFを画像化する解像度")
    ap.add_argument("--pages", type=int, default=1, help="OCRするページ数")
    ap.add_argument("--langs", default="ja,en")
    ap.add_argument("--log", help="結果を書き出すCSV")
    ap.add_argument("--dump-text", metavar="DIR", help="OCR結果の全文を保存するフォルダ")
    args = ap.parse_args()

    cfg = load_config(args.config)

    if os.path.isdir(args.input):
        targets = sorted(
            os.path.join(args.input, f) for f in os.listdir(args.input)
            if os.path.splitext(f)[1].lower() in (IMAGE_EXT | PDF_EXT))
    else:
        targets = [args.input]
    if not targets:
        print("対象ファイルが見つかりません", file=sys.stderr)
        return 1

    import easyocr
    reader = easyocr.Reader(args.langs.split(","), gpu=False, verbose=False)

    rows = []
    for path in targets:
        try:
            r = process(path, reader, cfg, args.dpi, args.pages)
        except Exception as e:
            print(f"!! {os.path.basename(path)}: {e}", file=sys.stderr)
            continue

        ext = os.path.splitext(path)[1].lower()
        dest_dir = args.out or os.path.dirname(os.path.abspath(path))
        if r["needs_review"] and cfg["review_dir"]:
            dest_dir = os.path.join(dest_dir, cfg["review_dir"])
        dest = unique_path(dest_dir, r["stem"], ext)

        mark = "要確認" if r["needs_review"] else "  OK  "
        print(f"[{mark}] {os.path.basename(path)}")
        print(f"          -> {os.path.relpath(dest, args.out or os.path.dirname(os.path.abspath(path)) or '.')}")
        print(f"          日付={r['date'] or '-'}  取引先={r['party'] or '-'}"
              f"({r['party_score']})  種別={r['doctype'] or '-'}({r['doctype_score']})"
              f"  conf={r['mean_conf']}")

        if args.dump_text:
            os.makedirs(args.dump_text, exist_ok=True)
            base = os.path.splitext(os.path.basename(path))[0]
            with open(os.path.join(args.dump_text, base + ".txt"), "w",
                      encoding="utf-8") as f:
                f.write(r["text"])

        if args.apply:
            os.makedirs(dest_dir, exist_ok=True)
            (shutil.copy2 if args.copy else shutil.move)(path, dest)

        rows.append(dict(source=os.path.basename(path), dest=os.path.basename(dest),
                         needs_review=r["needs_review"], date=r["date"],
                         party=r["party"], party_score=r["party_score"],
                         party_raw=r["party_raw"], doctype=r["doctype"],
                         doctype_score=r["doctype_score"], mean_conf=r["mean_conf"]))

    if args.log:
        with open(args.log, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(f"\nログ: {args.log}")

    ok = sum(1 for r in rows if not r["needs_review"])
    print(f"\n{len(rows)}件中 {ok}件が自動判定できました"
          f"（{len(rows) - ok}件は要確認）")
    if not args.apply:
        print("※ dry-run です。実際に改名するには --apply を付けてください。")
    return 0


if __name__ == "__main__":
    sys.exit(main())

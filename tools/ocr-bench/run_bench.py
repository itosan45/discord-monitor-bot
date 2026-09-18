#!/usr/bin/env python3
"""EasyOCRの認識精度を測るベンチマーク。

使い方:
  # 合成サンプル一式を評価
  python run_bench.py

  # 実写画像1枚を評価（正解テキストのファイルを添えると精度も出る）
  python run_bench.py --image /path/photo.jpg --truth /path/photo.txt
"""
import argparse
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))


def norm(s):
    """空白・改行を除き、全角英数記号を半角に寄せて比較しやすくする。"""
    s = s.translate(str.maketrans(
        "０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"
        "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ：／－",
        "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "abcdefghijklmnopqrstuvwxyz:/-"))
    return re.sub(r"\s+", "", s)


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


def cer(truth, hyp):
    t, h = norm(truth), norm(hyp)
    if not t:
        return 0.0 if not h else 1.0
    return levenshtein(t, h) / len(t)


def read_order(results):
    """認識結果を（おおまかな）行順に並べて連結する。"""
    items = []
    for box, text, conf in results:
        ys = [p[1] for p in box]
        xs = [p[0] for p in box]
        items.append((sum(ys) / 4, sum(xs) / 4, text, conf))
    items.sort(key=lambda r: (round(r[0] / 25), r[1]))
    return items


def line_match_rate(truth_lines, hyp_items):
    """正解の各行が、認識結果のどれかと一致（CER<=0.1）した割合。"""
    hyps = [t for _, _, t, _ in hyp_items]
    hit = 0
    detail = []
    for gt in truth_lines:
        best, best_c = "", 1.0
        for h in hyps:
            c = cer(gt, h)
            if c < best_c:
                best_c, best = c, h
        ok = best_c <= 0.10
        hit += ok
        detail.append(dict(truth=gt, best_match=best, cer=round(best_c, 3), ok=ok))
    return hit / len(truth_lines) if truth_lines else 0.0, detail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", help="単体で評価する画像")
    ap.add_argument("--truth", help="正解テキストファイル（1行1テキスト）")
    ap.add_argument("--langs", default="ja,en")
    ap.add_argument("--out", default=os.path.join(HERE, "results.json"))
    args = ap.parse_args()

    import easyocr
    langs = args.langs.split(",")
    t0 = time.time()
    reader = easyocr.Reader(langs, gpu=False, verbose=False)
    print(f"reader ready ({time.time() - t0:.1f}s, langs={langs})", file=sys.stderr)

    if args.image:
        jobs = [dict(file=args.image, sample="custom", sample_desc="実写画像",
                     condition="-", condition_desc="-",
                     lines=(open(args.truth, encoding="utf-8").read().splitlines()
                            if args.truth else []))]
        base = ""
    else:
        sdir = os.path.join(HERE, "samples")
        jobs = json.load(open(os.path.join(sdir, "manifest.json"), encoding="utf-8"))
        base = sdir

    rows = []
    for job in jobs:
        path = os.path.join(base, job["file"]) if base else job["file"]
        t0 = time.time()
        res = reader.readtext(path)
        dt = time.time() - t0
        items = read_order(res)
        hyp_text = "\n".join(t for _, _, t, _ in items)
        confs = [c for _, _, _, c in items]
        row = dict(file=os.path.basename(path), sample=job["sample"],
                   sample_desc=job["sample_desc"], condition=job["condition"],
                   condition_desc=job["condition_desc"], seconds=round(dt, 2),
                   boxes=len(items),
                   mean_conf=round(sum(confs) / len(confs), 3) if confs else 0.0,
                   text=hyp_text)
        if job["lines"]:
            truth = "\n".join(job["lines"])
            row["cer"] = round(cer(truth, hyp_text), 4)
            row["char_acc"] = round(max(0.0, 1 - row["cer"]) * 100, 1)
            rate, detail = line_match_rate(job["lines"], items)
            row["line_acc"] = round(rate * 100, 1)
            row["lines_detail"] = detail
        rows.append(row)
        tag = f"{row.get('char_acc', '-')}%" if "char_acc" in row else "(正解なし)"
        print(f"{row['file']:34s} 文字精度={tag:>8s} "
              f"行一致={row.get('line_acc', '-')}% conf={row['mean_conf']} {row['seconds']}s",
              file=sys.stderr)

    json.dump(rows, open(args.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\nwrote {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()

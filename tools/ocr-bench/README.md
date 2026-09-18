# EasyOCR 精度テスト用ベンチマーク

EasyOCR が「スマホのカメラで撮った写真」からどのくらい文字を拾えるかを
数値で測るための最小構成のツールです。

## 中身

| ファイル | 役割 |
|----------|------|
| `gen_samples.py` | 正解テキスト付きのテスト画像を生成（撮影時の劣化を合成） |
| `run_bench.py` | EasyOCR を実行し、文字精度(CER)・行一致率・推論時間を算出 |
| `samples/` | 生成された画像と `manifest.json`（正解データ） |
| `results.json` | ベンチ結果 |

## セットアップ

```bash
python3 -m venv .venv
.venv/bin/pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
.venv/bin/pip install easyocr
```

## 使い方

```bash
# 1. テスト画像を作る
.venv/bin/python tools/ocr-bench/gen_samples.py

# 2. 一括ベンチ
.venv/bin/python tools/ocr-bench/run_bench.py

# 3. 実写画像1枚を評価（正解テキストは1行1テキストのtxt）
.venv/bin/python tools/ocr-bench/run_bench.py --image photo.jpg --truth photo.txt
```

## 指標

- **文字精度** = `1 - CER`。CER は正解文字列との編集距離を正解の文字数で割った値。
  空白は無視し、全角英数は半角へ正規化してから比較する。
- **行一致率** = 正解の各行が認識結果のどれかと CER 0.1 以下で一致した割合。
- **conf** = EasyOCR が返す確信度の平均。低い値は誤読の目安になる。

## 撮影条件の再現

`gen_samples.py` は同じ原稿に対し 4 段階の劣化を掛けて出力する。

| 条件 | 内容 |
|------|------|
| `clean` | 劣化なし（スキャナ相当） |
| `phone_good` | 明るい室内で丁寧に撮影 |
| `phone_tilt` | 斜めから手持ちで撮影 |
| `phone_dark` | 暗所・手ブレあり |

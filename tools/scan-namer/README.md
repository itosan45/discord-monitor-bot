# スキャン書類 自動ファイル名付けツール

事務機スキャナが出力した PDF / 画像を OCR して、中身から
`20260401_中部白蟻研究所_請求書.pdf` のような名前を付ける。

## 考え方

OCR は画数の多い漢字を読み違える（`確認→碑観`、`基礎→基礁`）。
読めた文字をそのままファイル名にすると化けた名前が量産される。

そこで**取引先名は自由入力として読まず、設定ファイルの一覧と照合する**。
OCR が `中部白蟻研究所` を `中都白蟻研兜所` と読んでも、一覧の各社名との
距離を測れば正しい社名に戻せる。書類種別（請求書・見積書…）も同じ方式。
日付だけは一覧化できないので正規表現で拾う（和暦・西暦の主な書き方に対応）。

判定できなかったものは `_要確認` フォルダに分けるので、**間違った名前が
黙って付くことはない**。

## セットアップ

```bash
python3 -m venv .venv
.venv/bin/pip install easyocr pypdfium2
```

## 使い方

```bash
# 1. 設定をコピーして取引先一覧を自社のものに書き換える
cp tools/scan-namer/config.example.json config.json

# 2. まず dry-run（何も変更しない）
.venv/bin/python tools/scan-namer/scan_namer.py スキャン置き場 \
    --config config.json --log 結果.csv

# 3. 結果を確認してから実行
.venv/bin/python tools/scan-namer/scan_namer.py スキャン置き場 \
    --config config.json --out 整理済み --apply
```

### 主なオプション

| オプション | 説明 |
|------------|------|
| `--apply` | 実際に改名する。付けない限り一切変更しない |
| `--copy` | 移動ではなく複製する（元を残したいとき） |
| `--out DIR` | 出力先フォルダ。省略時は元の場所で改名 |
| `--dpi N` | PDF を画像化する解像度。既定200。文字が小さい原稿は300 |
| `--pages N` | OCR するページ数。既定1（表紙だけ見る） |
| `--log FILE` | 判定結果を CSV に出す（Excel で開ける BOM 付き） |
| `--dump-text DIR` | OCR の全文を保存。閾値調整の材料になる |

## 設定ファイル

```json
{
  "filename_template": "{date}_{party}_{doctype}",
  "date_format": "%Y%m%d",
  "party_threshold": 0.62,
  "doctype_threshold": 0.70,
  "review_dir": "_要確認",
  "doctypes": { "請求書": ["請求書", "ご請求書", "INVOICE"] },
  "parties": ["中部白蟻研究所"],
  "party_aliases": { "中部白蟻研究所": ["株式会社中部白蟻研究所", "中部白蟻"] }
}
```

- `parties` … 取引先の正式名。**ここがファイル名になる**
- `party_aliases` … 書類上の表記ゆれ。略称・英語表記・法人格付きを登録する
- `*_threshold` … 一致とみなす下限（0〜1）。上げると取りこぼす、
  下げると誤判定が増える。`--log` の score 列を見ながら調整する
- `filename_template` … `{date}` `{party}` `{doctype}` が使える

`株式会社` `(株)` `㈱` などの法人格は照合時に自動で無視するので、
一覧にどちらの表記で書いても一致する。

## 検証

実際の原稿が無くても動作確認できる。

```bash
.venv/bin/python tools/scan-namer/make_test_scans.py   # 検証用PDFを生成
.venv/bin/python tools/scan-namer/scan_namer.py tools/scan-namer/testscans \
    --config tools/scan-namer/config.example.json
```

`make_test_scans.py` は A4・200dpi の帳票に、スキャナ特有の劣化
（原稿セットの傾き、用紙の地色、紙送りの縦スジ、CIS の粒状ノイズ、
グレースケール JPEG 圧縮）を載せた PDF を作る。5件のうち1件は
取引先一覧に無い会社で、`_要確認` に回るのが正しい挙動。

# 歩きの等速化ツール(RIFE補間)

歩きシートの「コマ間の脚の動き」のばらつきを、AI補間(RIFE v4.25)で取り直して減らす実験用ツール。手描きで直せるなら手描きを優先する。

## 用意するもの
1. Python 3.10以上、`pip install torch numpy pillow`(CPUだけで動く。6〜16コマの1枚で数十秒〜数分)。
2. 重み `flownet_v4.25.pkl`(約24.6MB)を `game/tools/rife_walk/models/` に置く(リポジトリには入れない):
   `https://github.com/HolyWu/vs-rife/releases/download/model/flownet_v4.25.pkl`
   SHA-256: `6615790efd627772917205db291f51cd392528a157ecbb2ecaeec3bff8eb6de2`(違う場合は使わない)。重みは `weights_only=True`(テンソルだけ)で読み込む。
3. モデル定義 `rife_core.py` は、公開コード(IFNet_HDv3 v4.25)を読んで内容を確認し、書き写したもの。外部のコードは実行しない。

## 使い方
```
python game/tools/rife_walk/retime_walk.py assets/sprites/<入力>.png 8 <出力>.png 16 --gif <プレビュー>.gif
```
- 出力先が既にあると止まる(既存PNGは上書きしない)。出力は新しい版・新しい名前で保存する。
- 最後に `game/tools/check_walk_evenness.py` の目安(CV 0.20以下・最大/最小 2.5以下)を表示する。

## 注意
- 補間コマには、槍や旗の二重像・ゴミ点・縁のピンク残りが出ることがある。GIFと拡大で必ず目視する。
- 目安の数値は脚の輪郭の変化だけを見ている。最終判断は1周を10〜20fpsで再生した目視(滑り・足の交差)。
- 実験の記録: `game/experiments/rife_yukimura/README.md`。

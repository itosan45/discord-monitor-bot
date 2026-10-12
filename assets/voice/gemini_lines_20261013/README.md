# Gemini TTS で作り直した2つのセリフ(2026-10-13)

オーナー依頼「敵将、討ち取ったり」と「者ども、勝鬨をあげよう」を Gemini の音声生成で作り直し、ゲームに入れた。
オーナー自身の録音は消していない(下の「元に戻す」を参照)。

| ファイル | 内容 | 音のある長さ |
|---|---|---|
| teki_a.wav | 敵将、討ち取ったり！ (1回目) | 2.11 秒 |
| teki_b.wav | 同 (2回目)  ← **ゲームに採用** | 2.23 秒 |
| teki_c.wav | 同 (3回目、いちばん速い) | 1.75 秒 |
| kachi_a.wav | 者ども、勝鬨をあげよう！ (1回目) | 3.19 秒 |
| kachi_b.wav | 同 (2回目)  ← **ゲームに採用** | 3.05 秒 |

生成条件: Google AI Studio の音声生成(Gemini TTS)、声は無料の Algenib、Temperature 1。
スタイル指示(勝鬨): 「日本語。戦国武将が、敵の大将を討ち取った直後に、勝ち誇って、腹の底から大声で力強く言い放つ。威厳のある、低く太い男性の声。短く、鋭く、迫力をもって。」
(討ち取ったりの指示文は記録し忘れた。同じ系統の指示で、長さはほぼ同じ。再現が必要なら上の指示で作り直す。)
素のWAVは 24kHz モノラル。耳での確認はオーナーがする(作った側は聴けない)。

聴き比べ用: compare_tekisho_yuki_old_b_a_c.mp3(旧→b→a→c、幸村の高さ)、tekisho_6heroes_new.mp3(6人)、compare_kachidoki_old_b_a.mp3(旧→b→a)。各音の間は0.8秒。

## ゲームへの入れ方
`python3 game/tools/import_generated_lines.py [teki_?] [kachi_?]`  → そのあと `cd game && python3 build.py`
- 引数なしなら teki_b と kachi_b。別のテイクにしたいときは `... teki_c kachi_a` のように指定する。
- `vo`(6人の主人公の「討ち取ったり」)は主人公ごとに音の高さを変える(従来の v5 と同じ比率)。
- `uv.victory`(勝鬨の音頭)は、次の「えい・えい・おー」(3.2秒後)に被らないよう約2.7秒に速度をそろえる(採用の kachi_b は 3.01 秒→×1.11→出力 2.76 秒。従来の録音版も 2.78 秒)。

## 元に戻す
オーナー録音は `assets/voice/user/` に残っている。戻すには次の2つを実行して再ビルドする。
```
python3 game/tools/import_tekisho_vo.py      # vo を「敵将、討ち取ったり」オーナー録音版(v5)に戻す
python3 game/tools/import_user_voice.py      # uv.victory を「者ども、勝ち鬨をあげよ」オーナー録音版に戻す(charge/hey/seiya も同じ内容で作り直される)
cd game && python3 build.py
```

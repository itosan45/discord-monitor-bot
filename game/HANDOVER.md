# 関ヶ原乱舞 引き継ぎ書(Codex向け)

## 1. 概要
- 戦国ベルトスクロールアクション「関ヶ原乱舞」。IFストーリー(関ヶ原に真田幸村が参戦)。
- 公開先: https://sekigahara-ranbu.vercel.app (Vercel プロジェクト `sekigahara-ranbu`)
- リポジトリ: `itosan45/discord-monitor-bot`、作業ブランチ `ccr-851ab851-t271uq`(PR #3)
- 主な遊び方: Android の Chrome(横画面・タッチ操作)。友人にも共有されている。
- オーナーへの連絡・報告はすべて **日本語** で(英語表記は読めないと言われている)。

## 2. フォルダ構成
| 場所 | 中身 |
|---|---|
| `index.html` | **完成品**(自動生成。直接編集しない) |
| `gfx/` | 完成品が読む画像・音楽(`atlas_*.webp`=キャラ絵、`bg_*.webp`=背景、`bgm_thunder.mp3`=第一幕BGM) |
| `game/game_src.html` | **ゲーム本体のソース**(JavaScript 1ファイル、約2000行)。直すのは基本ここ |
| `game/build.py` | ソース+データ → `index.html` を組み立てる |
| `game/data/audio.json` | 効果音・声・BGM(base64)。音を差し替えない限り触らない |
| `game/sprites/` | キャラ絵の変換スクリプトと位置データ(sprmeta.json, hands.json) |
| `game/tests/` | ブラウザ自動テスト(Playwright) |
| `assets/sprites/` | 元絵(Codexが追加している連番シート。ファイル名 `<武将名>_<動作>_<N>コマ_v*.png`) |
| `vercel.json` | 公開時は index.html・manifest・gfx をそのまま配信するだけ |

## 3. 基本の作業手順
```bash
# 1) 必ず最新を取り込む
git fetch origin ccr-851ab851-t271uq && git merge origin/ccr-851ab851-t271uq
# 2) game/game_src.html を編集
# 3) 組み立て
cd game && python3 build.py          # → ../index.html が更新される
# 4) テスト(リポジトリ直下でサーバを立てる)
cd .. && python3 -m http.server 8765 &
node game/tests/tmeta.js            # 全画像に位置データがあるか → {"bad":[]} ならOK
node game/tests/tbo.js              # ボス戦が最後まで進むか
node game/tests/tht.js              # チュートリアル
node game/tests/tand2.js            # スマホ(Pixel 7 横)で攻撃・騎馬
node game/tests/tki.js              # 必殺ゲージ(必殺技では増えない/通常攻撃・被弾で増える)
node game/tests/tcharge.js          # 溜め攻撃が武器ごとに変わるか
node game/tests/tkusari.js          # 鎖鎌(回転・貫通投げ・引き寄せ)
node game/tests/tiai.js             # 居合
# 5) コミットしてプッシュ → Vercel に production デプロイ
```
- テストは `npm i playwright` 済みの環境、または `PLAYWRIGHT=/path/to/playwright node ...` で実行。
- **index.html だけ直してはいけない**(次の build で消える)。必ず game_src.html を直して build.py。

## 4. キャラ絵(スプライト)の更新手順
新しい元絵を `assets/sprites/` に入れたら:
```bash
cd game/sprites
python3 mk.py yuki            # 武将を指定して再生成(指定なしで全員。既存データには足し込み)
python3 mku.py                # 手ぶら版(<武将>_u)を作る ※mk.py の後に必ず
python3 hand.py               # 手の位置(武器を持たせる位置)を再計算 ※最後に必ず
cd .. && python3 build.py     # sprites/atlas_*.webp を gfx/ にコピーして組み立て
node tests/tmeta.js           # 位置データ欠けがないか必ず確認
```
- 元絵の選び方: ファイル名の末尾 `_v3` > `追加v1` > … の順で新しいものを優先(mk.py の `find()`)。
- 大きさの補正は mk.py の `KFIX`、他のコマの絵が混ざった時の消しゴムは `CUTS`、色の補正は `DEMAG`。
- 隣のコマの破片は `descrap()` が自動で消す。
- **注意**: 以前 mk.py が sprmeta.json を丸ごと上書きして、馬・騎馬兵・アイテムが消える事故があった。現在は足し込み式に修正済み。build.py も位置データ欠けがあれば止まる。

## 5. ゲームの仕組み(game_src.html の主な場所)
- 状態管理: `G`(全体)、`TY`(キャラ・敵の能力表)、`WPN`(拾える武器)、`STG`(ステージ)、`DIFF`(難易度 やさしい/ふつう/むずかしい)
- 進行: `stepGame()` が1フレーム処理、`frame()` が描画ループ(低スペック端末は `setLowRes` で軽量化)
- プレイヤー: `updPlayer`、攻撃開始 `startPAtk`、溜め攻撃 `CHG`/`startCharge`、必殺 `startSpecial`、奥義 `startUlt`
- 敵: `updEnemy`、`spawnEn`、ボス技 `bossTech`
- 被弾: `hurt()`、ガード、`knock()`
- 相方: `partnerCtl`、かばう `tryCover`、殿(しんがり)`rearCheck`/`rearStep`
- 描画: `drawSprite`(キャラ絵)、武器を持った時は手ぶら版に切替(`UMAP`、全武将。足りない動きは `UGEN` の代用表で補う)。鎖鎌の長押し回転・貫通投げ・引き寄せは `kusariCtl`
- 画面: タイトル `drawTitle`、キャラ選択 `drawSelect`、チュートリアル `HT_STEPS`、一時停止メニュー `PZM`、ストーリー `SCN`
- 主人公6人は `sc:1.08`(足軽より少し大きく見せるため)
- ジャンプ力: `p.vz=T.jump*1.2`(TY 各武将の `jump` 値 × 1.2)
- 溜め攻撃(長押し→離す)は武器ごとに変わる: `chargeKind()` で判定。刀(景勝・信長・武蔵の持ち武器/長剣/妖刀)=居合 `startIai`/`iaiStep`/`drawIai`、槍=突進(従来の `startCharge`)、薙刀=回転斬り、斧・棍棒=地割れ、鉄砲=溜め撃ち、弓=三本矢、鉄扇=疾風、軍配=号令(`startCk`/`chargeStep`)。鎖鎌だけは `kusariCtl` で別処理。鎖鎌の回転中は各武将の `kspin` 絵、投げは `kthrow` 絵(現在は幸村のみ。他の武将は手ぶら版+手描きの鎌)。元絵は `<武将>_鎖鎌_分銅旋回_4コマ` / `<武将>_鎖鎌_分銅投擲_6コマ`
- 必殺ゲージ: 必殺技・奥義のダメージでは増えない(`hurt()` 内)。被弾でも増える(ダメージ×0.8)
- 注意: ゲーム内時計 `G.t` は `frame()` で進む。テストで `stepGame()` だけ回すときは `G.t++` も自分で進めること

## 6. 残っている作業
1. **手ぶら版の絵**: 幸村以外(景勝・三成・信長・信玄・武蔵)。届いたら mku.py で作成し、`UMAP` に追加すると「武器を拾った時に武器が二重に見える」問題が消える。
   手ぶらシートは旗・装備の有無をコマ間でそろえること(そろっていないと点滅して見える)。
2. 武将の登場ボイス(assets/voice/v3)が届いたら組み込む。
3. オーナー本人が録音した声を入れたいという話あり(ファイル待ち)。
4. スマホ実機で「体が縦に切れる」報告が過去にあった。古い版のキャッシュの可能性が高いが、新しい元絵を入れたら `tests/tyk.js <武将>` でコマ一覧を出して目で確認すること。

## 7. 守ること
- オーナーへの返答・進捗報告は日本語。
- 見た目の判断は自分で全キャラ分確認してから出す。
- プッシュ前に必ず fetch+merge(複数人が同じブランチに push している)。
- プッシュしたら Vercel に production デプロイして、公開URLで動くことまで確認する。

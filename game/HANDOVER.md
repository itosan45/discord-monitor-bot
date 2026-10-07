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
node game/tests/tdecap.js           # 会心で首が飛ぶ(流血オン/オフ)
node game/tests/tkachi.js           # 勝鬨で味方の足軽が集まる(真田だけ赤備え+六文銭の旗)
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
- 新しい元絵は大きさがばらばらに届くことが多い。組み込むたびに、待機の絵と並べて背の高さを確認し、ずれていれば mk.py の `KFIX` で補正すること(例: ボスの歩き8コマv2は1.2〜1.6倍大きく描かれていた)
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
- 溜め攻撃(長押し→離す)は武器ごとに変わる: `chargeKind()` で判定。刀(景勝・信長・武蔵の持ち武器/長剣/妖刀)=居合 `startIai`/`iaiStep`/`drawIai`、槍=突進(従来の `startCharge`)、薙刀=回転斬り、斧・棍棒=地割れ、鉄砲=溜め撃ち、弓=三本矢、鉄扇=疾風、軍配=号令(`startCk`/`chargeStep`)。鎖鎌だけは `kusariCtl` で別処理。鎖鎌の絵(`drawSprite` 冒頭の `kart`): 普通の攻撃=`kslash`(鎌斬撃)、長押し=`kspin`(歩くと `kwalk`、現在は幸村・景勝・武蔵・信長・信玄)、投げ=`kthrow`、引き寄せ=`kpull`、空振りの巻き戻し=`kret`。元絵は `<武将>_鎖鎌_<動作>_<N>コマ`。大きさは mk.py の KFIX で武将ごとに補正済み
- ボスAI(`updEnemy` の `T.ai==='boss'`): 体力は定義値×1.25。プレイヤーの攻撃を読んでガード(`BGUARD`、防いだら反撃)や飛び退き(`BSTEP`)、技のあと連続技(`comboN`、怒り状態で最大2回)、6連続で殴られると振り払い(`BSHAKE`)。最上義光は `ai2:'archer'` で距離を取り、三本矢(`arrows3`)と矢の雨を使う。テストは `tests/tbossai.js`
- 音声(Gemini生成、`assets/voice/gemini/` に元WAVと manifest.csv): 名乗り=キャラ選択で再生(`AU.intro`)、必殺の掛け声=必殺技・奥義の発動時(`AU.spv`)、気合い=攻撃時(`AU.kiai`)、勝ちどき=ステージクリア(`AU.kachi`、import_voice.py で声の高さだけ変えた30人分(元の0.62〜1.45倍に均等に散らす)をほぼ同時(ずれ30ms以内)に重ねた1本を作って再生。再生速度でずらすとやまびこになるので注意)、殿=相方の殿(`AU.shingari`)。やられ声は不採用。差し替えは WAV を置き換えて `python3 game/tools/import_voice.py` → `cd game && python3 build.py`
- 勝鬨の演出(ボス撃破後 `G.state==='bossdown'`): kt=60 で `kgunInit()` が味方の足軽10人(刀・槍の敵足軽の絵を流用)を画面の両端から呼び、主人公の周りに集める(`kgunStep`/`drawKgun`、描画は `renderWorld` の奥行き並べに混ぜている)。「えい!」(kt=180/214)と「おー!」(kt=250)で跳ねて刀を振り上げる(刀足軽は攻撃2コマ目、槍足軽は待機絵を傾ける)。真田幸村の時だけ `redS()` で青い着物を赤に塗り替え(赤備え)、背中に六文銭の旗を手描き。声は30人分の勝ちどき1本だけ(前の掛け声・太鼓を重ねた版はオーナーの判断で不採用)
- 騎乗: 乗り手は立ち絵を腰で切って鞍に乗せる(`drawRiderPlayer`)。脚の長い絵は `MRIDE` で切り位置・高さ・大きさを補正(現在は武蔵のみ)。乗り手のいない馬(走り去る馬・奪える馬)は `mount_blue` の絵を使用。手描きの馬 `drawHorse` は絵の読み込み失敗時の予備のみ
- 会心(クリティカル): `hurt()` 内で判定(通常7%、溜め攻撃・居合30%、ダメージ1.6倍、「会心!」表示)。会心で倒すと `decap()` で首が飛ぶ(流血オフ `G.blood=false` なら笠・兜だけ)。頭の範囲は `headRect()` が絵の上部から自動で探す。ボス・騎馬は対象外
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

## 8. 作りかけの素材(未組み込み)
- 味方足軽の勝鬨ポーズ(拳を突き上げて叫ぶ、2〜4コマ。できれば赤備え版も): 今は敵足軽の刀を振り上げる絵で代用中。届いたら `drawKgun` の `e.up` の絵を差し替える
- 乗り手なしの馬(待機・疾走): 今は主人公用の馬の絵を流用しているため、鞍の上に乗り手の脚当てが少し残る。専用の絵が届いたら差し替える
- 真田十勇士(猿飛佐助・霧隠才蔵・海野六郎・穴山小助・筧十蔵・三好清海入道・三好伊三入道・根津甚八・由利鎌之助): 待機・被弾・一部の攻撃と設定画のみ。動き一式がそろったら組み込む

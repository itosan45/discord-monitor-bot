# 関ヶ原乱舞のClaude Code向け案内

- 作業前に `AGENTS.md` と `game/ASSET_REQUESTS.md` を読み、ブランチ・既存PNG保護・素材検品の約束に従う。
- 背景・設定画・会話胸像が必要なときは `python game/tools/cf_image.py --prompt "..." --out game/experiments/<新しいフォルダ>/<新しい名前>.png --steps 8` でCloudflare Workers AIを使える。
- 自宅PCでは本人が設定したWindowsのユーザー環境変数を道具が読み取る。鍵・全環境変数の値を表示したり、コード・ログ・コミットへ書いたりしない。未設定なら本人に `python game/tools/cf_setup_windows.py` の設定画面へ直接入力してもらう。
- 切り抜き用は `--magenta`、横長背景は `--crop-aspect 16:9`。seedが現行APIで拒否された場合のみ、道具がseedなしで1回再試行する。実効seedは `prompts.jsonl` の `seed` を確認する。
- 同名PNGを上書きしない。無料枠を守るため一度に数枚まで。429では停止し、再試行を繰り返さない。
- 出力には不要な文字や装備の誤りが混ざるため、必ず画像を開いて検品し、現行素材と絵柄を比較する。生成成功だけで正式納品・採用とはしない。
- 同じ人物を連続した形で動かすスプライトには使わず、従来どおり手で清書する。

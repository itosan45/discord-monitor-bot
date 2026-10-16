"""Cloudflare Workers AI(FLUX.1-schnell)で画像を1枚作る道具(2026-10-16 オーナー依頼)。
鍵はコードに書かない。環境変数から読む: CLOUDFLARE_ACCOUNT_ID / CLOUDFLARE_API_TOKEN(Workers AI の権限付き)。
使い方:
  python3 game/tools/cf_image.py --prompt "..." --out game/experiments/cf_gen_20261017/島津義弘_設定画_cf_v1.png [--seed 123] [--steps 8] [--magenta]
- 同じ名前のファイルが既にあれば止まる(上書きしない)。
- 作るたびに、プロンプト・seed・steps・モデル・日時を同じフォルダの prompts.jsonl に1行ずつ書き足す。
- --magenta: 背景を純マゼンタ #FF00FF にそろえる(四隅の色から背景を判定。人物の切り抜きの下ごしらえ)。
- 無料枠は1日1万ニューロン程度。試すのは数枚ずつにする。
向いている: 設定画・背景・会話の胸像。向かない: 同じ人物を何コマも同じ形で描く動きの絵(スプライト)。"""
import argparse, base64, datetime, io, json, os, sys, urllib.error, urllib.request
from pathlib import Path

MODEL = '@cf/black-forest-labs/flux-1-schnell'


def die(msg):
    print('エラー: ' + msg, file=sys.stderr)
    sys.exit(1)


def generate(prompt, steps, seed):
    acc, tok = os.environ.get('CLOUDFLARE_ACCOUNT_ID'), os.environ.get('CLOUDFLARE_API_TOKEN')
    if not acc or not tok:
        die('環境変数 CLOUDFLARE_ACCOUNT_ID / CLOUDFLARE_API_TOKEN がありません。環境の設定に入れてください(値はチャットに貼らない)。')
    body = {'prompt': prompt, 'steps': steps}
    if seed is not None:
        body['seed'] = seed
    req = urllib.request.Request(f'https://api.cloudflare.com/client/v4/accounts/{acc}/ai/run/{MODEL}',
                                 data=json.dumps(body).encode(), method='POST',
                                 headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            res = json.loads(r.read())
    except urllib.error.HTTPError as e:
        detail = e.read().decode('utf-8', 'replace')[:300]
        if e.code == 429:
            die('無料枠の上限に達しました(429)。明日またはプランを確認してください。' + detail)
        if e.code in (401, 403):
            die(f'認証エラー({e.code})。トークンに Workers AI の権限があるか、アカウントIDが正しいか確認してください。')
        die(f'HTTP {e.code}: {detail}')
    except urllib.error.URLError as e:
        die(f'接続できません: {e.reason}(api.cloudflare.com へのネットワークの許可を確認)')
    img = (res.get('result') or {}).get('image')
    if not img:
        die('応答に画像がありません: ' + json.dumps(res, ensure_ascii=False)[:300])
    return base64.b64decode(img)


def to_magenta(data):
    import numpy as np
    from PIL import Image
    im = Image.open(io.BytesIO(data)).convert('RGB')
    a = np.asarray(im).astype(int)
    h, w, _ = a.shape
    corners = np.array([a[:8, :8].reshape(-1, 3).mean(0), a[:8, -8:].reshape(-1, 3).mean(0),
                        a[-8:, :8].reshape(-1, 3).mean(0), a[-8:, -8:].reshape(-1, 3).mean(0)])
    bg = np.median(corners, 0)
    d = np.sqrt(((a - bg) ** 2).sum(2))
    mask = d < 38
    try:
        from scipy import ndimage
        mask = ndimage.binary_dilation(mask, iterations=1)
    except ImportError:
        pass
    a[mask] = (255, 0, 255)
    return Image.fromarray(a.astype('uint8'), 'RGB')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--prompt', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--steps', type=int, default=8)
    ap.add_argument('--seed', type=int)
    ap.add_argument('--magenta', action='store_true')
    o = ap.parse_args()
    out = Path(o.out)
    if out.exists():
        die(f'{out} は既にあります(上書きしない)。新しい名前(_v2 など)にしてください。')
    out.parent.mkdir(parents=True, exist_ok=True)
    data = generate(o.prompt, max(1, min(8, o.steps)), o.seed)
    from PIL import Image
    im = to_magenta(data) if o.magenta else Image.open(io.BytesIO(data)).convert('RGB')
    im.save(out)
    with open(out.parent / 'prompts.jsonl', 'a', encoding='utf-8') as f:
        f.write(json.dumps({'file': out.name, 'prompt': o.prompt, 'seed': o.seed, 'steps': o.steps, 'model': MODEL,
                            'magenta': o.magenta, 'at': datetime.datetime.now().isoformat(timespec='seconds')}, ensure_ascii=False) + '\n')
    print(f'作成: {out} {im.size}')


if __name__ == '__main__':
    main()

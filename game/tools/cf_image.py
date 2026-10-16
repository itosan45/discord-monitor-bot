#!/usr/bin/env python3
"""Generate one image with Cloudflare Workers AI FLUX.1-schnell.

Requires Python 3 and Pillow. Credentials are read from CLOUDFLARE_ACCOUNT_ID
and CLOUDFLARE_API_TOKEN; never put their values in source or command history.
"""

import argparse
import base64
import datetime
import io
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

MODEL = "@cf/black-forest-labs/flux-1-schnell"
API_ROOT = "https://api.cloudflare.com/client/v4/accounts"


def fail(message):
    print(f"エラー: {message}", file=sys.stderr)
    raise SystemExit(1)


def generate(prompt, steps, seed):
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not account_id or not token:
        fail("環境変数 CLOUDFLARE_ACCOUNT_ID と CLOUDFLARE_API_TOKEN が必要です(値は表示しません)。")

    body = {"prompt": prompt, "steps": steps}
    if seed is not None:
        body["seed"] = seed
    request = urllib.request.Request(
        f"{API_ROOT}/{account_id}/ai/run/{MODEL}",
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        if error.code == 429:
            fail("HTTP 429: 利用上限またはレート制限に達しました。時間をおいて利用状況を確認してください。")
        if error.code in (401, 403):
            fail(f"HTTP {error.code}: 認証に失敗しました。アカウントIDとWorkers AI権限を確認してください。")
        fail(f"Cloudflare API が HTTP {error.code} を返しました。")
    except urllib.error.URLError as error:
        fail(f"Cloudflare API に接続できません: {error.reason}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        fail("Cloudflare API の応答をJSONとして読み取れませんでした。")

    encoded = (result.get("result") or {}).get("image")
    if not encoded:
        fail("Cloudflare API の応答に result.image がありません。")
    try:
        return base64.b64decode(encoded, validate=True)
    except (ValueError, TypeError):
        fail("応答画像のBase64データが壊れています。")


def _near_corner(image, color, tolerance):
    """Return a 1-bit Pillow mask of pixels close to one corner color."""
    source = image.load()
    width, height = image.size
    mask = Image.new("1", image.size, 0)
    pixels = mask.load()
    cr, cg, cb = color
    for y in range(height):
        for x in range(width):
            r, g, b = source[x, y]
            if max(abs(r - cr), abs(g - cg), abs(b - cb)) <= tolerance:
                pixels[x, y] = 1
    return mask


def magenta_background(image):
    """Flood-fill corner-colored background, then contract the figure by 1px."""
    image = image.convert("RGB")
    width, height = image.size
    pixels = image.load()
    corners = ((0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1))
    background = Image.new("1", image.size, 0)
    for point in corners:
        color = pixels[point]
        # Flood-fill a fresh near-color mask. The changed component becomes 0.
        candidates = _near_corner(image, color, tolerance=24)
        component = candidates.copy()
        ImageDraw.floodfill(component, point, 0, thresh=0)
        # Difference keeps only candidate pixels that flood-fill reached.
        changed = ImageChops.difference(candidates.convert("L"), component.convert("L"))
        background = ImageChops.lighter(background.convert("L"), changed).convert("1")

    # Contract the foreground by one pixel to remove the generated edge fringe.
    foreground = Image.eval(background.convert("L"), lambda value: 255 - value)
    foreground = foreground.filter(ImageFilter.MinFilter(3))
    output = Image.new("RGB", image.size, (255, 0, 255))
    output.paste(image, mask=foreground)
    return output


def main():
    parser = argparse.ArgumentParser(description="Cloudflare Workers AIで画像を1枚生成します")
    parser.add_argument("--prompt", required=True, help="画像生成プロンプト")
    parser.add_argument("--out", required=True, help="新規PNGの保存先")
    parser.add_argument("--steps", type=int, default=8, choices=range(4, 9), help="生成step数(4〜8)")
    parser.add_argument("--seed", type=int, help="任意のseed")
    parser.add_argument("--magenta", action="store_true", help="四隅を基準に背景を#FF00FFへ置換し、縁を1px締める")
    args = parser.parse_args()

    output = Path(args.out)
    if output.exists():
        fail(f"{output} は既にあります。別のファイル名を指定してください(上書きしません)。")
    if output.suffix.lower() != ".png":
        fail("出力先はPNG(.png)にしてください。")

    image_data = generate(args.prompt, args.steps, args.seed)
    try:
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
    except Exception as error:
        fail(f"応答データを画像として開けません: {error}")
    if args.magenta:
        image = magenta_background(image)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        # Exclusive create prevents overwriting a file created during the request.
        with output.open("xb") as file:
            file.write(buffer.getvalue())
    except FileExistsError:
        fail(f"{output} は既にあります。上書きしません。")

    record = {
        "file": output.name,
        "prompt": args.prompt,
        "seed": args.seed,
        "steps": args.steps,
        "model": MODEL,
        "magenta": args.magenta,
        "at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    }
    try:
        with (output.parent / "prompts.jsonl").open("a", encoding="utf-8") as log:
            log.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as error:
        fail(f"画像は保存しましたがprompts.jsonlへ記録できません: {error}")
    print(f"作成しました: {output} ({image.width}x{image.height})")


if __name__ == "__main__":
    main()

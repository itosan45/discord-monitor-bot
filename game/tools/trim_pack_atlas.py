"""大きな一体絵アトラス(4096px超など)の余白を詰めて詰め直し、新キーで保存する。
元のアトラスと元のsprmetaは変更しない。描画結果は元と1ピクセルも変わらない
(各コマを不透明部分だけに切り詰め、描画位置 dx,dy をその分ずらす)。

使い方: python3 game/tools/trim_pack_atlas.py mountfull3_musashi mountfull4_musashi
  → game/sprites/atlas_mountfull4_musashi.webp と sprmeta.json の新キーを作る
"""
import json, sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SPR = ROOT / "game" / "sprites"
MAX_W, GUTTER = 2048, 2

def main(src_key, dst_key):
    meta_path = SPR / "sprmeta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    src_img = SPR / f"atlas_{src_key}.webp"
    if not src_img.exists():
        src_img = ROOT / "gfx" / f"atlas_{src_key}.webp"
    atlas = Image.open(src_img).convert("RGBA")
    items = []  # (anim, index, crop, q)
    for anim, frames in meta[src_key].items():
        for i, q in enumerate(frames):
            sx, sy, sw, sh = q[:4]
            cell = atlas.crop((sx, sy, sx + sw, sy + sh))
            bbox = cell.getchannel("A").getbbox() or (0, 0, 1, 1)
            items.append((anim, i, cell.crop(bbox), bbox, q))
    # 棚詰め(高い順)
    order = sorted(range(len(items)), key=lambda n: -items[n][2].height)
    x = y = shelf = 0
    pos = {}
    for n in order:
        w, h = items[n][2].size
        if x + w > MAX_W:
            x, y, shelf = 0, y + shelf + GUTTER, 0
        pos[n] = (x, y)
        x += w + GUTTER
        shelf = max(shelf, h)
    H = y + shelf
    out = Image.new("RGBA", (MAX_W, H), (0, 0, 0, 0))
    new_meta = {}
    for n, (anim, i, crop, bbox, q) in enumerate(items):
        px, py = pos[n]
        out.alpha_composite(crop, (px, py))
        sc = q[6] if len(q) > 6 else 1
        nq = [px, py, crop.width, crop.height, q[4] + bbox[0] * sc, q[5] + bbox[1] * sc, q[6] if len(q) > 6 else 1]
        new_meta.setdefault(anim, []).append(nq)
    out.save(SPR / f"atlas_{dst_key}.webp", "WEBP", lossless=True, method=6)
    meta[dst_key] = new_meta
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(dst_key, out.size, "decoded MB", round(out.width * out.height * 4 / 1e6, 1))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

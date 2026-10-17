"""Pack the captured mounted hero attack strips into runtime atlases and sprite metadata."""
import json, os
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ASSETS = Path(os.environ["OUT"])
SPRITES = ROOT / "game" / "sprites"
HEROES = {
    "yuki": "真田幸村", "kage": "上杉景勝", "mitsu": "石田三成",
    "nobu": "織田信長", "shin": "武田信玄", "musashi": "宮本武蔵",
}
PROFILES = {"default":"主武器","odachi":"長剣","naginata":"薙刀","teppo":"火縄銃","yoto":"妖刀","ono":"斧","konbou":"棍棒","takeyari":"竹槍","kusari":"鎖鎌","yumi":"弓矢"}

W, H, FRAMES = 576, 416, 5

meta_path = SPRITES / "sprmeta.json"
meta = json.loads(meta_path.read_text(encoding="utf-8"))
for hero, jp in HEROES.items():
    atlas = Image.new("RGBA", (W * FRAMES, H * len(PROFILES)), (0, 0, 0, 0))
    animations = {}
    for row, (profile, label) in enumerate(PROFILES.items()):
        filename = f"馬上攻撃_{jp}_{label}_5コマ_v2.png"
        strip = Image.open(ASSETS / filename).convert("RGBA")
        if strip.size != (W * FRAMES, H):
            raise SystemExit(f"bad dimensions: {filename}: {strip.size}")
        foot_lines, signatures = [], set()
        for i in range(FRAMES):
            cell = strip.crop((i * W, 0, (i + 1) * W, H))
            alpha = cell.getchannel("A")
            bbox = alpha.getbbox()
            if not bbox or bbox[0] < 16 or bbox[1] < 16 or bbox[2] > W - 16 or bbox[3] > H - 16:
                raise SystemExit(f"frame touches 16px safe border: {filename} frame {i} bbox={bbox}")
            # Horse hooves stay near the body center; a lowered yari tip may extend lower.
            foot_bbox = cell.crop((130, 0, 280, H)).getchannel("A").getbbox()
            foot_lines.append(foot_bbox[3] if foot_bbox else -1)
            signatures.add(alpha.tobytes())
        if max(foot_lines) - min(foot_lines) > 4:
            raise SystemExit(f"mounted feet drift across frames: {filename} y={foot_lines}")
        if len(signatures) < 3:
            raise SystemExit(f"too few distinct mounted frames: {filename}")
        atlas.alpha_composite(strip, (0, row * H))
        animations[profile] = [[i * W, row * H, W, H, -W // 2, -384, 1] for i in range(FRAMES)]
    key = f"mountatk2_{hero}"
    meta[key] = animations
    atlas.save(SPRITES / f"atlas_{key}.webp", "WEBP", lossless=True, method=6)
    print(key, atlas.size)
meta_path.write_text(json.dumps(meta, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

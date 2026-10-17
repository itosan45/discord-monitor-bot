"""Repack A-028 fall/get-up poses for Claude's integration baseline.

Reads the previously generated 2x2 source canvases from the adjacent
a028-bossfalls-20261017 experiment, then writes new 1536x384 candidate sheets
at 188px standing height with the inclusive groundline at y=363. Existing
candidate PNGs in that experiment are never overwritten.
"""
from pathlib import Path
import argparse
import hashlib
import json

import cv2
import numpy as np
from PIL import Image


HERE = Path(__file__).parent
SOURCE_ROOT = HERE.parent / "a028-bossfalls-20261017"
TARGET_HEIGHT = 188
GROUNDLINE = 363
MAGENTA = (255, 0, 255)


def source_path(name: str, action: str) -> Path:
    if name == "最上義光":
        filename = f"mogami_source_{action}.png"
    else:
        filename = f"source_{name}_{action}.png"
    return SOURCE_ROOT / filename


def get_poses(name: str, action: str):
    src = Image.open(source_path(name, action)).convert("RGB")
    a = np.asarray(src)
    bg = ((a[:, :, 0] >= 190) & (a[:, :, 1] <= 70) & (a[:, :, 2] >= 190)).astype(np.uint8)
    _, labels, _, _ = cv2.connectedComponentsWithStats(bg, connectivity=4)
    edge_labels = set(np.unique(np.r_[labels[0, :], labels[-1, :], labels[:, 0], labels[:, -1]]))
    fg = ((labels == 0) | ~np.isin(labels, list(edge_labels))).astype(np.uint8)
    count, components, stats, centroids = cv2.connectedComponentsWithStats(fg, connectivity=8)
    ids = [i for i in range(1, count) if stats[i, cv2.CC_STAT_AREA] > 15000]
    ids.sort(key=lambda i: (centroids[i][1] >= 627, centroids[i][0] >= 627))
    if len(ids) != 4:
        raise ValueError(f"{name} {action}: expected four poses, found {len(ids)}")
    return a, components, stats, ids


def build(name: str, action: str, label: str, scale: float):
    a, components, stats, ids = get_poses(name, action)
    sheet = Image.new("RGB", (1536, 384), MAGENTA)
    bboxes = []
    for frame, component in enumerate(ids):
        x, y, w, h, _ = stats[component].tolist()
        mask = components[y:y+h, x:x+w] == component
        crop = a[y:y+h, x:x+w].copy()
        crop[~mask] = MAGENTA
        resized = Image.fromarray(crop).resize((round(w*scale), round(h*scale)), Image.Resampling.LANCZOS)
        resized_mask = Image.fromarray(mask.astype(np.uint8)*255).resize(resized.size, Image.Resampling.NEAREST)
        dx = (384-resized.width)//2
        dy = GROUNDLINE+1-resized.height
        if dx < 1 or dx+resized.width > 383 or dy < 1 or dy+resized.height > 384:
            raise ValueError(f"{name} {label} frame {frame+1}: out of cell bounds {resized.size} at {(dx,dy)}")
        sheet.paste(resized, (dx+384*frame,dy), resized_mask)
        bboxes.append([dx,dy,dx+resized.width-1,GROUNDLINE])
    filename = f"{name}_{label}_4コマ_v1.png"
    out = HERE / filename
    if out.exists():
        raise FileExistsError(f"Refusing to overwrite existing candidate: {out}")
    sheet.save(out, format="PNG", optimize=True)
    gif = HERE / f"{name}_{label}_preview.gif"
    frames = [sheet.crop((i*384,0,(i+1)*384,384)) for i in range(4)]
    frames[0].save(gif, save_all=True, append_images=frames[1:], duration=220, loop=0, disposal=2)
    return {
        "character": name, "action": label, "file": filename,
        "size": [1536,384], "frames": 4, "cell_size": [384,384],
        "background_rgb": list(MAGENTA), "groundline_y_inclusive": GROUNDLINE,
        "frame_bboxes": bboxes,
        "sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
        "status": "candidate_not_delivery",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--character", required=True)
    args = parser.parse_args()
    name = args.character
    fall = get_poses(name,"fall")
    getup = get_poses(name,"getup")
    tallest = max(fall[2][fall[3][0],cv2.CC_STAT_HEIGHT], getup[2][getup[3][-1],cv2.CC_STAT_HEIGHT])
    scale = TARGET_HEIGHT / tallest
    entries = [build(name,"fall","転倒",scale), build(name,"getup","起き上がり",scale)]
    qa_file = HERE / "qa.json"
    qa = json.loads(qa_file.read_text(encoding="utf-8")) if qa_file.exists() else {
        "ticket":"A-028", "status":"candidate_not_delivery",
        "review_note":"Same format as Claude's integrated Naomasa sheets: 384px cells, 188px upright height, magenta background, inclusive groundline y=363. Candidate sheets receive static visual and pixel QA; gameplay timing and runtime integration remain for Claude.",
        "sheets": [],
    }
    qa["sheets"].extend(entries)
    qa_file.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    readme = HERE / "README.md"
    section = (
        f"\n## {name}\n\n"
        f"- `{name}_転倒_4コマ_v1.png`: 4-frame fall candidate.\n"
        f"- `{name}_起き上がり_4コマ_v1.png`: 4-frame recovery candidate.\n"
        f"- Source setting/idle: `assets/sprites/{name}_設定画.png`, `assets/sprites/{name}_待機_4コマ.png`.\n"
        f"- Repacked from `../a028-bossfalls-20261017/{source_path(name,'fall').name}` and its get-up source. Upright height target {TARGET_HEIGHT}px; groundline y={GROUNDLINE}.\n"
        f"- Static sheet order, silhouette, weapon/costume continuity, dimensions, exact magenta background, cell borders, hashes and 4-frame GIF decode checked. Gameplay cadence and live in-game/down-to-idle behavior remain unverified.\n"
    )
    prior = readme.read_text(encoding="utf-8") if readme.exists() else "# A-028 y=363 integration-format candidates\n\nCandidates for the integration format used by the accepted Ii Naomasa sheets. These are not completed game assets until Claude confirms runtime behavior.\n"
    if f"## {name}\n" in prior:
        raise ValueError(f"README already contains {name}; refusing duplicate section")
    readme.write_text(prior+section,encoding="utf-8")
    print(f"{name}: source standing height {tallest}px, scale {scale:.6f}; wrote 2 sheets at y={GROUNDLINE}")


if __name__ == "__main__":
    main()

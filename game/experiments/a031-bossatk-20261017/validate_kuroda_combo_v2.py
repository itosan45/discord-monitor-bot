from pathlib import Path
import hashlib
import json

import numpy as np
from PIL import Image

ROOT = Path(__file__).parent
SHEETS = [
    ROOT / "黒田長政_連撃1_qa-v5.json",
    ROOT / "黒田長政_連撃2_qa-v4.json",
    ROOT / "黒田長政_連撃3_qa-v4.json",
]
MAGENTA = np.array([255, 0, 255], dtype=np.uint8)
summary = []

for qa_path in SHEETS:
    qa = json.loads(qa_path.read_text(encoding="utf-8"))
    count = qa["frames"]
    sprite = ROOT / qa["output"]
    image = Image.open(sprite).convert("RGB")
    assert image.size == (count * 512, 384), (sprite.name, image.size)
    pixels = np.asarray(image)
    frame_hashes = []
    adjacent_diffs = []
    for i in range(count):
        frame = pixels[:, i * 512:(i + 1) * 512]
        assert np.all(frame[0] == MAGENTA) and np.all(frame[-1] == MAGENTA)
        assert np.all(frame[:, 0] == MAGENTA) and np.all(frame[:, -1] == MAGENTA)
        foreground = np.any(frame != MAGENTA, axis=2)
        expected_bottom = qa.get("vertical_anchor_y_by_frame", [qa.get("ground_anchor_y", 363) - 1 - lift for lift in qa.get("vertical_lift_px_by_frame", [0] * count)])[i]
        assert foreground.any() and np.where(foreground)[0].max() == expected_bottom, (sprite.name, i + 1, "vertical anchor", np.where(foreground)[0].max(), expected_bottom)
        frame_hashes.append(hashlib.sha256(frame.tobytes()).hexdigest())
        if i:
            adjacent_diffs.append(int(np.abs(frame.astype(np.int16) - pixels[:, (i - 1) * 512:i * 512].astype(np.int16)).sum()))
    assert len(set(frame_hashes)) == count, (sprite.name, "duplicate frame")
    assert qa["frame_sha256"] == frame_hashes, (sprite.name, "frame hash mismatch")
    digest = hashlib.sha256(sprite.read_bytes()).hexdigest()
    assert digest == qa["sha256"], (sprite.name, "sheet hash mismatch")
    gif = Image.open(ROOT / qa["preview_gif"])
    assert gif.n_frames == count, (sprite.name, "GIF frame count")
    assert min(adjacent_diffs) > 1000, (sprite.name, "near-identical adjacent frames", min(adjacent_diffs))
    summary.append({"file": sprite.name, "size": list(image.size), "frames": count, "unique": count, "gif_frames": gif.n_frames, "edge_contact": 0, "ground_y": qa.get("ground_anchor_y"), "sha256": digest, "min_adjacent_pixel_difference": min(adjacent_diffs)})

assert summary[0]["frames"] == summary[1]["frames"] == 12 and summary[2]["frames"] == 16
print(json.dumps(summary, ensure_ascii=False, indent=2))

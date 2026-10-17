from pathlib import Path
import hashlib
import json

import numpy as np
from PIL import Image

ROOT = Path(__file__).parent
QA = json.loads((ROOT / "黒田長政_防御_QA-v1.json").read_text(encoding="utf-8"))
EXPECTED = {"構え": 6, "受け止め": 4, "受け流し": 8, "崩れ": 6}
MAGENTA = np.array([255, 0, 255], dtype=np.uint8)
assert QA["character"] == "黒田長政" and set(QA["actions"]) == set(EXPECTED)
report = {}

for action, count in EXPECTED.items():
    item = QA["actions"][action]
    path = ROOT / item["sprite"]
    image = Image.open(path).convert("RGB")
    assert image.size == (count * 512, 384), (action, image.size)
    pixels = np.asarray(image)
    frames = [pixels[:, i * 512:(i + 1) * 512] for i in range(count)]
    unique = len({frame.tobytes() for frame in frames})
    assert unique == count, (action, unique)
    for i, frame in enumerate(frames):
        edges = np.concatenate((frame[0], frame[-1], frame[:, 0], frame[:, -1]))
        assert np.all(np.all(edges == MAGENTA, axis=1)), (action, i + 1, "edge")
        fg = np.any(frame != MAGENTA, axis=2)
        assert np.where(fg)[0].max() == 362, (action, i + 1, "ground")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == item["sha256"], (action, "sha256")
    gif = Image.open(ROOT / item["preview_gif"])
    assert gif.n_frames == count, (action, gif.n_frames)
    report[action] = {
        "frames": count,
        "size": list(image.size),
        "unique": unique,
        "gif_frames": gif.n_frames,
        "sha256": digest,
        "edge_contact": 0,
        "ground_y": 362,
    }

print(json.dumps(report, ensure_ascii=False, indent=2))

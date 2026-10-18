from pathlib import Path
import hashlib, json
import numpy as np
from PIL import Image

ROOT = Path(__file__).parent
QA = json.loads((ROOT / "福島正則_防御_QA-v5.json").read_text(encoding="utf-8"))
EXPECTED = {"構え": 6, "受け止め": 4, "受け流し": 8, "崩れ": 6}
MAGENTA = np.array([255, 0, 255], dtype=np.uint8)
report = {}
assert QA["character"] == "福島正則" and set(QA["actions"]) == set(EXPECTED)

for action, count in EXPECTED.items():
    item = QA["actions"][action]
    path = ROOT / item["sprite"]
    image = Image.open(path).convert("RGB")
    assert image.size == (count * 512, 384), (action, image.size)
    pixels = np.asarray(image)
    frames = [pixels[:, i * 512:(i + 1) * 512] for i in range(count)]
    assert len({frame.tobytes() for frame in frames}) == count, action
    for i, frame in enumerate(frames):
        assert all(tuple(frame[y, x]) == (255, 0, 255) for x, y in ((0, 0), (511, 0), (0, 383), (511, 383))), (action, i + 1, "corner")
        edges = np.concatenate((frame[0], frame[-1], frame[:, 0], frame[:, -1]))
        assert np.all(np.all(edges == MAGENTA, axis=1)), (action, i + 1, "edge")
        fg = np.any(frame != MAGENTA, axis=2)
        assert np.where(fg)[0].max() == 362, (action, i + 1, "ground")
    assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"], action
    gif = Image.open(ROOT / item["preview_gif"])
    assert gif.n_frames == count, (action, gif.n_frames)
    report[action] = {"frames": count, "size": list(image.size), "unique": len({f.tobytes() for f in frames}), "gif_frames": gif.n_frames, "sha256": item["sha256"], "edge_contact": 0, "ground_y": 362}

print(json.dumps(report, ensure_ascii=False, indent=2))

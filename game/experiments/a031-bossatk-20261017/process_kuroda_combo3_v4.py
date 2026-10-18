from pathlib import Path
import hashlib
import json

import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).parent
SOURCE = ROOT / "黒田長政_連撃3_source-v1.png"
OUTPUT = ROOT / "黒田長政_連撃3(締め)_16コマ_v4.png"
GIF = ROOT / "黒田長政_連撃3_preview-v4.gif"
GRID = ROOT / "黒田長政_連撃3_review-grid-v4.png"
QA_PATH = ROOT / "黒田長政_連撃3_qa-v4.json"
assert all(not p.exists() for p in (OUTPUT, GIF, GRID, QA_PATH)), "Refusing to overwrite"

src = np.asarray(Image.open(SOURCE).convert("RGB"))
h, w = src.shape[:2]
cols, rows = 4, 4
cells, boxes, masks, edge_contacts = [], [], [], []
for row in range(rows):
    for col in range(cols):
        x0, x1 = round(col * w / cols), round((col + 1) * w / cols)
        y0, y1 = round(row * h / rows), round((row + 1) * h / rows)
        cell = src[y0:y1, x0:x1].copy()
        r, g, b = [cell[:, :, i] for i in range(3)]
        candidate = ((r > 190) & (b > 190) & (g < 100) & (r.astype(int) - g > 100) & (b.astype(int) - g > 100)).astype(np.uint8)
        _, labels, _, _ = cv2.connectedComponentsWithStats(candidate, connectivity=8)
        border_labels = set(np.unique(np.concatenate((labels[0], labels[-1], labels[:, 0], labels[:, -1]))))
        bg = np.isin(labels, list(border_labels)) & (candidate > 0)
        ring = cv2.dilate(bg.astype(np.uint8), np.ones((3, 3), np.uint8), iterations=1).astype(bool) & ~bg
        fringe = ring & (r > 125) & (b > 125) & (g < 105) & (r.astype(int) - g > 55) & (b.astype(int) - g > 55)
        fg = ~(bg | fringe)
        ys, xs = np.where(fg)
        assert len(xs) > 10000, (row, col, len(xs))
        box = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
        contacts = {"top": int(fg[0].sum()), "bottom": int(fg[-1].sum()), "left": int(fg[:, 0].sum()), "right": int(fg[:, -1].sum())}
        cells.append(cell)
        boxes.append(box)
        masks.append(fg.astype(np.uint8) * 255)
        edge_contacts.append(contacts)

lift = [0, 0, 0, 0, 18, 36, 52, 62, 48, 24, 0, 12, 0, 0, 0, 0]
heights = [b[3] - b[1] for i, b in enumerate(boxes) if lift[i] == 0]
scale = 188 / float(np.median(heights))
frames = []
removed_components = []
for frame_index, (cell, box, mask) in enumerate(zip(cells, boxes, masks)):
    x0, y0, x1, y1 = box
    sprite = Image.fromarray(cell[y0:y1, x0:x1])
    alpha = Image.fromarray(mask[y0:y1, x0:x1])
    size = (max(1, round(sprite.width * scale)), max(1, round(sprite.height * scale)))
    sprite = sprite.resize(size, Image.Resampling.LANCZOS)
    alpha = alpha.resize(size, Image.Resampling.LANCZOS)
    frame = Image.new("RGB", (512, 384), (255, 0, 255))
    bottom = 362 - lift[frame_index]
    frame.paste(sprite, (256 - sprite.width // 2, bottom + 1 - sprite.height), alpha)
    pixels = np.asarray(frame).copy()
    fg = np.any(pixels != (255, 0, 255), axis=2).astype(np.uint8)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(fg, connectivity=8)
    removed = []
    for label in range(1, count):
        area = int(stats[label, cv2.CC_STAT_AREA])
        if area < 500:
            x, y, cw, ch = [int(v) for v in stats[label, :4]]
            pixels[labels == label] = (255, 0, 255)
            removed.append({"area": area, "bbox": [x, y, x + cw, y + ch]})
    removed_components.append(removed)
    cleaned = Image.fromarray(pixels)
    fg = np.any(pixels != (255, 0, 255), axis=2)
    current_bottom = int(np.where(fg)[0].max())
    target_bottom = 362 - lift[frame_index]
    delta = target_bottom - current_bottom
    translated = Image.new("RGB", (512, 384), (255, 0, 255))
    if delta >= 0:
        translated.paste(cleaned.crop((0, 0, 512, 384 - delta)), (0, delta))
    else:
        translated.paste(cleaned.crop((0, -delta, 512, 384)), (0, 0))
    frames.append(translated)

sheet = Image.new("RGB", (512 * 16, 384), (255, 0, 255))
for i, frame in enumerate(frames):
    sheet.paste(frame, (512 * i, 0))
sheet.save(OUTPUT, optimize=True)

contact = Image.new("RGB", (2048, 1536), (255, 0, 255))
for i, frame in enumerate(frames):
    thumb = frame.resize((256, 192), Image.Resampling.LANCZOS)
    x, y = (i % 4) * 512 + 128, (i // 4) * 384 + 64
    contact.paste(thumb, (x, y))
    ImageDraw.Draw(contact).text((x + 4, y + 2), str(i + 1), fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
contact.save(GRID, optimize=True)
frames[0].save(GIF, save_all=True, append_images=frames[1:], duration=100, loop=0, optimize=True)

qa = {
    "character": "黒田長政", "action": "連撃3(締め)", "frames": 16,
    "source": SOURCE.name, "source_size": [w, h], "source_grid": "4x4 equal cells",
    "output": OUTPUT.name, "output_size": list(sheet.size),
    "sha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
    "preview_gif": GIF.name, "review_grid": GRID.name,
    "frame_sha256": [hashlib.sha256(f.tobytes()).hexdigest() for f in frames],
    "adjacent_pixel_difference_sum": [float(np.abs(np.asarray(frames[i], dtype=np.int16) - np.asarray(frames[i+1], dtype=np.int16)).sum()) for i in range(15)],
    "source_edge_contact_pixels": edge_contacts,
    "removed_detached_components_lt_500px": removed_components,
    "ground_anchor_y": 363, "vertical_lift_px_by_frame": lift, "estimated_hit_frames": [11],
    "forward_step_frames": [4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
    "sequence": ["high crossed guard carry-over", "load hips", "open blades", "step and turn", "small forward hop", "airborne draw-back", "turn in air", "begin cross sweep", "accelerate descending turn", "cross-sword strike", "impact peak", "follow-through", "land in lunge", "split blades and settle cape", "recover", "low ready guard"],
    "notes": "AI-generated pose sheet cropped, background-keyed, uniformly scaled and composited; detached output components below 500px removed. Frames 5-10 rise and descend by 18/36/52/62/48/24px; frame 11 lands at y=363 for the impact. Frame 12 settles 12px above ground, then frames 13-16 are grounded. Not hand-drawn. Hit frame is a visual estimate, not a game hitbox. Frame 1 is intended to follow combo 2's high crossed guard.",
}
QA_PATH.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"output": OUTPUT.name, "size": list(sheet.size), "frames": len(frames), "unique": len(set(qa["frame_sha256"])), "source_edge_contact_pixels": edge_contacts, "sha256": qa["sha256"]}, ensure_ascii=False, indent=2))

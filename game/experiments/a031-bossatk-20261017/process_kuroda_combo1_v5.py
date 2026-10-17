from pathlib import Path
import hashlib
import json

import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).parent
SOURCE = ROOT / "黒田長政_連撃1_source-v1.png"
OUTPUT = ROOT / "黒田長政_連撃1_12コマ_v5.png"
GIF = ROOT / "黒田長政_連撃1_preview-v5.gif"
GRID = ROOT / "黒田長政_連撃1_review-grid-v5.png"
QA_PATH = ROOT / "黒田長政_連撃1_qa-v5.json"
assert not OUTPUT.exists() and not GIF.exists() and not GRID.exists() and not QA_PATH.exists(), "Refusing to overwrite"

src = np.asarray(Image.open(SOURCE).convert("RGB"))
assert src.shape == (1086, 1448, 3), src.shape
frames = []
boxes = []
masks = []
# Image is an exact 4x3 grid of 362px square source cells.
for row in range(3):
    for col in range(4):
        cell = src[row * 362:(row + 1) * 362, col * 362:(col + 1) * 362].copy()
        r, g, b = [cell[:, :, i] for i in range(3)]
        bg_candidates = ((r > 190) & (b > 190) & (g < 100) & (r.astype(int) - g > 100) & (b.astype(int) - g > 100)).astype(np.uint8)
        n, labels, stats, _ = cv2.connectedComponentsWithStats(bg_candidates, connectivity=8)
        border_labels = set(np.unique(np.concatenate((labels[0], labels[-1], labels[:, 0], labels[:, -1]))))
        bg = np.isin(labels, list(border_labels)) & (bg_candidates > 0)
        assert bg.sum() > 35000, (row, col, int(bg.sum()))
        # Remove only the one-pixel magenta antialias fringe adjoining the exterior.
        ring = cv2.dilate(bg.astype(np.uint8), np.ones((3, 3), np.uint8), iterations=1).astype(bool) & ~bg
        fringe = ring & (r > 125) & (b > 125) & (g < 105) & (r.astype(int) - g > 55) & (b.astype(int) - g > 55)
        foreground = ~(bg | fringe)
        ys, xs = np.where(foreground)
        assert len(xs) > 10000, (row, col, len(xs))
        box = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
        boxes.append(box)
        frames.append(cell)
        masks.append(foreground.astype(np.uint8) * 255)

heights = [box[3] - box[1] for i, box in enumerate(boxes) if i != 6]
scale = 188 / float(np.median(heights))
bottoms = [362, 362, 362, 362, 362, 362, 330, 362, 362, 362, 362, 362]
final_frames = []
for cell, box, mask in zip(frames, boxes, masks):
    x0, y0, x1, y1 = box
    crop = Image.fromarray(cell[y0:y1, x0:x1], "RGB")
    alpha = Image.fromarray(mask[y0:y1, x0:x1], "L")
    w, h = crop.size
    size = (max(1, round(w * scale)), max(1, round(h * scale)))
    crop = crop.resize(size, Image.Resampling.LANCZOS)
    alpha = alpha.resize(size, Image.Resampling.LANCZOS)
    sheet_cell = Image.new("RGB", (512, 384), (255, 0, 255))
    sheet_cell.paste(crop, (256 - crop.width // 2, 363 - crop.height), alpha)
    final_frames.append(sheet_cell)

# Keep the connected character silhouette and remove only tiny detached AI artifacts.
removed_components = []
cleaned_frames = []
for i, frame in enumerate(final_frames):
    pixels = np.asarray(frame).copy()
    foreground = np.any(pixels != (255, 0, 255), axis=2).astype(np.uint8)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(foreground, connectivity=8)
    removed = []
    for label in range(1, count):
        area = int(stats[label, cv2.CC_STAT_AREA])
        if area < 500:
            x, y, w, h = [int(v) for v in stats[label, :4]]
            pixels[labels == label] = (255, 0, 255)
            removed.append({"area": area, "bbox": [x, y, x + w, y + h]})
    removed_components.append(removed)
    cleaned = Image.fromarray(pixels)
    fg = np.any(pixels != (255, 0, 255), axis=2)
    current_bottom = int(np.where(fg)[0].max())
    target_bottom = bottoms[i]
    delta = target_bottom - current_bottom
    translated = Image.new("RGB", (512, 384), (255, 0, 255))
    if delta >= 0:
        translated.paste(cleaned.crop((0, 0, 512, 384 - delta)), (0, delta))
    else:
        translated.paste(cleaned.crop((0, -delta, 512, 384)), (0, 0))
    cleaned_frames.append(translated)
final_frames = cleaned_frames

sheet = Image.new("RGB", (512 * 12, 384), (255, 0, 255))
for i, frame in enumerate(final_frames):
    sheet.paste(frame, (i * 512, 0))
sheet.save(OUTPUT, optimize=True)

contact = Image.new("RGB", (512 * 4, 384 * 3), (255, 0, 255))
for i, frame in enumerate(final_frames):
    thumb = frame.resize((256, 192), Image.Resampling.LANCZOS)
    x, y = (i % 4) * 512 + 128, (i // 4) * 384 + 64
    contact.paste(thumb, (x, y))
    ImageDraw.Draw(contact).text((x + 4, y + 2), str(i + 1), fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
contact.save(GRID, optimize=True)
final_frames[0].save(GIF, save_all=True, append_images=final_frames[1:], duration=100, loop=0, optimize=True)

qa = {
    "character": "黒田長政",
    "action": "連撃1",
    "frames": 12,
    "source": SOURCE.name,
    "source_size": [1448, 1086],
    "source_grid": "4x3, 362x362 each",
    "output": OUTPUT.name,
    "output_size": list(sheet.size),
    "sha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
    "preview_gif": GIF.name,
    "review_grid": GRID.name,
    "frame_sha256": [hashlib.sha256(frame.tobytes()).hexdigest() for frame in final_frames],
    "removed_detached_components_lt_500px": removed_components,
    "adjacent_pixel_difference_sum": [float(np.abs(np.asarray(final_frames[i], dtype=np.int16) - np.asarray(final_frames[i+1], dtype=np.int16)).sum()) for i in range(11)],
    "ground_anchor_y": 363,
    "vertical_anchor_y_by_frame": bottoms,
    "estimated_hit_frames": [7],
    "forward_step_frames": [4, 5, 6, 7, 8, 9, 10],
    "sequence": [
        "neutral low guard", "compress and turn", "dual sword windup", "step and start diagonal cut",
        "hips rotate and descend", "diagonal strike", "contact peak", "follow-through",
        "arms extend and cape trails", "low forward lunge", "retract one sword", "low crossed-sword bridge pose",
    ],
    "notes": "AI-generated 4x3 pose sheet cropped, background-keyed, uniformly scaled and composited; disconnected output components smaller than 500px were removed to clear isolated artifacts. Frame 7 is the airborne crossed-sword peak (32px above ground); other frames touch down at y=363. Not hand-drawn. Candidate timing only; hit frames are visual estimates, not game hitboxes. Frame 12 is the intended start pose for combo stage 2.",
}
QA_PATH.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"output": OUTPUT.name, "size": sheet.size, "frames": 12, "median_source_height": float(np.median(heights)), "scale": scale, "sha256": qa["sha256"], "bbox": boxes}, ensure_ascii=False, indent=2))

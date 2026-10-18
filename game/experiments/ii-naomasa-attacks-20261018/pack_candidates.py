from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage


ROOT = Path(__file__).parent
MAGENTA = (255, 0, 255)
CELL_W, CELL_H = 512, 384
ROOT_X, GROUND_Y, TARGET_BODY_H = 256, 363, 188

SHEETS = [
    {
        "source": "source_石突き打ち上げ_grid-v2.png",
        "name": "井伊直政_石突き打ち上げ_16コマ_v2",
        "count": 16,
        "hits": [7, 11],
        "advance_px": 28,
    },
    {
        "source": "source_蹴り込み突き_grid-v1.png",
        "name": "井伊直政_蹴り込み突き_14コマ_v2",
        "count": 14,
        "hits": [5, 11],
        "advance_px": 32,
    },
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def split_background(tile: Image.Image) -> tuple[Image.Image, np.ndarray, int]:
    rgb = np.asarray(tile.convert("RGB"), dtype=np.int16)
    # The generator leaves a mild magenta color gradient. Label only colors
    # close to magenta, then flood from the tile border to preserve any
    # similar-colored isolated detail on the character.
    near = (
        (rgb[:, :, 0] > 170)
        & (rgb[:, :, 2] > 170)
        & (rgb[:, :, 1] < 90)
        & (np.abs(rgb[:, :, 0] - rgb[:, :, 2]) < 80)
    )
    labels, _ = ndimage.label(near, structure=np.ones((3, 3), dtype=np.uint8))
    border = np.concatenate((labels[0], labels[-1], labels[:, 0], labels[:, -1]))
    edge_ids = np.unique(border)
    edge_ids = edge_ids[edge_ids != 0]
    bg = np.isin(labels, edge_ids)
    fg = ~bg
    comp, n = ndimage.label(fg, structure=np.ones((3, 3), dtype=np.uint8))
    sizes = np.bincount(comp.ravel())
    removed_pixels = 0
    # Remove tiny isolated artifacts, and small fragments that falsely meet a
    # source-cell edge. Preserve the main connected character/weapon silhouette;
    # a larger edge-crossing component is rejected later by the frame bounds QA.
    tiny = np.flatnonzero((sizes < 64) & (np.arange(len(sizes)) != 0))
    if len(tiny):
        removed_pixels += int(sizes[tiny].sum())
        fg[np.isin(comp, tiny)] = False
    largest = int(sizes[1:].max()) if n else 0
    if largest:
        edge_labels = np.unique(np.concatenate((comp[0], comp[-1], comp[:, 0], comp[:, -1])))
        edge_labels = edge_labels[(edge_labels != 0) & (sizes[edge_labels] < largest * 0.05)]
        if len(edge_labels):
            removed_pixels += int(sizes[edge_labels].sum())
            fg[np.isin(comp, edge_labels)] = False
    out = np.empty_like(rgb, dtype=np.uint8)
    out[:, :] = MAGENTA
    out[fg] = rgb[fg].clip(0, 255).astype(np.uint8)
    return Image.fromarray(out), fg, removed_pixels


def get_bbox(mask: np.ndarray) -> tuple[int, int, int, int]:
    ys, xs = np.nonzero(mask)
    if not len(xs):
        raise ValueError("empty animation cell")
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def build(config: dict) -> dict:
    src_path = ROOT / config["source"]
    source = Image.open(src_path).convert("RGB")
    sw, sh = source.size
    if sw % 4 or sh % 4:
        raise ValueError(f"source must be a 4x4 grid: {source.size}")
    tile_w, tile_h = sw // 4, sh // 4
    cells: list[Image.Image] = []
    masks: list[np.ndarray] = []
    removed_artifact_pixels: list[int] = []
    for n in range(16):
        row, col = divmod(n, 4)
        box = (col * tile_w, row * tile_h, (col + 1) * tile_w, (row + 1) * tile_h)
        tile, mask, removed = split_background(source.crop(box))
        if n < config["count"] and not mask.any():
            raise ValueError(f"frame {n + 1}: no foreground")
        if n >= config["count"] and mask.any():
            raise ValueError(f"unused cell {n + 1} must be blank")
        cells.append(tile)
        masks.append(mask)
        removed_artifact_pixels.append(removed)

    # Measure the character in a central body ROI, excluding most of the long
    # polearm. Use one uniform scale for the complete attack to avoid frame-size
    # pumping. Anchor each pose by the lowest support-foot pixels in this ROI.
    roi_l, roi_r = int(tile_w * 0.27), int(tile_w * 0.69)
    body_heights, supports = [], []
    for n, mask in enumerate(masks[: config["count"]]):
        ys, xs = np.nonzero(mask[:, roi_l:roi_r])
        if not len(ys):
            raise ValueError(f"frame {n + 1}: no body pixels in anchor ROI")
        body_heights.append(int(ys.max() - ys.min() + 1))
        lower = mask[int(tile_h * 0.66) :, roi_l:roi_r]
        ly, lx = np.nonzero(lower)
        if not len(ly):
            raise ValueError(f"frame {n + 1}: no foot pixels")
        foot_y = int(tile_h * 0.66) + int(ly.max())
        # Estimate the center across both feet when both are planted; during a
        # kick, the low band contains only the supporting foot.
        foot_xs = lx[ly >= ly.max() - 14] + roi_l
        supports.append((int(round((int(foot_xs.min()) + int(foot_xs.max())) / 2)), foot_y))
    body_median = float(np.median(body_heights))
    scale = TARGET_BODY_H / body_median

    strip = Image.new("RGB", (CELL_W * config["count"], CELL_H), MAGENTA)
    per_frame = []
    frames = []
    for n, (tile, mask, (fx, fy)) in enumerate(zip(cells[: config["count"]], masks[: config["count"]], supports)):
        bbox = get_bbox(mask)
        crop = tile.crop(bbox)
        crop_mask = Image.fromarray((mask[bbox[1] : bbox[3], bbox[0] : bbox[2]] * 255).astype(np.uint8))
        nw, nh = max(1, round(crop.width * scale)), max(1, round(crop.height * scale))
        resized = crop.resize((nw, nh), Image.Resampling.LANCZOS)
        alpha = crop_mask.resize((nw, nh), Image.Resampling.NEAREST)
        foot_rel_x, foot_rel_y = fx - bbox[0], fy - bbox[1]
        dx = round(ROOT_X - foot_rel_x * scale)
        dy = round(GROUND_Y - foot_rel_y * scale)
        frame = Image.new("RGB", (CELL_W, CELL_H), MAGENTA)
        frame.paste(resized, (dx, dy), alpha)
        frame_arr = np.asarray(frame)
        fg_final = np.any(frame_arr != np.asarray(MAGENTA, dtype=np.uint8), axis=2)
        final_bbox = get_bbox(fg_final)
        x0, y0, x1, y1 = final_bbox
        edge_count = int(
            fg_final[:2].sum()
            + fg_final[-2:].sum()
            + fg_final[:, :2].sum()
            + fg_final[:, -2:].sum()
        )
        if edge_count:
            raise ValueError(
                f"frame {n + 1}: foreground touches the 2px safety edge ({edge_count}); "
                f"bbox={final_bbox}, source_bbox={bbox}, scale={scale:.3f}, offset=({dx},{dy}), "
                f"source_anchor=({fx},{fy}), resized=({nw},{nh})"
            )
        if not (y1 - y0 <= CELL_H and x0 >= 2 and x1 <= CELL_W - 2):
            raise ValueError(f"frame {n + 1}: output bounds invalid {final_bbox}")
        frames.append(frame)
        strip.paste(frame, (n * CELL_W, 0))
        per_frame.append(
            {
                "frame": n + 1,
                "body_roi_height_source_px": body_heights[n],
                "support_anchor_source_xy": [fx, fy],
                "final_foreground_bbox_xyxy": [x0, y0, x1, y1],
                "edge_pixels_within_2px": edge_count,
                "source_artifact_pixels_removed": removed_artifact_pixels[n],
                "ground_y": GROUND_Y,
                "root_x": ROOT_X,
            }
        )

    strip_path = ROOT / f"{config['name']}.png"
    strip.save(strip_path, format="PNG", optimize=True)

    thumbs = Image.new("RGB", (4 * 256, 4 * 192), MAGENTA)
    for n, frame in enumerate(frames):
        thumb = frame.resize((256, 192), Image.Resampling.LANCZOS)
        thumbs.paste(thumb, ((n % 4) * 256, (n // 4) * 192))
    thumbs.save(ROOT / f"{config['name']}-contact.png", format="PNG", optimize=True)

    gif_frames = [frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=256) for frame in frames]
    gif_frames[0].save(
        ROOT / f"{config['name']}-12_5fps.gif",
        save_all=True,
        append_images=gif_frames[1:],
        duration=80,
        loop=0,
        optimize=False,
        disposal=2,
    )

    diffs = []
    for a, b in zip(frames, frames[1:]):
        aa, bb = np.asarray(a), np.asarray(b)
        diffs.append(float(np.any(aa != bb, axis=2).mean()))
    qa = {
        "candidate_only": True,
        "file": strip_path.name,
        "source_grid": src_path.name,
        "source_dimensions": [sw, sh],
        "source_cell_dimensions": [tile_w, tile_h],
        "dimensions": list(strip.size),
        "frame_count": config["count"],
        "cell_dimensions": [CELL_W, CELL_H],
        "background_rgb": list(MAGENTA),
        "facing": "right",
        "root_anchor_x": ROOT_X,
        "ground_y": GROUND_Y,
        "target_body_height_px": TARGET_BODY_H,
        "body_roi_median_source_px": body_median,
        "uniform_frame_scale": scale,
        "suggested_hit_frames_1based": config["hits"],
        "suggested_forward_travel_px": config["advance_px"],
        "whole_body_airborne": False,
        "weapon_length_strict_measurement": "not verified; review and integration check required",
        "gif_frames": len(gif_frames),
        "gif_duration_ms_per_frame": 80,
        "gif_fps": 12.5,
        "edge_contact_pixels_within_2px_per_frame": [r["edge_pixels_within_2px"] for r in per_frame],
        "source_artifact_pixels_removed_per_frame": [r["source_artifact_pixels_removed"] for r in per_frame],
        "adjacent_changed_pixel_fraction": diffs,
        "frames": per_frame,
        "sha256": sha256(strip_path),
        "visual_motion_review": "static contact sheet reviewed; full gameplay motion not verified",
    }
    (ROOT / f"{config['name']}-qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return qa


def main() -> None:
    for item in SHEETS:
        print(json.dumps(build(item), ensure_ascii=False))


if __name__ == "__main__":
    main()

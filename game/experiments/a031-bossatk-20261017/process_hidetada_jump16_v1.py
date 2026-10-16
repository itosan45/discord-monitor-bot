from PIL import Image
import numpy as np
import hashlib, json, os

ROOT = 'game/experiments/a031-bossatk-20261017'
SRC = ROOT + '/徳川秀忠_跳び込み攻撃_16f-source-v1.png'
BASE = ROOT + '/徳川秀忠_跳び込み攻撃'
im = Image.open(SRC).convert('RGB')
assert im.size == (1254, 1254), im.size

sheet = Image.new('RGB', (16 * 512, 384), (255, 0, 255))
boxes, magenta_counts, edge_counts, pixel_hashes = [], [], [], []
for i in range(16):
    row, col = divmod(i, 4)
    x0, x1 = round(col * im.width / 4), round((col + 1) * im.width / 4)
    y0, y1 = round(row * im.height / 4), round((row + 1) * im.height / 4)
    tile = np.asarray(im.crop((x0, y0, x1, y1)).convert('RGB')).copy()
    # Source background is a slightly noisy magenta. Replace only key-like pixels;
    # preserve all character/effect pixels and do not crop/scale per-pose bboxes.
    r, g, b = tile[..., 0], tile[..., 1], tile[..., 2]
    key = (r > 220) & (b > 220) & (g < 65) & (np.abs(r.astype(np.int16) - b.astype(np.int16)) < 45)
    # Remove only tiny detached generation specks; keep connected accessories/effects.
    fg = ~key
    seen = np.zeros(fg.shape, dtype=bool)
    h, w = fg.shape
    for sy, sx in zip(*np.where(fg)):
        if seen[sy, sx]:
            continue
        stack = [(int(sy), int(sx))]
        seen[sy, sx] = True
        component = []
        while stack:
            cy, cx = stack.pop()
            component.append((cy, cx))
            for ny in range(max(0, cy - 1), min(h, cy + 2)):
                for nx in range(max(0, cx - 1), min(w, cx + 2)):
                    if fg[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((ny, nx))
        if len(component) < 24:
            for cy, cx in component:
                key[cy, cx] = True
    keyed = tile.copy()
    keyed[key] = (255, 0, 255)
    # Uniform 1.08 scale retains vertical jump travel across poses.
    frame = Image.fromarray(keyed).resize((round(tile.shape[1] * 1.08), round(tile.shape[0] * 1.08)), Image.Resampling.LANCZOS)
    cx = i * 512 + 256
    px, py = cx - frame.width // 2, 8
    sheet.paste(frame, (px, py))
    a = np.asarray(sheet.crop((i * 512, 0, (i + 1) * 512, 384)))
    mask = np.any(a != (255, 0, 255), axis=2)
    yy, xx = np.where(mask)
    boxes.append([int(xx.min()), int(yy.min()), int(xx.max()), int(yy.max())])
    edge_counts.append(int(mask[0].sum() + mask[-1].sum() + mask[:, 0].sum() + mask[:, -1].sum()))
    magenta_counts.append(int((~mask).sum()))
    pixel_hashes.append(hashlib.sha256(a.tobytes()).hexdigest())

out = BASE + '_跳び込み攻撃_16コマ_v1.png'
# Name follows existing Japanese conventions; keep unique and never replace the 8-frame sheet.
out = ROOT + '/徳川秀忠_跳び込み攻撃_16コマ_v1.png'
sheet.save(out, optimize=True)
grid = Image.new('RGB', (4 * 512, 4 * 384), (40, 40, 40))
for i in range(16):
    grid.paste(sheet.crop((i * 512, 0, (i + 1) * 512, 384)), ((i % 4) * 512, (i // 4) * 384))
grid_path = ROOT + '/徳川秀忠_跳び込み攻撃_review-grid-16f-v1.png'
grid.save(grid_path, optimize=True)
frames = [sheet.crop((i * 512, 0, (i + 1) * 512, 384)) for i in range(16)]
gif_path = ROOT + '/徳川秀忠_跳び込み攻撃_preview-16f-v1.gif'
frames[0].save(gif_path, save_all=True, append_images=frames[1:], duration=90, loop=0, disposal=2)
g = Image.open(gif_path)
decoded = []
for i in range(g.n_frames):
    g.seek(i)
    decoded.append(np.asarray(g.convert('RGB').copy()))
unique = len({hashlib.sha256(f.tobytes()).hexdigest() for f in decoded})
changed = [round(float(np.mean(np.any(decoded[i] != decoded[i + 1], axis=2))), 4) for i in range(15)]
assert g.n_frames == 16 and unique == 16
assert not any(edge_counts), edge_counts
qa = {
  'character': '徳川秀忠', 'attack': '跳び込み銃床打ち', 'asset': os.path.basename(out),
  'status': 'candidate, not game-integrated', 'sheet_size': [8192, 384], 'cell_size': [512, 384],
  'frames': 16, 'source_grid_size': list(im.size), 'source_grid': '4x4, row-major',
  'background_rgb': [255, 0, 255], 'frame_foreground_bboxes': boxes,
  'magenta_pixel_counts_per_cell': magenta_counts, 'nonmagenta_outer_edge_pixels_per_cell': edge_counts,
  'decoded_gif_frames': g.n_frames, 'unique_frame_count': unique,
  'adjacent_changed_pixel_fraction': changed,
  'sha256': hashlib.sha256(open(out, 'rb').read()).hexdigest(),
  'generation': 'OpenAI built-in imagegen; references: existing Hidetada 8-frame jump sheet and prior rejected 16-pose attempt. AI-generated source, cell extraction and uniform scaling; not hand-drawn.',
  'notes': 'Sixteen sequential pose slots cover crouch, launch, ascent, midair gun-butt wind-up, descent, impact and recovery. Uniform tile scale preserves generated vertical travel; frames remain a candidate. Visual/runtime review pending.'
}
qa_path = ROOT + '/徳川秀忠_跳び込み攻撃_qa-16f-v1.json'
with open(qa_path, 'w', encoding='utf-8') as f:
    json.dump(qa, f, ensure_ascii=False, indent=2)
print(json.dumps({'asset': out, 'sha256': qa['sha256'], 'unique': unique, 'edges': edge_counts, 'changed': changed}, ensure_ascii=False))

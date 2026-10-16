from PIL import Image
import numpy as np
import hashlib, json, os

ROOT = 'game/experiments/a031-bossatk-20261017'
CHARACTERS = ['徳川家康', '小早川秀秋', '本多忠勝', '黒田長政', '福島正則']

def prune_tiny_specks(tile):
    r, g, b = tile[..., 0], tile[..., 1], tile[..., 2]
    bg = (r > 220) & (b > 220) & (g < 65) & (np.abs(r.astype(np.int16) - b.astype(np.int16)) < 45)
    fg = ~bg
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
                bg[cy, cx] = True
    tile[bg] = (255, 0, 255)
    return tile

for character in CHARACTERS:
    src = f'{ROOT}/{character}_跳び込み攻撃_16f-source-v1.png'
    original = Image.open(src).convert('RGB')
    assert original.width % 4 == 0 and original.height % 4 == 0, (character, original.size)
    w, h = original.width // 4, original.height // 4
    sheet = Image.new('RGB', (16 * 512, 384), (255, 0, 255))
    boxes, edges, hashes = [], [], []
    for i in range(16):
        row, col = divmod(i, 4)
        tile = np.asarray(original.crop((col * w, row * h, (col + 1) * w, (row + 1) * h))).copy()
        tile = prune_tiny_specks(tile)
        frame = Image.fromarray(tile).resize((round(w * 1.08), round(h * 1.08)), Image.Resampling.LANCZOS)
        sheet.paste(frame, (i * 512 + 256 - frame.width // 2, 16))
        cell = np.asarray(sheet.crop((i * 512, 0, (i + 1) * 512, 384)))
        mask = np.any(cell != (255, 0, 255), axis=2)
        yy, xx = np.where(mask)
        boxes.append([int(xx.min()), int(yy.min()), int(xx.max()), int(yy.max())])
        edges.append(int(mask[0].sum() + mask[-1].sum() + mask[:, 0].sum() + mask[:, -1].sum()))
        hashes.append(hashlib.sha256(cell.tobytes()).hexdigest())
    # Apply one common offset so the opening stance rests on the project groundline.
    first = np.asarray(sheet.crop((0, 0, 512, 384)))
    first_mask = np.any(first != (255, 0, 255), axis=2)
    first_y, _ = np.where(first_mask)
    dy = 363 - int(first_y.max())
    aligned = Image.new('RGB', sheet.size, (255, 0, 255))
    for i in range(16):
        aligned.paste(sheet.crop((i * 512, 0, (i + 1) * 512, 384)), (i * 512, dy))
    sheet = aligned
    boxes, edges = [], []
    for i in range(16):
        cell = np.asarray(sheet.crop((i * 512, 0, (i + 1) * 512, 384)))
        mask = np.any(cell != (255, 0, 255), axis=2)
        yy, xx = np.where(mask)
        boxes.append([int(xx.min()), int(yy.min()), int(xx.max()), int(yy.max())])
        edges.append(int(mask[0].sum() + mask[-1].sum() + mask[:, 0].sum() + mask[:, -1].sum()))
    out = f'{ROOT}/{character}_跳び込み攻撃_16コマ_v1.png'
    sheet.save(out, optimize=True)
    grid = Image.new('RGB', (4 * 512, 4 * 384), (40, 40, 40))
    frames = []
    for i in range(16):
        frame = sheet.crop((i * 512, 0, (i + 1) * 512, 384))
        grid.paste(frame, ((i % 4) * 512, (i // 4) * 384))
        frames.append(frame)
    grid.save(f'{ROOT}/{character}_跳び込み攻撃_review-grid-16f-v1.png', optimize=True)
    gif = f'{ROOT}/{character}_跳び込み攻撃_preview-16f-v1.gif'
    frames[0].save(gif, save_all=True, append_images=frames[1:], duration=90, loop=0, disposal=2)
    decoded = []
    g = Image.open(gif)
    for i in range(g.n_frames):
        g.seek(i)
        decoded.append(np.asarray(g.convert('RGB').copy()))
    unique = len({hashlib.sha256(x.tobytes()).hexdigest() for x in decoded})
    changed = [round(float(np.mean(np.any(decoded[i] != decoded[i + 1], axis=2))), 4) for i in range(15)]
    assert g.n_frames == 16 and unique == 16, (character, g.n_frames, unique)
    assert not any(edges), (character, edges)
    qa = {
      'character': character, 'attack': 'jump-in weapon strike', 'asset': os.path.basename(out),
      'status': 'candidate, not game-integrated', 'sheet_size': [8192, 384], 'cell_size': [512, 384],
      'frames': 16, 'source_grid_size': list(original.size), 'source_grid': '4x4, row-major',
      'background_rgb': [255, 0, 255], 'frame_foreground_bboxes': boxes,
      'uniform_vertical_shift_to_groundline_y363': dy,
      'nonmagenta_outer_edge_pixels_per_cell': edges, 'decoded_gif_frames': g.n_frames,
      'unique_frame_count': unique, 'adjacent_changed_pixel_fraction': changed,
      'sha256': hashlib.sha256(open(out, 'rb').read()).hexdigest(),
      'generation': 'OpenAI built-in imagegen using this character\'s existing 8-frame jump sheet as reference; AI generated source, tile extraction, uniform scaling, and small detached-speck cleanup; not hand-drawn.',
      'notes': 'Candidate motion phases: load, takeoff, ascent, aerial wind-up, descent, impact, recoil, recovery. One uniform vertical shift aligns the opening pose to y363 while preserving all relative pose travel. Game timing/hitbox and independent review pending.'
    }
    with open(f'{ROOT}/{character}_跳び込み攻撃_qa-16f-v1.json', 'w', encoding='utf-8') as f:
        json.dump(qa, f, ensure_ascii=False, indent=2)
    print(json.dumps({'character': character, 'sha256': qa['sha256'], 'unique': unique, 'edges': edges, 'adjacent_changed': changed}, ensure_ascii=False))

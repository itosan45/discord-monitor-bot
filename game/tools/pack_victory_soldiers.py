"""Pack the two accepted victory soldier strips; preserve source PNGs."""
import hashlib
import json
import pathlib
import shutil
import sys

import numpy as np
from PIL import Image, ImageSequence

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'game/sprites'))
from mk import keyim

def pack(source_dir, qa_dir):
    source_dir, qa_dir = pathlib.Path(source_dir), pathlib.Path(qa_dir)
    qa_dir.mkdir(parents=True, exist_ok=True)
    meta_path = ROOT / 'game/sprites/sprmeta.json'
    meta = json.loads(meta_path.read_text(encoding='utf-8'))
    report = []
    for key, name, target_height in [
        ('kgun_sword', '味方_足軽_勝鬨_4コマ_v1.png', 142),
        ('kgun_armor', '味方_鎧武者_勝鬨_4コマ_v1.png', 156),
    ]:
        source = source_dir / name
        image = Image.open(source).convert('RGB')
        assert image.size == (1024, 256)
        a = np.asarray(image).astype(int)
        fg = abs(a[..., 0]-255)+a[..., 1]+abs(a[..., 2]-255) > 150
        frames, bounds, hashes = [], [], []
        for i in range(4):
            frame = image.crop((i*256, 0, (i+1)*256, 256))
            y, x = np.where(fg[:, i*256:(i+1)*256])
            assert len(x) > 3000
            box = [int(x.min()), int(y.min()), int(x.max()+1), int(y.max()+1)]
            assert box[0] >= 16 and box[1] >= 16 and box[2] <= 240
            assert 228 <= y.max() <= 232
            frames.append(frame); bounds.append(box)
            hashes.append(hashlib.sha256(frame.tobytes()).hexdigest())
        assert len(set(hashes)) == 4
        gif_path = qa_dir / (source.stem+'.gif')
        frames[0].save(gif_path, save_all=True, append_images=frames[1:], duration=180, loop=0, disposal=2)
        decoded = [f.convert('RGB').copy() for f in ImageSequence.Iterator(Image.open(gif_path))]
        assert len(decoded) == 4
        decoded_sheet = Image.new('RGB', (1024,256))
        for i, f in enumerate(decoded): decoded_sheet.paste(f,(i*256,0))
        decoded_sheet.save(qa_dir / (source.stem+'_GIF復号.png'))
        sprite = Image.fromarray(keyim(image))
        arr = []
        # Scale from chest-fist frame, never raised-fist height, so the body
        # stays the same size throughout the four poses.
        scale = target_height / (bounds[0][3]-bounds[0][1])
        for i, box in enumerate(bounds):
            x0,y0,x1,y1=box
            arr.append([i*256+x0,y0,x1-x0,y1-y0,round((x0-128)*scale),round((y0-231)*scale),round(scale,4)])
        meta[key] = {'idle':[arr[0]],'kachi':arr}
        sprite.save(ROOT / 'game/sprites' / ('atlas_'+key+'.webp'), format='WEBP', lossless=True)
        dest = ROOT / 'assets/sprites' / name
        if dest.exists(): assert dest.read_bytes() == source.read_bytes(), 'Refuse existing PNG overwrite'
        else: shutil.copyfile(source, dest)
        report.append({'name':name,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'bounds':bounds,'uniqueFrames':4,'gifDecodedFrames':4,'source':str(source),'status':'geometry_pass'})
    meta_path.write_text(json.dumps(meta,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    (qa_dir/'soldier-victory-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))

if __name__ == '__main__': pack(sys.argv[1],sys.argv[2])

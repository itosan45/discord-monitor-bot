import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image
import rife_core as R

SRC = '/home/user/discord-monitor-bot/assets/sprites/真田幸村_歩き_6コマ.png'
OUT = '/tmp/claude-0/rife/out'
MODEL = sys.argv[1] if len(sys.argv) > 1 else 'flownet_v4.25'
SCALE = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
tag = f"{MODEL.replace('flownet_', '')}_s{SCALE:g}"
os.makedirs(OUT, exist_ok=True)

sheet = np.array(Image.open(SRC).convert('RGB'))
n, cw = 6, 256
frames = [sheet[:, i * cw:(i + 1) * cw] for i in range(n)]
net = R.load(f'/tmp/claude-0/rife/models/{MODEL}.pkl', SCALE)
out = []
t0 = time.time()
for i in range(n):
    a, b = frames[i], frames[(i + 1) % n]  # 歩きは循環するので最後→最初も補間
    out.append(a)
    out.append(R.interp(net, a, b, 0.5))
print('interp sec', round(time.time() - t0, 1))
sheet2 = np.concatenate(out, axis=1)
Image.fromarray(sheet2).save(f'{OUT}/yuki_walk12_{tag}.png')
print('saved', f'{OUT}/yuki_walk12_{tag}.png', sheet2.shape)

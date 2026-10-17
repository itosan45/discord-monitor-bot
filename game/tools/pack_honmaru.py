"""2026-10-14 A-017 敵武将8人の本丸背景(1920×1080)を、ゲーム用の背景 gfx/bg_honmaru_<ボスのキー>.webp(1280×720)にする。元PNGは変更しない。
ボス戦(G.boss が出る)の間だけ、その武将の本丸に切り替える(ゲーム側 G.hon / drawBG)。キー: 福島正則=boss9 小早川秀秋=boss4 黒田長政=boss8 徳川秀忠=boss5 最上義光=boss2 井伊直政=boss1 本多忠勝=boss7 徳川家康=boss3。
使い方: python3 game/tools/pack_honmaru.py  → cd game && python3 build.py"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'assets' / 'sprites'
GFX = ROOT / 'gfx'
BOSS = {'福島正則': 'boss9', '小早川秀秋': 'boss4', '黒田長政': 'boss8', '徳川秀忠': 'boss5', '最上義光': 'boss2', '井伊直政': 'boss1', '本多忠勝': 'boss7', '徳川家康': 'boss3'}
for name, key in BOSS.items():
    im = Image.open(SRC / f'背景_本丸_{name}_v1.png').convert('RGB')
    assert im.size == (1920, 1080), (name, im.size)
    out = im.resize((1280, 720), Image.LANCZOS)
    p = GFX / f'bg_honmaru_{key}.webp'
    out.save(p, 'WEBP', quality=80, method=6)
    print(name, key, p.stat().st_size // 1024, 'KB')

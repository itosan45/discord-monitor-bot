from pathlib import Path
import hashlib
import json

from PIL import Image, ImageDraw

ROOT = Path(__file__).parent
qa_names = [
    "黒田長政_連撃1_qa-v5.json",
    "黒田長政_連撃2_qa-v4.json",
    "黒田長政_連撃3_qa-v4.json",
]
qas = [json.loads((ROOT / name).read_text(encoding="utf-8")) for name in qa_names]
frames = []
for qa in qas:
    sheet = Image.open(ROOT / qa["output"]).convert("RGB")
    count = qa["frames"]
    frames.extend(sheet.crop((i * 512, 0, (i + 1) * 512, 384)) for i in range(count))

gif_path = ROOT / "黒田長政_連撃3段_40コマ_preview-v2.gif"
assert not gif_path.exists(), "Refusing to overwrite"
frames[0].save(gif_path, save_all=True, append_images=frames[1:], duration=100, loop=0, optimize=True)

transitions = [(frames[11], frames[12]), (frames[23], frames[24])]
compare = Image.new("RGB", (2048, 900), (255, 0, 255))
draw = ImageDraw.Draw(compare)
labels = ["Combo 1 end -> Combo 2 start", "Combo 2 end -> Combo 3 start"]
for i, (left, right) in enumerate(transitions):
    y = i * 450 + 24
    compare.paste(left.resize((512, 384), Image.Resampling.LANCZOS), (300, y + 40))
    compare.paste(right.resize((512, 384), Image.Resampling.LANCZOS), (1000, y + 40))
    draw.text((300, y + 10), labels[i], fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
    draw.text((300, y + 420), "previous end", fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
    draw.text((1000, y + 420), "next start", fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
compare_path = ROOT / "黒田長政_連撃3段_接続比較-v2.png"
assert not compare_path.exists(), "Refusing to overwrite"
compare.save(compare_path, optimize=True)

qa = {
    "character": "黒田長政",
    "stage_sheets": [qa["output"] for qa in qas],
    "total_frames": len(frames),
    "chain_preview_gif": gif_path.name,
    "chain_preview_gif_frames": Image.open(gif_path).n_frames,
    "transition_comparison": compare_path.name,
    "transition_pairs": [
        {"from": "連撃1 frame12", "to": "連撃2 frame1", "pixel_difference_sum": sum(abs(a - b) for a, b in zip(transitions[0][0].tobytes(), transitions[0][1].tobytes()))},
        {"from": "連撃2 frame12", "to": "連撃3 frame1", "pixel_difference_sum": sum(abs(a - b) for a, b in zip(transitions[1][0].tobytes(), transitions[1][1].tobytes()))},
    ],
    "note": "Static comparison and 40-frame GIF review only; frame rate, hit timing, position transition, and game playback require Claude integration QA.",
}
(ROOT / "黒田長政_連撃3段_QA-v2.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(qa, ensure_ascii=False, indent=2))

# A-028: Ii Naomasa fall and recovery candidates

Status: visual-review candidate only. Not yet approved as a completed game asset; runtime integration is Claude's responsibility.

## Files

- `井伊直政_転倒_4コマ_v1.png`: 4 frames, 1536x384, 384x384 cells.
- `井伊直政_起き上がり_4コマ_v1.png`: 4 frames, 1536x384, 384x384 cells.
- `source_fall.png` and `source_getup.png`: generated 2x2 pose canvases retained for provenance.
- `pack_fall.py` and `pack_getup.py`: reproducible separation/repacking scripts.
- `qa.json`: dimensions, frame bounds, baseline, and SHA-256.
- `井伊直政_転倒_preview.gif` and `井伊直政_起き上がり_preview.gif`: four-frame visual previews.

## Method and review

Generated pose canvases from the existing `assets/sprites/井伊直政_設定画.png` and `assets/sprites/井伊直政_待機_4コマ.png` visual identity (fall canvas references that generated pose sheet for costume consistency). Connected foreground components were separated from the magenta backdrop, scaled against the existing idle figure height (~188 px), and centered in four 384x384 cells. The four frame ground contact pixels align at y=363; cell edges remain magenta. The output retains the crimson armor, antler helmet, cape, and katana. Static inspection and 4-frame sequence review pass; actual game timing, facing under both directions, and runtime use have not been checked.

These are AI-generated poses composed and scaled into sheets, not hand-drawn art. Keep as candidates until Claude checks them in-game and confirms hit/recovery timing and visual scale.

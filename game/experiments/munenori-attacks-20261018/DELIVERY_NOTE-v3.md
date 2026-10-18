# 納品候補: 柳生宗矩 追加攻撃2種

- 居合斬り: `柳生宗矩_居合斬り_12コマ_v3.png` (12 frames, impact 7, forward proposal 22px).
- 二連斬り: `柳生宗矩_二連斬り_20コマ_v2.png` (20 frames, impacts 6 and 14, forward proposal 30px).
- Previews: corresponding `-12fps.gif`; contact sheets and numerical QA JSON accompany each PNG. `motion-review-v4.html` plays both.
- QA: cells 512x384; pure RGB(255,0,255); no foreground pixels within the outer two pixels; estimated central silhouette medians 188px and 187px. Candidate only; no game code/atlas changes.
- Weapon length across frames, actual hit-box alignment, integration scale, and the three required runtime modes remain for Claude to verify. The double-slash source is an AI-drawn candidate, not hand-rendered sprite art.

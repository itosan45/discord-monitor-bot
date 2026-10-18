"""8曲: ステージ2〜6・ボス・ラスボス・エンディング。python3 songs.py <名前...|all>
各曲は 32小節(エンディングは24小節)のループ。曲の骨組み(stage)は共通で、調・リズム・楽器・主題が違う。"""
import sys
from kit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'gfx')

def prog32(sections):
    out = []
    for n, cs in sections:
        for i in range(n):
            out.append(cs[i % len(cs)])
    return out

def stage(name, bpm, seed, chords, thA, thB, ost, tk=43, solo='shaku', intro=None, extra=None, vo=None,
          bedvel=(78, 80, 84, 90), gallop_from=12, tkvel=(96, 100, 104, 112), bass_rhy=None, tpat=None):
    """疾走する戦場曲の共通骨組み。
    0-3 導入 / 4-11 主題A(ホルン) / 12-19 主題B(トランペット+ヴァイオリン) / 20-27 全員でA(最大) / 28-31 つなぎ"""
    S = Song(name, bpm, 32, seed=seed)
    kw = dict(solo=solo); kw.update(vo or {}); setup(S, **kw)
    ch = chords
    sec = lambda b: 0 if b < 4 else 1 if b < 12 else 2 if b < 20 else 3 if b < 28 else 2
    for b in range(32):                                    # 弦の16分刻み(常時)
        s = sec(b); pat = ost[min(s, len(ost) - 1)]
        ostinato(S, CH['stac'], ch, [b], pat, octave=3, vel=bedvel[s], acc=14)
    root_line(S, CH['cello'], ch, range(0, 32), [(i * 0.5, 0.5, 'r') for i in range(8)], octave=2, vel=84)
    root_line(S, CH['bass'], ch, range(4, 32), bass_rhy or [(0, 1.5, 'r'), (1.5, .5, 'r'), (2, 1.5, 'r'), (3.5, .5, 'f')], octave=1, vel=96)
    for b in range(32):                                    # タイコ: 前へ進むギャロップ
        s = sec(b); v = tkvel[s]
        if b >= gallop_from or (b >= 4 and b % 2 == 1) or b >= 2:
            gallop_bar(S, CH['taiko'], b, tk, v, beats=(0, 1, 2, 3))
        else:
            for bt in (0, 2): S.note(CH['taiko'], b * 4 + bt, 0.5, tk, v)
    timp_hits(S, ch, range(4, 32), tpat or [(0, .5, 'r', 108), (2, .5, 'r', 100), (3, .5, 'f', 96)])
    for i, t in enumerate(thA): S.mel(CH['horn'], 4 + i, t, 100)
    for i, t in enumerate(thB):
        S.mel(CH['trp'], 12 + i, t, 100)
        S.mel(CH['vln'], 12 + i, t, 84)
        S.mel(CH['horn'], 12 + i, t, 78, trans=-12)
    for i, t in enumerate(thA):
        S.mel(CH['horn'], 20 + i, t, 106)
        S.mel(CH['trp'], 20 + i, t, 96, trans=12)
        S.mel(CH['vln'], 20 + i, t, 90, trans=12)
    if intro:
        for bar, t, v in intro: S.mel(CH['solo'], bar, t, v)
    pad(S, CH['str'], ch, range(4, 32), octave=4, vel=60)
    pad(S, CH['choir'], ch, range(12, 20), octave=4, vel=62)
    pad(S, CH['choir'], ch, range(20, 28), octave=4, vel=78)
    pad(S, CH['tbn'], ch, range(20, 28), octave=3, vel=70, notes=(0, 2))
    for b in range(20, 28):                               # 最大部: 小太鼓の8分刻み
        for k in range(8): S.note(9, b * 4 + k * 0.5, 0.3, 38, 78 if k % 2 == 0 else 58)
    for b in (4, 12, 20, 28): crash(S, b, 108)
    for b in (3, 11, 19, 27, 31):
        n = 4 if b == 31 else 2
        snare_roll(S, b, 52, 118, beats=n)
        fill_roll(S, CH['timp'], b, midi(ch[b][0] + '2'), 70, 118, beats=n)
        riser(S, b, 4, 80)
    for b in (4, 12, 20, 28):
        r, q = ch[b]; t = chord(r, q, 3)
        for p in t[:3]: S.note(CH['hit'], b * 4, 0.5, p, 100)
    for b0, b1, v0, v1 in ((0, 4, 104, 118), (8, 12, 108, 122), (16, 20, 110, 125), (24, 28, 114, 127)):
        for c in (CH['str'], CH['choir'], CH['horn']): S.ramp(c, b0 * 4, b1 * 4, v0, v1)
    if extra: extra(S, ch)
    return S

# ---------- ステージ2「松尾山の雨」ニ短調156 : 張りつめて駆け抜ける ----------
def matsuo():
    D, Bb, C, Gm, A, F = ('D','m'), ('Bb','M'), ('C','M'), ('G','m'), ('A','M'), ('F','M')
    ch = prog32([(4, [D, D, D, A]), (8, [D, D, Bb, C, D, Gm, A, A]), (8, [Bb, F, Gm, A, Bb, C, D, A]),
                 (8, [D, D, Bb, C, D, Gm, A, A]), (4, [Bb, C, A, A])])
    thA = ["D5/1.5 D5/.5 F5/1 A5/1", "G5/1.5 F5/.5 E5/1 D5/1", "D5/1 F5/1 Bb5/1.5 A5/.5", "G5/1.5 E5/.5 G5/1 C6/1",
           "D6/1.5 D6/.5 C6/1 A5/1", "Bb5/1.5 A5/.5 G5/1 F5/1", "E5/1 A5/1 C#6/1 E6/1", "D6/1 C#6/1 A5/2"]
    thB = ["F5/1 Bb5/1 D6/2", "C6/1.5 A5/.5 F5/1 A5/1", "Bb5/1 D6/1 G6/2", "F6/1.5 E6/.5 C#6/1 A5/1",
           "D6/1 F6/1 Bb6/1.5 A6/.5", "G6/1 E6/1 C6/1 E6/1", "F6/1.5 E6/.5 D6/1 A5/1", "A5/.5 C#6/.5 E6/.5 A6/.5 G6/1 E6/1"]
    ost = [[0, 2, 3, 2] * 4, [0, 2, 3, 2] * 4, [0, 2, 3, 2] * 4, ['0>', 2, 3, 2, '0>', 2, 3, 2, '0>', 2, 3, 2, '0>', 2, 3, '2>']]
    intro = [(0, "D5/2 F5/1 E5/1 D5/3 r/1", 90), (2, "A5/2 G5/1 F5/1 E5/3 C#5/1", 90)]
    def extra(S, ch):                                      # ピアノ: 低音オクターブの8分が駆ける(B・C)
        piano_pulse(S, CH['harp'], ch, range(12, 28), vel=76)
    return stage('matsuo', 156, 2, ch, thA, thB, ost, tk=43, solo='shaku', intro=intro, extra=extra, vo=dict(harp='piano'))

# ---------- ステージ3「笹尾山の死闘」ホ短調(フリジアン)168 : 激突 ----------
def sasao():
    Em, F, D, C, B, G = ('E','m'), ('F','M'), ('D','M'), ('C','M'), ('B','M'), ('G','M')
    ch = prog32([(4, [Em, Em, F, Em]), (8, [Em, Em, F, Em, Em, C, D, B]), (8, [C, D, Em, B, C, D, Em, Em]),
                 (8, [Em, Em, F, Em, Em, C, D, B]), (4, [C, D, F, B])])
    thA = ["E5/1 E5/.5 G5/.5 B5/1 E6/1", "D6/1.5 B5/.5 G5/1 B5/1", "F5/1 F5/.5 A5/.5 C6/1 F6/1", "E6/1.5 D6/.5 B5/1 G5/1",
           "E5/.5 E5/.5 G5/1 B5/1 E6/1", "G5/1 C6/1 E6/1 G6/1", "F#6/1.5 E6/.5 D6/1 A5/1", "D#6/1 F#6/1 B6/2"]
    thB = ["G5/1 C6/1 E6/2", "A5/1 D6/1 F#6/2", "G6/1.5 F#6/.5 E6/1 B5/1", "B5/.5 D#6/.5 F#6/.5 B6/.5 A6/1 F#6/1",
           "G6/1 E6/1 C6/1 E6/1", "A6/1 F#6/1 D6/1 F#6/1", "E6/1.5 G6/.5 B6/2", "B6/.5 A6/.5 G6/.5 F#6/.5 E6/1 D#6/1"]
    ost = [['0>', 0, 2, 0] * 4, ['0>', 0, 2, 0, '0>', 0, 2, 0, '0>', 0, 3, 2, '0>', 2, 3, '2>'],
           ['0>', 0, 2, 0, '0>', 0, 3, 0, '0>', 0, 2, 0, '0>', 0, 3, '2>'],
           ['0>', 0, 2, 3, '0>', 2, 3, 2, '0>', 0, 2, 3, '0>', 2, 3, '2>']]
    intro = [(0, "E4/.5 E4/.25 G4/.25 A4/.5 B4/.5 D5/.5 B4/.5 A4/.5 G4/.5 E4/1 r/2 E4/.5 E4/.25 G4/.25 A4/.5 B4/.5 E5/1 D5/.5 B4/.5 A4/1 B4/2 r/1", 100)]
    return stage('sasao', 168, 3, ch, thA, thB, ost, tk=40, solo='shami', intro=intro,
                 tkvel=(100, 104, 108, 116))

# ---------- ステージ4「上田城の伏兵」ト短調(陰旋法)160 : 忍び寄って襲う ----------
def ueda():
    Gm, Ab, Cm, Eb, D, Bb, F = ('G','m'), ('Ab','M'), ('C','m'), ('Eb','M'), ('D','M'), ('Bb','M'), ('F','M')
    ch = prog32([(4, [Gm, Gm, Ab, D]), (8, [Gm, Gm, Ab, Gm, Cm, Eb, F, D]), (8, [Eb, Bb, Cm, D, Eb, F, Gm, D]),
                 (8, [Gm, Gm, Ab, Gm, Cm, Eb, F, D]), (4, [Ab, F, Eb, D])])
    thA = ["G5/1 Ab5/.5 G5/.5 D6/1 C6/1", "Bb5/1.5 G5/.5 D5/2", "Ab5/1 C6/.5 Eb6/.5 Ab6/1 G6/1", "F6/1 D6/1 Bb5/1 G5/1",
           "C6/1 Eb6/1 G6/1.5 F6/.5", "Eb6/1 Bb5/1 G5/2", "A5/1 C6/1 F6/1 A6/1", "D6/1.5 C6/.5 A5/1 F#5/1"]
    thB = ["Eb6/1.5 D6/.5 Bb5/2", "D6/1.5 Bb5/.5 F5/2", "Eb6/1 G6/1 C7/2", "D7/1 C7/1 A6/1 F#6/1",
           "G6/1 Bb6/1 Eb7/2", "F7/1.5 Eb7/.5 C7/1 A6/1", "Bb6/1.5 A6/.5 G6/1 D6/1", "F#6/.5 A6/.5 D7/.5 F#7/.5 D7/1 A6/1"]
    ost = [[0, None, None, 2, None, 3, None, 2, 0, None, None, 2, None, 3, 2, None],
           [0, None, 2, None, 3, None, 2, None, 0, None, 2, 3, 2, None, 3, None],
           [0, None, 2, 3, 2, 3, None, 2, 0, None, 2, 3, 2, 3, 2, 3],
           ['0>', 2, 3, 2, '0>', 2, 3, 2, '0>', 2, 3, 2, '0>', 2, 3, '2>']]
    intro = [(0, "G4/.5 r/.5 Ab4/.5 G4/.5 D5/1 r/1 G4/.5 r/.5 Ab4/.5 G4/.5 C5/1 Bb4/1 G4/.5 Ab4/.5 D5/1 C5/1 Ab4/1", 98)]
    return stage('ueda', 160, 4, ch, thA, thB, ost, tk=43, solo='koto', intro=intro,
                 vo=dict(stac='pizz'), bedvel=(80, 82, 86, 92), gallop_from=16, tkvel=(92, 96, 102, 112))

# ---------- ステージ5「長谷堂の夜戦」ロ短調164 : 闇を切り裂く ----------
def hasedo():
    Bm, G, D, A, Em, F_, Fs, Bm7 = ('B','m'), ('G','M'), ('D','M'), ('A','M'), ('E','m'), ('F#','m'), ('F#','M'), ('B','m')
    ch = prog32([(4, [Bm, Bm, G, Fs]), (8, [Bm, G, D, A, Bm, G, Em, Fs]), (8, [G, D, Em, Fs, G, A, Bm, Fs]),
                 (8, [Bm, G, D, A, Bm, G, Em, Fs]), (4, [G, A, Fs, Fs])])
    thA = ["B5/1.5 B5/.5 D6/1 F#6/1", "E6/1 D6/1 B5/2", "D6/1.5 D6/.5 F#6/1 A6/1", "G6/1 F#6/1 E6/1 C#6/1",
           "B5/1.5 D6/.5 F#6/1 B6/1", "A6/1 G6/1 E6/2", "B5/1 E6/1 G6/1 B6/1", "A#6/1 F#6/1 C#6/2"]
    thB = ["D6/1 G6/1 B6/2", "A6/1.5 F#6/.5 D6/2", "G6/1 B6/1 E7/2", "F#7/1 E7/1 C#7/1 A#6/1",
           "D7/1 B6/1 G6/1 B6/1", "E7/1 C#7/1 A6/1 E6/1", "D7/1.5 B6/.5 F#6/2", "A#6/.5 C#7/.5 F#7/1 E7/1 C#7/1"]
    ost = [[0, 1, 2, 1, 0, 1, 2, 1, 0, 1, 2, 1, 0, 1, 2, 1], [0, 1, 2, 3, 2, 1, 2, 1] * 2,
           [0, 2, 3, 2, 0, 2, 3, 2, 0, 2, 3, 4, 3, 2, 3, 2], ['0>', 1, 2, 3, '0>', 1, 2, 3, '0>', 1, 2, 3, '0>', 2, 3, '4>']]
    intro = [(0, "B4/2 D5/1 C#5/1 B4/3 r/1", 92), (2, "F#5/2 E5/1 D5/1 C#5/3 A#4/1", 92)]
    def extra(S, ch):                                      # 夜: ピアノの分散和音+ヴァイオリン独奏の嘆き
        piano_arp(S, CH['harp'], ch, range(0, 12), vel=64)
        piano_pulse(S, CH['harp'], ch, range(20, 28), vel=80)
        S.mel(CH['solo'], 28, "F#6/2 E6/1 C#6/1 D6/2 F#6/2", 92)
    return stage('hasedo', 164, 5, ch, thA, thB, ost, tk=47, solo='violin', intro=intro, extra=extra, vo=dict(harp='piano'),
                 tkvel=(96, 102, 106, 114))

# ---------- ステージ6「天下分け目の夕刻」嬰ヘ短調172 : 決戦 ----------
def tenka():
    Fm, D, A, E, Cs, B, Bm = ('F#','m'), ('D','M'), ('A','M'), ('E','M'), ('C#','M'), ('B','m'), ('B','m')
    ch = prog32([(4, [Fm, Fm, D, Cs]), (8, [Fm, D, A, E, Fm, D, B, Cs]), (8, [D, A, E, Fm, D, A, B, Cs]),
                 (8, [Fm, D, A, E, Fm, D, B, Cs]), (4, [D, E, Fm, Cs])])
    thA = ["F#5/1 A5/1 C#6/1.5 B5/.5", "A5/1.5 F#5/.5 D6/2", "E6/1 C#6/1 A5/1 C#6/1", "B5/1.5 C#6/.5 E#6/2",
           "F#6/1.5 F#6/.5 A6/1 C#7/1", "B6/1.5 A6/.5 F#6/2", "D6/1 F#6/1 B6/1 D7/1", "C#7/3 E#6/1"]
    thB = ["A5/1 C#6/1 E6/2", "E6/1 A6/1 C#7/2", "B6/1.5 A6/.5 G#6/1 E6/1", "F#6/1 A6/1 C#7/2",
           "F#6/.5 A6/.5 D7/1 C#7/1 A6/1", "E6/.5 A6/.5 C#7/1 B6/1 G#6/1", "D6/1 F#6/1 B6/2", "C#7/.5 B6/.5 A6/.5 G#6/.5 F#6/1 E#6/1"]
    ost = [[0, 2, 3, 4, 3, 2, 3, 2] * 2, [0, 2, 3, 4, 3, 2, 3, 2] * 2,
           ['0>', 2, 3, 4, '3>', 2, 3, 2, '0>', 2, 3, 4, '3>', 2, 3, 2],
           ['0>', 2, 3, '4>', '3>', 2, 3, '4>', '0>', 2, 3, '4>', '3>', 4, '3>', '4>']]
    intro = [(0, "F#5/2 A5/1 G#5/1 F#5/3 r/1", 94), (2, "C#6/2 B5/1 A5/1 G#5/3 E#5/1", 94)]
    def extra(S, ch):                                      # 決戦: ピアノの重い8分+ヴァイオリンの高いトレモロ
        piano_arp(S, CH['harp'], ch, range(4, 12), vel=62)
        piano_pulse(S, CH['harp'], ch, range(20, 28), vel=88)
        for b in range(20, 28):
            S.note(CH['solo'], b * 4, 3.9, midi(ch[b][0] + '5') + 12, 66)
    return stage('tenka', 172, 6, ch, thA, thB, ost, tk=42, solo='tremolo', intro=intro, extra=extra,
                 vo=dict(harp='piano'), bedvel=(80, 84, 88, 96), tkvel=(100, 106, 110, 118))

# ---------- ボス戦 ハ短調176 : 鬼気迫る(半音の刻み・三全音・怒号の合唱) ----------
def boss():
    Cm, Db, Ab, G, Bb, Fm, Fd = ('C','m'), ('Db','M'), ('Ab','M'), ('G','M'), ('Bb','M'), ('F','m'), ('F#','dim')
    ch = prog32([(4, [Cm]), (8, [Cm, Cm, Db, Cm, Cm, Ab, G, G]), (8, [Ab, Bb, Cm, G, Ab, Bb, G, G]),
                 (8, [Cm, Cm, Db, Cm, Cm, Ab, G, G]), (4, [Ab, Bb, Fd, G])])
    S = Song('boss', 176, 32, seed=7)
    setup(S, solo='tremolo', harp='piano')
    sec = lambda b: 0 if b < 4 else 1 if b < 12 else 2 if b < 20 else 3 if b < 28 else 2
    chrom = [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, -1, 0, 1]
    for b in range(32):                                    # チェロ・コントラバス: 半音で這う16分
        r, q = ch[b]; base = midi(r + '2'); v = (78, 90, 96, 104)[sec(b)]
        for i, o in enumerate(chrom):
            S.note(CH['cello'], b * 4 + i * 0.25, 0.2, base + o + (12 if i % 8 == 7 else 0), v + (10 if i % 4 == 0 else 0))
        if b >= 4:
            for bt in (0, 1.5, 2, 3.5): S.note(CH['bass'], b * 4 + bt, 0.5, base - 12 + 12, 96)
        ostinato(S, CH['stac'], ch, [b], [0, None, 0, None, 2, None, 0, None] * 2 if b < 12 else ['0>', 0, 2, 0] * 4, octave=3, vel=(70, 80, 88, 96)[sec(b)])
    for b in range(32):                                    # タイコ16分+ティンパニ
        s = sec(b)
        for bt in range(4):
            S.note(CH['taiko'], b * 4 + bt, 0.45, 43, (92, 104, 108, 118)[s] + (8 if bt == 0 else 0))
            if s >= 1:
                S.note(CH['taiko'], b * 4 + bt + 0.5, 0.2, 43, 88)
                S.note(CH['taiko'], b * 4 + bt + 0.75, 0.2, 43, 80)
    timp_hits(S, ch, range(0, 32), [(0, .5, 'r', 112), (1.5, .4, 'r', 100), (2, .5, 'r', 108), (3.5, .4, 'f', 100)])
    thA = ["C5/.5 C5/.5 Eb5/.5 C5/.5 G5/1 F#5/1", "Eb5/.5 D5/.5 C5/1 G4/2", "Db5/.5 Db5/.5 F5/.5 Db5/.5 Ab5/1 G5/1", "Eb5/1 D5/1 C5/2",
           "C6/.5 C6/.5 Eb6/.5 C6/.5 G6/1 F#6/1", "Eb6/1 C6/1 Ab5/2", "D6/1 G5/1 B5/1 D6/1", "F6/.5 Eb6/.5 D6/.5 B5/.5 G5/2"]
    thB = ["Ab5/1 C6/1 Eb6/2", "Bb5/1 D6/1 F6/2", "C6/1 Eb6/1 G6/2", "B5/.5 D6/.5 G6/1 F6/1 D6/1",
           "Ab6/1.5 G6/.5 Eb6/1 C6/1", "Bb6/1.5 Ab6/.5 F6/1 D6/1", "Eb6/1 G6/1 C7/2", "B6/.5 D7/.5 G7/1 F7/1 D7/1"]
    for i, tx in enumerate(thA): S.mel(CH['horn'], 4 + i, tx, 104); S.mel(CH['tbn'], 4 + i, tx, 92, trans=-12)
    for i, tx in enumerate(thB):
        S.mel(CH['trp'], 12 + i, tx, 104); S.mel(CH['vln'], 12 + i, tx, 92); S.mel(CH['horn'], 12 + i, tx, 84, trans=-12)
    for i, tx in enumerate(thA):
        S.mel(CH['horn'], 20 + i, tx, 110); S.mel(CH['trp'], 20 + i, tx, 100, trans=12); S.mel(CH['vln'], 20 + i, tx, 96, trans=12)
        S.mel(CH['tbn'], 20 + i, tx, 96, trans=-12)
    for b in range(4, 32, 1):                              # 金管の刻み(裏拍)と怒号の合唱・オケヒット
        r, q = ch[b]
        if sec(b) >= 1:
            for bt in (1.5, 3.5):
                for p in chord(r, q, 3)[:3]: S.note(CH['hit'], b * 4 + bt, 0.35, p, 92)
    pad(S, CH['choir'], ch, range(12, 28), octave=4, vel=84, notes=(0, 1, 2), dur=1.8)
    for b in range(12, 28):
        for p in chord(ch[b][0], ch[b][1], 4)[:3]: S.note(CH['choir'], b * 4 + 2, 1.8, p, 88)
    piano_pulse(S, CH['harp'], ch, range(4, 32), vel=84, octave=1)
    for b in range(20, 28):
        for k in range(8): S.note(9, b * 4 + k * 0.5, 0.3, 38, 84 if k % 2 == 0 else 62)
    for b in (4, 12, 20, 28): crash(S, b, 112)
    for b in (3, 11, 19, 27, 31):
        n = 4 if b == 31 else 2; snare_roll(S, b, 56, 122, beats=n); fill_roll(S, CH['timp'], b, midi('C2'), 72, 122, beats=n); riser(S, b, 4, 88)
    for b0, b1, v0, v1 in ((0, 4, 104, 118), (8, 12, 108, 122), (16, 20, 110, 126), (24, 28, 114, 127)):
        for c in (CH['str'], CH['choir'], CH['horn'], CH['solo']): S.ramp(c, b0 * 4, b1 * 4, v0, v1)
    for b in range(4, 32): S.note(CH['solo'], b * 4, 3.9, midi(ch[b][0] + '5') + 12, 60)     # 高いトレモロ弦=悲鳴
    return S

# ---------- ラスボス ニ短調184 : 絶望の行進(パイプオルガン・鐘・合唱) ----------
def lastboss():
    Dm, Bb, A, Gm, C, Ed = ('D','m'), ('Bb','M'), ('A','M'), ('G','m'), ('C','M'), ('E','dim')
    ch = prog32([(4, [Dm]), (8, [Dm, Dm, Bb, Bb, Gm, A, Dm, A]), (8, [Bb, C, A, A, Bb, C, Ed, A]),
                 (8, [Dm, Dm, Bb, Bb, Gm, A, Dm, A]), (4, [Bb, C, A, A])])
    S = Song('lastboss', 184, 32, seed=9)
    setup(S, solo='organ', harp='bells', hit='hit')
    sec = lambda b: 0 if b < 4 else 1 if b < 12 else 2 if b < 20 else 3 if b < 28 else 2
    chrom = [0, 1, 0, -1, 0, 1, 0, -1, 0, 1, 0, 3, 2, 1, 0, -1]
    for b in range(32):
        r, q = ch[b]; base = midi(r + '2'); s = sec(b)
        for i, o in enumerate(chrom):
            S.note(CH['cello'], b * 4 + i * 0.25, 0.2, base + o, (84, 92, 98, 106)[s] + (10 if i % 4 == 0 else 0))
        S.note(CH['solo'], b * 4, 3.95, base, 78); S.note(CH['solo'], b * 4, 3.95, base + 12, 70)     # オルガンの低音ペダル
        ostinato(S, CH['stac'], ch, [b], ['0>', 0, 2, 3, '0>', 0, 2, 3, '0>', 2, 3, 2, '0>', 2, 3, '2>'], octave=3, vel=(72, 84, 92, 100)[s])
        S.note(CH['harp'], b * 4, 3.0, midi('D4'), 80); S.note(CH['harp'], b * 4 + 2, 2.0, midi('A4'), 70)  # 弔いの鐘
        for bt in range(4):                                 # 16分のタイコ+ティンパニ
            S.note(CH['taiko'], b * 4 + bt, 0.4, 38, (96, 106, 112, 120)[s] + (8 if bt == 0 else 0))
            for off, vv in ((0.25, 74), (0.5, 94), (0.75, 78)):
                if s >= 1: S.note(CH['taiko'], b * 4 + bt + off, 0.18, 38, vv)
            S.note(CH['timp'], b * 4 + bt, 0.4, midi(r + '2'), 108)
            if s >= 1: S.note(CH['timp'], b * 4 + bt + 0.5, 0.3, midi(r + '2'), 92)
        if b >= 4:
            for bt in (0, 1.5, 2.5, 3.5): S.note(CH['bass'], b * 4 + bt, 0.5, base - 12 + 12, 100)
    thA = ["D6/.5 D6/.5 F6/1 E6/1 D6/1", "C#6/.5 C#6/.5 E6/1 A5/2", "Bb5/.5 Bb5/.5 D6/1 F6/1 Bb6/1", "A6/.5 G6/.5 F6/.5 E6/.5 C#6/2",
           "G5/.5 G5/.5 Bb5/1 D6/1 G6/1", "E6/1 C#6/1 A5/2", "D6/1 F6/1 A6/1 D7/1", "C#7/1 A6/1 E6/1 C#6/1"]
    thB = ["Bb5/1 D6/1 F6/2", "C6/1 E6/1 G6/2", "A5/1 C#6/1 E6/2", "A6/.5 G6/.5 F6/.5 E6/.5 C#6/2",
           "Bb6/1.5 A6/.5 F6/1 D6/1", "C7/1.5 Bb6/.5 G6/1 E6/1", "E6/.5 G6/.5 Bb6/1 D7/1 G6/1", "A6/.5 C#7/.5 E7/1 D7/1 C#7/1"]
    for i, tx in enumerate(thA):
        S.mel(CH['horn'], 4 + i, tx, 104); S.mel(CH['tbn'], 4 + i, tx, 94, trans=-12)
    for i, tx in enumerate(thB):
        S.mel(CH['trp'], 12 + i, tx, 106); S.mel(CH['vln'], 12 + i, tx, 94); S.mel(CH['horn'], 12 + i, tx, 86, trans=-12)
    for i, tx in enumerate(thA):
        S.mel(CH['horn'], 20 + i, tx, 112); S.mel(CH['trp'], 20 + i, tx, 102, trans=12); S.mel(CH['vln'], 20 + i, tx, 98, trans=12)
        S.mel(CH['tbn'], 20 + i, tx, 100, trans=-12)
    for b in range(4, 32):
        r, q = ch[b]
        if sec(b) >= 1:
            for bt in (1.5, 3.5):
                for p in chord(r, q, 3)[:3]: S.note(CH['hit'], b * 4 + bt, 0.35, p, 96)
    pad(S, CH['choir'], ch, range(8, 28), octave=4, vel=86, dur=3.9)
    pad(S, CH['str'], ch, range(4, 32), octave=4, vel=66)
    for b in range(20, 28):
        for k in range(8): S.note(9, b * 4 + k * 0.5, 0.3, 38, 88 if k % 2 == 0 else 64)
    for b in (4, 12, 20, 28): crash(S, b, 114)
    for b in (3, 11, 19, 27, 31):
        n = 4 if b == 31 else 2; snare_roll(S, b, 58, 124, beats=n); riser(S, b, 4, 92)
    for b0, b1, v0, v1 in ((0, 4, 106, 120), (8, 12, 108, 124), (16, 20, 110, 127), (24, 28, 114, 127)):
        for c in (CH['str'], CH['choir'], CH['horn']): S.ramp(c, b0 * 4, b1 * 4, v0, v1)
    return S

# ---------- エンディング ニ長調84 : 戦いのあとの静かな夜明け ----------
def ending():
    D, A, Bm, Fm, G, Em = ('D','M'), ('A','M'), ('B','m'), ('F#','m'), ('G','M'), ('E','m')
    ch = prog32([(4, [D, A, Bm, G]), (8, [D, A, Bm, Fm, G, D, Em, A]), (8, [Bm, Fm, G, D, Em, D, G, A]), (4, [G, A, D, D])])
    S = Song('ending', 84, 24, seed=11)
    setup(S, solo='shaku', harp='piano', vln='violin')
    piano_arp(S, CH['harp'], ch, range(0, 24), vel=62, octave=3)
    pad(S, CH['str'], ch, range(0, 24), octave=3, vel=58, notes=(0, 1, 2, 3))
    root_line(S, CH['cello'], ch, range(4, 24), [(0, 2, 'r'), (2, 2, 'f')], octave=2, vel=78)
    root_line(S, CH['bass'], ch, range(4, 24), [(0, 4, 'r')], octave=1, vel=84)
    melA = ["F#5/2 A5/1 B5/1", "C#6/2 A5/1 E5/1", "D6/2 B5/1 D6/1", "C#6/3 A5/1", "B5/2 D6/1 G6/1", "F#6/2 E6/1 D6/1", "E6/2 B5/1 G5/1", "A5/3 r/1"]
    melB = ["D6/1.5 F#6/.5 B6/2", "A6/1.5 F#6/.5 C#6/2", "B6/1.5 G6/.5 D6/2", "F#6/2 A6/2", "G6/1.5 B6/.5 E7/2", "D7/1.5 A6/.5 F#6/2", "G6/1 B6/1 D7/2", "C#7/2 E7/1 A6/1"]
    melC = ["B5/2 D6/2", "C#6/2 E6/2", "F#6/2 A6/2", "D6/4"]
    for i, tx in enumerate(melA): S.mel(CH['solo'], 4 + i, tx, 84); S.mel(CH['harp'], 4 + i, tx, 56, trans=0)
    for i, tx in enumerate(melB):
        S.mel(CH['vln'], 12 + i, tx, 92); S.mel(CH['horn'], 12 + i, tx, 80, trans=-12); S.mel(CH['solo'], 12 + i, tx, 70, trans=0)
    for i, tx in enumerate(melC): S.mel(CH['horn'], 20 + i, tx, 84, trans=-12); S.mel(CH['vln'], 20 + i, tx, 84)
    S.mel(CH['vln'], 0, "F#5/4 A5/4 B5/4 D6/4", 66)
    pad(S, CH['choir'], ch, range(12, 24), octave=4, vel=70)
    for b in (4, 12, 20): S.note(CH['timp'], b * 4, 3.5, midi(ch[b][0] + '2'), 90)
    for b in range(12, 20):
        S.note(CH['timp'], b * 4, 0.6, midi(ch[b][0] + '2'), 84); S.note(CH['timp'], b * 4 + 2, 0.6, midi(ch[b][0] + '2'), 76)
    fill_roll(S, CH['timp'], 19, midi('A2'), 50, 110, beats=4, step=0.25)
    crash(S, 12, 80); crash(S, 20, 70)
    for b0, b1, v0, v1 in ((0, 4, 84, 100), (8, 12, 96, 112), (16, 20, 104, 127), (20, 24, 122, 86)):
        for c in (CH['str'], CH['choir'], CH['horn']): S.ramp(c, b0 * 4, b1 * 4, v0, v1)
    return S

SONGS = dict(boss=boss, lastboss=lastboss, ending=ending, matsuo=matsuo, sasao=sasao, ueda=ueda, hasedo=hasedo, tenka=tenka)

if __name__ == '__main__':
    names = list(SONGS) if sys.argv[1] == 'all' else sys.argv[1:]
    for n in names:
        S = SONGS[n]()
        dur = render(S, os.path.join(OUT, f'bgm_{n}.mp3'))
        print(n, 'loop', round(dur, 1), 's', os.path.getsize(os.path.join(OUT, f'bgm_{n}.mp3')) // 1024, 'KB')

"""曲づくりの部品。疾走感の核は「ギャロップ(8分+16分2つ)」「16分の弦の刻み」「前へ進むタイコ」。"""
from engine import *

# チャンネル割り当て(GM音色)
CH = dict(str=0, stac=1, cello=2, bass=3, horn=4, trp=5, tbn=6, choir=7, timp=8, taiko=10, solo=11,
          harp=12, hit=13, vln=14, fx=15)
GM = dict(strings=48, strings2=49, tremolo=44, pizz=45, violin=40, viola=41, cello=42, bass=43, harp=46,
          timp=47, hit=55, horn=60, brass=61, trumpet=56, tbn=57, tuba=58, choir=52, oohs=53, synvox=54,
          flute=73, shaku=77, koto=107, shami=106, taiko=116, mtom=117, revcym=119, organ=19, bells=14,
          piano=0, bright=1, pipe=72, oboe=68, bassoon=70, clar=71, sbrass=62, glock=9, celesta=8)

def setup(S, **over):
    """標準の編成。over で音色を差し替え: setup(S, solo='shaku')"""
    P = dict(str='strings', stac='strings2', cello='cello', bass='bass', horn='horn', trp='trumpet', tbn='tbn',
             choir='choir', timp='timp', taiko='taiko', solo='shaku', harp='harp', hit='hit', vln='violin', fx='revcym')
    P.update(over)
    V = dict(str=88, stac=92, cello=100, bass=102, horn=108, trp=100, tbn=100, choir=84, timp=112, taiko=118,
             solo=96, harp=84, hit=96, vln=90, fx=90)
    PAN = dict(str=52, stac=80, cello=40, bass=64, horn=46, trp=82, tbn=60, choir=64, timp=64, taiko=64,
               solo=72, harp=94, hit=64, vln=30, fx=64)
    REV = dict(str=70, stac=45, cello=55, bass=30, horn=75, trp=70, tbn=60, choir=95, timp=60, taiko=65,
               solo=85, harp=90, hit=80, vln=75, fx=80)
    for k, c in CH.items():
        S.prog(c, GM[P[k]], V[k], PAN[k], REV[k])
    S.prog(9, 48, 100, 64, 70, bank=0)       # オーケストラキット(シンバル・小太鼓)

def bar_range(a, b):
    return range(a, b)

def pad(S, ch, chords, bars, octave=3, vel=70, notes=(0, 1, 2), dur=3.9, swell=None):
    for b in bars:
        r, q = chords[b]
        tones = chord(r, q, octave)
        for i in notes:
            S.note(ch, b * 4, dur, tones[i % len(tones)] + 12 * (i // len(tones)), vel)

def ostinato(S, ch, chords, bars, pattern, octave=3, vel=80, acc=14, gate=0.8, step=0.25):
    """pattern: 16個(1小節=16分×16)。None=休み、数字=コード音の番号(0根音,1三度,2五度,3オクターブ,4=十度...)。
    '>' を付けた文字列 '2>' はアクセント"""
    for b in bars:
        r, q = chords[b]
        tones = chord(r, q, octave)
        ext = tones + [tones[0] + 12, tones[1] + 12, tones[2] + 12]
        for i, p in enumerate(pattern):
            if p is None: continue
            a = isinstance(p, str)
            idx = int(p[:-1]) if a else p
            S.note(ch, b * 4 + i * step, step * gate, ext[idx], vel + (acc if a else 0))

def root_line(S, ch, chords, bars, rhythm, octave=2, vel=100, gate=0.9):
    """rhythm: [(拍位置, 長さ, 度数 'r'根音/'5'五度/'o'オクターブ/'b'短三度...)]"""
    iv = dict(r=0, f=7, o=12, t=3, T=4, n=10)
    for b in bars:
        r, q = chords[b]
        base = midi(r + str(octave))
        for (pos, d, k) in rhythm:
            S.note(ch, b * 4 + pos, d * gate, base + iv[k], vel)

def gallop_bar(S, ch, bar, pitch, vel=100, beats=(0, 1, 2, 3), accent=0):
    for bt in beats:
        S.note(ch, bar * 4 + bt, 0.45, pitch, vel + (8 if bt == accent else 0))
        S.note(ch, bar * 4 + bt + 0.5, 0.22, pitch, vel - 14)
        S.note(ch, bar * 4 + bt + 0.75, 0.22, pitch, vel - 8)

def fill_roll(S, ch, bar, pitch, v0=60, v1=120, beats=4, step=0.25):
    n = int(beats / step)
    for i in range(n):
        S.note(ch, bar * 4 + (4 - beats) + i * step, step * 0.95, pitch, int(v0 + (v1 - v0) * i / n), hum=False)

def snare_roll(S, bar, v0=50, v1=118, beats=4, step=0.25, note=38):
    n = int(beats / step)
    for i in range(n):
        S.note(9, bar * 4 + (4 - beats) + i * step, step * 0.9, note, int(v0 + (v1 - v0) * i / n), hum=False)

def crash(S, bar, vel=110, beat=0):
    S.note(9, bar * 4 + beat, 3.0, 49, vel, hum=False)

def riser(S, bar, beats=4, vel=100):
    """逆回しシンバルで直前から持ち上げる"""
    S.note(CH['fx'], bar * 4 + 4 - beats, beats, 60, vel, hum=False)

def timp_hits(S, chords, bars, pat, octave=2, vel=105):
    for b in bars:
        r, q = chords[b]
        base = midi(r + str(octave))
        for (pos, d, k, v) in pat:
            S.note(CH['timp'], b * 4 + pos, d, base + {'r': 0, 'f': 7, 'o': 12}[k], v if v else vel)

def taiko_pat(S, bars, pat):
    """pat: [(拍位置, 音高MIDI, 強さ, 長さ)]"""
    for b in bars:
        for (pos, p, v, d) in pat:
            S.note(CH['taiko'], b * 4 + pos, d, p, v)

def check_scale(chords_scale, notes):
    pass


def piano_pulse(S, ch, chords, bars, vel=84, octave=2, stab=True):
    """ピアノ: 左手のオクターブ8分(前へ進む推進力)+小節頭の和音"""
    for b in bars:
        r, q = chords[b]; base = midi(r + str(octave))
        for i in range(8):
            v = vel + (8 if i % 2 == 0 else -6)
            S.note(ch, b * 4 + i * 0.5, 0.42, base, v); S.note(ch, b * 4 + i * 0.5, 0.42, base + 12, v - 8)
        if stab:
            for p in chord(r, q, octave + 2)[:3]: S.note(ch, b * 4, 0.9, p, vel + 6)

def piano_arp(S, ch, chords, bars, vel=70, octave=3, step=0.5):
    """ピアノ: 分散和音(根・五・オクターブ・十度…の上昇下降)"""
    for b in bars:
        r, q = chords[b]; t = chord(r, q, octave); seq = [t[0], t[1], t[2], t[0] + 12, t[2], t[1], t[2], t[0] + 12]
        for i, p in enumerate(seq):
            S.note(ch, b * 4 + i * step, step * 1.6, p, vel + (6 if i % 4 == 0 else 0))

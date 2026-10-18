"""勝利のファンファーレ(勝鬨のあと)。ドラムロール→シンバルと同時に吹奏楽で勝利の旋律→最後の一撃。
ループしない1回きりの曲なので、尾(残響)まで残して書き出す。ギター系は使わない(engine が禁止)。
使い方: python3 fanfare.py <出力mp3>"""
import sys, os, wave, subprocess
import numpy as np
from engine import Song, midi, chord, wavwrite, SF2
from kit import CH, setup, crash

BPM = 126

def build():
    S = Song('fanfare', BPM, 6, seed=21)
    setup(S, solo='flute', vln='clar', bass='tuba', harp='glock')
    SN, BD = 38, 36
    # 小節0: 小太鼓のロール(32分)とティンパニのロールで盛り上げる
    for i in range(32):
        S.note(9, i * 0.125, 0.12, SN, int(34 + 86 * i / 31), hum=False)
    for i in range(16):
        S.note(CH['timp'], i * 0.25, 0.24, midi('F2'), int(40 + 80 * i / 15), hum=False)
    S.note(CH['fx'], 0, 4, midi('C5'), 92)                     # 逆回しシンバルで持ち上げ
    # 旋律(変ロ長調)。和音は2拍ごと
    mel = ["Bb4/.5 Bb4/.25 Bb4/.25 F5/1 D5/.5 F5/.5 Bb5/1",
           "A5/.5 G5/.5 F5/.5 Eb5/.5 D5/.75 Eb5/.25 F5/1",
           "G5/.5 A5/.5 Bb5/.5 C6/.5 F6/1 C6/1",
           "D6/2 r/2"]
    chords = [(('Bb', 'M'), ('Bb', 'M')), (('F', 'M'), ('Bb', 'M')), (('Eb', 'M'), ('F', 'M')), (('Bb', 'M'), ('Bb', 'M'))]
    for k, tx in enumerate(mel):
        bar = 1 + k
        S.mel(CH['trp'], bar, tx, 112)                         # トランペット
        S.mel(CH['solo'], bar, tx, 82, trans=12)               # フルート(1オクターブ上)
        S.mel(CH['vln'], bar, tx, 86)                          # クラリネット
        # ホルン・トロンボーン: 旋律の音ごとに、その下の和音の音を重ねる(吹奏楽の厚み)
        b = bar * 4.0
        for tok in tx.split():
            nm, d = tok.split('/'); d = float(d)
            if nm != 'r':
                p = midi(nm); (r, q) = chords[k][0 if b - bar * 4 < 2 else 1]
                tones = sorted({t + 12 * o for t in chord(r, q, 3) for o in range(0, 3)})
                below = [t for t in tones if t < p - 2][-2:]
                for t in below: S.note(CH['horn'], b, d * 0.95, t, 96)
                S.note(CH['tbn'], b, d * 0.95, chord(r, q, 3)[0] if d >= 0.5 else chord(r, q, 3)[2], 92)
            b += d
        for half in (0, 1):
            r, q = chords[k][half]
            S.note(CH['bass'], bar * 4 + half * 2, 1.9, midi(r + '1') if r != 'Bb' else midi('Bb1'), 104)
            S.note(CH['timp'], bar * 4 + half * 2, 0.5, midi((r if r in ('Bb', 'F') else 'F') + '2'), 100)
        # 小太鼓の行進リズムと大太鼓
        if k < 3:
            for pos, v in ((0, 100), (1, 70), (1.5, 76), (2, 96), (3, 72), (3.25, 64), (3.5, 82)):
                S.note(9, bar * 4 + pos, 0.2, SN, v, hum=False)
            for pos in (0, 2): S.note(9, bar * 4 + pos, 0.4, BD, 104, hum=False)
    crash(S, 1, 120); crash(S, 4, 112)
    # 小節4: 最後の和音を伸ばしながらティンパニとロール、小節4の3拍目で「ジャン！」
    for i in range(16):
        S.note(CH['timp'], 16 + i * 0.125, 0.12, midi('Bb2'), int(70 + 50 * i / 15), hum=False)
        S.note(9, 16 + i * 0.125, 0.1, SN, int(50 + 64 * i / 15), hum=False)
    for t in chord('Bb', 'M', 3) + chord('Bb', 'M', 4): S.note(CH['horn'], 16, 1.9, t, 100)
    for t in chord('Bb', 'M', 2): S.note(CH['tbn'], 16, 1.9, t, 100)
    S.note(CH['bass'], 16, 1.9, midi('Bb1'), 108)
    for c, ps in ((CH['trp'], ('Bb4', 'D5', 'F5', 'Bb5')), (CH['horn'], ('F3', 'Bb3', 'D4', 'F4')), (CH['tbn'], ('Bb2', 'F3', 'D3')),
                  (CH['bass'], ('Bb1',)), (CH['solo'], ('Bb6',)), (CH['vln'], ('D5',)), (CH['timp'], ('Bb2',))):
        for p in ps: S.note(c, 18, 0.7, midi(p), 124)
    crash(S, 4, 127, beat=2); S.note(9, 18, 0.5, BD, 124, hum=False)
    return S

def render_once(S, out, tail=2.0, target_lufs=-12.5):
    mid, wav = out + '.mid', out + '.wav'
    S.write(mid, loops=1, tail_beats=8)
    subprocess.run(['fluidsynth', '-ni', '-g', '0.9', '-r', '44100', '-o', 'synth.reverb.room-size=0.85',
                    '-o', 'synth.reverb.level=0.7', '-o', 'synth.polyphony=512', '-F', wav, SF2, mid], check=True, capture_output=True)
    with wave.open(wav) as w:
        sr, n = w.getframerate(), w.getnframes()
        a = np.frombuffer(w.readframes(n), dtype=np.int16).reshape(-1, 2).astype(np.float32) / 32768
    end = int((18 * 60 / BPM + tail) * sr)                 # 最後の一撃から残響 tail 秒まで
    a = a[:end]
    f = int(0.8 * sr); a[-f:] *= np.linspace(1, 0, f)[:, None] ** 2
    tmp = out + '.tmp.wav'; wavwrite(tmp, a, sr)
    r = subprocess.run(['ffmpeg', '-nostats', '-i', tmp, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    lufs = float([l for l in r.splitlines() if ' I:' in l][-1].split()[1])
    a = a * 10 ** ((target_lufs - lufs) / 20)
    a = np.where(np.abs(a) > 0.7, np.sign(a) * (0.7 + 0.19 * np.tanh((np.abs(a) - 0.7) / 0.19)), a).astype(np.float32)
    wavwrite(tmp, a, sr)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-c:a', 'libmp3lame', '-b:a', '128k', out], check=True)
    for x in (mid, wav, tmp): os.remove(x)
    return len(a) / sr

if __name__ == '__main__':
    print(round(render_once(build(), sys.argv[1]), 2), 's')

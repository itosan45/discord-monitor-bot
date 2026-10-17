"""BGM作曲エンジン: 小さなDSLで曲をMIDIに書き、fluidsynth(FluidR3_GM)で演奏、
ループが切れ目なくつながるよう切り出して mp3 にする。
使い方: python3 songs.py <曲名|all>   → ../../../gfx/bgm_<曲名>.mp3
"""
import mido, random, subprocess, os, re, math, struct, wave
import numpy as np

PPQ = 480
SF2 = '/usr/share/sounds/sf2/FluidR3_GM.sf2'
NOTE = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}

def midi(name):
    """'D4' 'F#3' 'Bb2' -> MIDI番号"""
    m = re.fullmatch(r'([A-G])([#b]?)(-?\d)', name)
    n = NOTE[m.group(1)] + (1 if m.group(2) == '#' else -1 if m.group(2) == 'b' else 0)
    return 12 * (int(m.group(3)) + 1) + n

QUAL = {'M':(0,4,7), 'm':(0,3,7), '5':(0,7,12), 'dim':(0,3,6), 'sus2':(0,2,7), 'sus4':(0,5,7),
        '7':(0,4,7,10), 'm7':(0,3,7,10), 'aug':(0,4,8), 'm6':(0,3,7,9), 'M7':(0,4,7,11)}

def chord(root, q, octave):
    """コードの構成音(根音は octave)。root は 'D' 'Bb' 'F#' のように音名のみ"""
    r = midi(root + str(octave))
    return [r + i for i in QUAL[q]]

class Song:
    def __init__(self, name, bpm, bars, seed=1):
        self.name, self.bpm, self.bars = name, bpm, bars
        self.ev = []            # (tick, order, msg)
        self.rng = random.Random(seed)
        self.chmap = {}
        # 各楽器の実用上限(MIDI番号)。超える旋律の音は1オクターブ下げる(音源が不自然な高音になるのを防ぐ)
        self.maxp = {4: 89, 5: 96, 6: 76, 11: 98, 14: 100}

    # --- 低レベル ---
    def prog(self, ch, program, vol=100, pan=64, rev=60, bank=0):
        if 24 <= program <= 31 or program in (120,):   # ギター系(アコースティック・エレキ・歪み)は使わない方針
            raise SystemExit('ギター系の音色は使用禁止: program=%d' % program)
        self.chmap[ch] = program
        self.ev.append((0, 0, mido.Message('control_change', channel=ch, control=0, value=bank)))
        if ch != 9:
            self.ev.append((0, 1, mido.Message('program_change', channel=ch, program=program)))
        else:
            self.ev.append((0, 1, mido.Message('program_change', channel=9, program=program)))
        for c, v in ((7, vol), (10, pan), (91, rev), (93, 0), (11, 127)):
            self.ev.append((0, 2, mido.Message('control_change', channel=ch, control=c, value=v)))

    def t(self, beat):
        return int(round(beat * PPQ))

    def note(self, ch, beat, dur, pitch, vel=90, hum=True):
        if beat < 0 or beat >= self.bars * 4:
            return
        j = self.rng.randint(-5, 5) if (hum and ch != 9) else 0
        v = max(1, min(127, vel + (self.rng.randint(-4, 4) if hum else 0)))
        on = max(0, self.t(beat) + j)
        off = on + max(10, self.t(dur) - 6)
        self.ev.append((on, 5, mido.Message('note_on', channel=ch, note=int(pitch), velocity=v)))
        self.ev.append((off, 4, mido.Message('note_off', channel=ch, note=int(pitch), velocity=0)))

    def cc(self, ch, beat, ctrl, val):
        self.ev.append((self.t(beat), 3, mido.Message('control_change', channel=ch, control=ctrl, value=int(max(0, min(127, val))))))

    def ramp(self, ch, b0, b1, v0, v1, ctrl=11, step=0.5):
        """表現(CC11)の直線変化。クレッシェンドなどに使う"""
        n = max(1, int((b1 - b0) / step))
        for i in range(n + 1):
            self.cc(ch, b0 + (b1 - b0) * i / n, ctrl, v0 + (v1 - v0) * i / n)

    # --- 旋律: "D5/1 F5/.5 r/.5 ..." ---
    def mel(self, ch, bar, text, vel=95, legato=0.96, trans=0):
        b = bar * 4.0
        for tok in text.split():
            nm, d = tok.split('/')
            d = float(d)
            if nm != 'r':
                p = midi(nm) + trans
                while ch in self.maxp and p > self.maxp[ch]: p -= 12
                self.note(ch, b, d * legato, p, vel)
            b += d
        return b / 4.0

    def hit(self, ch, beat, pitch, vel=100, dur=0.25):
        self.note(ch, beat, dur, pitch, vel)

    # --- 書き出し ---
    def write(self, path, loops=2, tail_beats=16):
        mid = mido.MidiFile(ticks_per_beat=PPQ)
        tr = mido.MidiTrack(); mid.tracks.append(tr)
        tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(self.bpm), time=0))
        total = self.bars * 4 * PPQ
        evs = []
        for k in range(loops):
            for (tk, od, m) in self.ev:
                if od <= 2 and k > 0:
                    continue
                evs.append((tk + k * total, od, m))
        evs.sort(key=lambda e: (e[0], e[1]))
        last = 0
        for tk, od, m in evs:
            tr.append(m.copy(time=tk - last)); last = tk
        # 最後に尾(リバーブ)用の余白
        tr.append(mido.MetaMessage('end_of_track', time=tail_beats * PPQ))
        mid.save(path)

def wavwrite(path, a, sr):
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((np.clip(a, -1, 1) * 32767).astype('<i2').tobytes())

def render(song, out_mp3, loops=2, bitrate='128k', gain_db=0.0, target_lufs=-13.5):
    d = os.path.dirname(out_mp3) or '.'
    mid = out_mp3 + '.mid'; wav = out_mp3 + '.wav'
    song.write(mid, loops=loops)
    subprocess.run(['fluidsynth', '-ni', '-g', '0.9', '-r', '44100',
                    '-o', 'synth.reverb.room-size=0.9', '-o', 'synth.reverb.damp=0.25',
                    '-o', 'synth.reverb.width=1.0', '-o', 'synth.reverb.level=0.75',
                    '-o', 'synth.chorus.level=1.2', '-o', 'synth.polyphony=512',
                    '-F', wav, SF2, mid], check=True, capture_output=True)
    with wave.open(wav) as w:
        sr, n, ch = w.getframerate(), w.getnframes(), w.getnchannels()
        a = np.frombuffer(w.readframes(n), dtype=np.int16).reshape(-1, ch).astype(np.float32) / 32768
    L = int(round(song.bars * 4 * 60.0 / song.bpm * sr))
    seg = a[L:2 * L] if loops >= 2 else a[:L]     # 2周目 = 1周目の尾が重なった定常状態
    # 音量をオーナーの既存曲(約-13.5 LUFS)にそろえる: ffmpeg で測ってゲインをかけ、天井だけ軽くリミット
    tmp = out_mp3 + '.tmp.wav'
    wavwrite(tmp, seg, sr)
    r = subprocess.run(['ffmpeg', '-nostats', '-i', tmp, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    lufs = float([l for l in r.splitlines() if ' I:' in l][-1].split()[1])
    os.remove(tmp)
    seg = seg * 10 ** ((target_lufs - lufs + gain_db) / 20.0)
    ceil = 0.89
    over = np.abs(seg) > 0.7
    seg = np.where(over, np.sign(seg) * (0.7 + (ceil - 0.7) * np.tanh((np.abs(seg) - 0.7) / (ceil - 0.7))), seg).astype(np.float32)
    raw = out_mp3 + '.f32'
    seg.astype('<f4').tofile(raw)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'f32le', '-ar', str(sr), '-ac', '2', '-i', raw,
                    '-af', 'highpass=f=28', '-c:a', 'libmp3lame', '-b:a', bitrate, out_mp3], check=True)
    for f in (mid, wav, raw):
        try: os.remove(f)
        except OSError: pass
    return L / sr

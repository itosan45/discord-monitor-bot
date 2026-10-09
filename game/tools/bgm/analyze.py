"""BGMの検査: 音量(LUFS)・ピーク・帯域バランス・ループ継ぎ目・時間ごとの音量推移を出す。
python3 analyze.py a.mp3 [b.mp3 ...]  (--png で時間-周波数の図も出す)"""
import sys, subprocess, numpy as np, wave, os, tempfile

def load(p):
    t = tempfile.mktemp(suffix='.wav')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', p, '-ac', '2', '-ar', '44100', t], check=True)
    with wave.open(t) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).reshape(-1, 2).astype(np.float32) / 32768
    os.remove(t); return a

def lufs(p):
    r = subprocess.run(['ffmpeg', '-nostats', '-i', p, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    I = [l for l in r.splitlines() if ' I:' in l][-1].split()[1]
    pk = [l for l in r.splitlines() if 'Peak:' in l][-1].split()[1]
    return float(I), float(pk)

def bands(a):
    m = a.mean(1); n = len(m) // 4096 * 4096
    F = np.abs(np.fft.rfft(m[:n].reshape(-1, 4096) * np.hanning(4096), axis=1)) ** 2
    f = np.fft.rfftfreq(4096, 1 / 44100); tot = F.sum()
    edges = [(30, 120, '低'), (120, 500, '中低'), (500, 2000, '中'), (2000, 6000, '中高'), (6000, 16000, '高')]
    return {nm: round(100 * F[:, (f >= lo) & (f < hi)].sum() / tot, 1) for lo, hi, nm in edges}

def seam(a):
    """ループ継ぎ目: 末尾→先頭の波形の飛び vs 通常の隣り合うサンプル差、および前後100msの音量比"""
    jump = np.abs(a[0] - a[-1]).max(); typ = np.abs(np.diff(a, axis=0)).mean() * 6
    n = 4410
    return round(float(jump), 4), round(float(typ), 4), round(float(np.sqrt((a[:n] ** 2).mean()) / (np.sqrt((a[-n:] ** 2).mean()) + 1e-9)), 2)

def curve(a, step=4):
    sr = 44100; n = int(sr * step)
    return [round(20 * np.log10(np.sqrt((a[i:i + n] ** 2).mean()) + 1e-9), 1) for i in range(0, len(a) - n + 1, n)]

if __name__ == '__main__':
    for p in [x for x in sys.argv[1:] if not x.startswith('--')]:
        a = load(p); I, pk = lufs(p)
        print(os.path.basename(p), f'{len(a)/44100:.1f}s', f'{I} LUFS', f'peak {pk}dBTP', bands(a), 'seam', seam(a))
        print('   音量推移(dB/4秒):', curve(a))
        if '--png' in sys.argv:
            import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
            m = a.mean(1); plt.figure(figsize=(12, 4)); plt.specgram(m, NFFT=2048, Fs=44100, noverlap=1024, cmap='magma', vmin=-110)
            plt.ylim(0, 8000); plt.savefig(p + '.png', dpi=70, bbox_inches='tight')

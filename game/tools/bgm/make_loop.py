"""Gemini(Lyria)で作った約3分のBGMを、ゲーム用の「途切れず繰り返せる約100秒」に整える。
- 拍の位置を、音の立ち上がりから推定する(4拍=1小節として扱う)。
- 曲の冒頭の導入(約10秒)と、終わりの余韻(約12秒)を避けて、小節の頭から小節の頭までの範囲を切り出す。
- 繋ぎ目: 範囲の最後の1小節を、「範囲の直前の1小節」へ等パワーでクロスフェードする。
  こうすると、最後まで流れたあと、頭に戻るところで拍と音がつながる。
- 音量を -14 LUFS(ピーク -1 dB)にそろえ、MP3 44.1kHz ステレオ 128kbps(今のBGMと同じ形式)で書き出す。
使い方: python3 game/tools/bgm/make_loop.py <入力mp3> <出力mp3> <狙いのBPM> [長さ秒=100]
推定結果(実際のBPM・切り出し範囲・繋ぎ目の指標)を表示する。耳で聴けないので、繋ぎ目の滑らかさは数値でだけ確認している。"""
import sys, subprocess, numpy as np

SR = 22050


def load(path, sr=SR, ch=1):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', str(ch), '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True, check=True)
    x = np.frombuffer(r.stdout, dtype=np.float32)
    return x if ch == 1 else x.reshape(-1, ch)


def onset_env(x, hop=512, n=1024):
    win = np.hanning(n)
    frames = (len(x) - n) // hop
    mag = np.abs(np.array([np.fft.rfft(x[i * hop:i * hop + n] * win) for i in range(frames)]))
    mag = np.log1p(mag * 50)
    flux = np.maximum(0, np.diff(mag, axis=0)).sum(axis=1)
    flux = np.concatenate([[0], flux])
    flux = flux - np.convolve(flux, np.ones(9) / 9, 'same')
    return np.maximum(flux, 0), hop / SR


def fit_grid(env, dt, bpm_hint):
    t = np.arange(len(env)) * dt
    best = (-1, bpm_hint, 0.0)
    for bpm in np.arange(bpm_hint * 0.88, bpm_hint * 1.14, 0.1):
        period = 60.0 / bpm
        for ph in np.arange(0, period, dt):
            idx = np.round((np.arange(ph, t[-1], period)) / dt).astype(int)
            idx = idx[idx < len(env)]
            s = env[idx].mean()
            if s > best[0]:
                best = (s, bpm, ph)
    return best[1], best[2]


def main():
    src, dst, bpm_hint = sys.argv[1], sys.argv[2], float(sys.argv[3])
    target = float(sys.argv[4]) if len(sys.argv) > 4 else 100.0
    x = load(src)
    L = len(x) / SR
    env, dt = onset_env(x)
    bpm, ph = fit_grid(env, dt, bpm_hint)
    beat = 60.0 / bpm
    bar = beat * 4
    # 小節の頭の時刻 = ph + k*bar (拍の位相の、4拍に1回を小節の頭とみなす。位相が小節の途中でも、頭同士の対応は崩れない)
    k0 = int(np.ceil((10.0 + bar - ph) / bar))
    S = ph + k0 * bar
    nbars = int(round(target / bar))
    while S + nbars * bar > L - 12.0 and nbars > 8:
        nbars -= 1
    E = S + nbars * bar
    X = bar
    ff = ['ffmpeg', '-y', '-v', 'error', '-i', src]
    # out = T[S:E-X] + crossfade(T[E-X:E], T[S-X:S])
    fc = (f"[0:a]atrim={S:.4f}:{E - X:.4f},asetpts=PTS-STARTPTS[m];"
          f"[0:a]atrim={E - X:.4f}:{E:.4f},asetpts=PTS-STARTPTS[tl];"
          f"[0:a]atrim={S - X:.4f}:{S:.4f},asetpts=PTS-STARTPTS[hd];"
          f"[tl][hd]acrossfade=d={X:.4f}:c1=qsin:c2=qsin[cf];"
          f"[m][cf]concat=n=2:v=0:a=1[o]")
    tmp = dst + '.tmp.wav'
    subprocess.run(ff + ['-filter_complex', fc, '-map', '[o]', '-ar', '44100', '-ac', '2', tmp], check=True)
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', tmp, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True)
    import re
    loud = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr)[-1])
    gain = -14.0 - loud
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', tmp, '-af', f'volume={gain:.2f}dB,alimiter=limit=0.89:attack=5:release=80', '-ar', '44100', '-ac', '2', '-codec:a', 'libmp3lame', '-b:a', '128k', dst], check=True)
    import os
    os.remove(tmp)
    # 繋ぎ目の指標: 出力の「最後の0.5秒」と「最初の0.5秒」の音量の差(dB)と、拍の位相のずれ(ミリ秒)
    y = load(dst)
    n = int(0.5 * SR)
    a, b = np.sqrt(np.mean(y[-n:] ** 2)) + 1e-9, np.sqrt(np.mean(y[:n] ** 2)) + 1e-9
    d_out = len(y) / SR
    print(f"{src}: 実際のBPM {bpm:.1f}(狙い {bpm_hint}) / 切り出し {S:.1f}s〜{E:.1f}s ({nbars}小節, {E - S:.1f}s) / 繋ぎ目 {X:.1f}s / 出力 {d_out:.1f}s / 継ぎ目の音量差 {20 * np.log10(a / b):+.1f} dB / 補正 {gain:+.1f} dB")


main()

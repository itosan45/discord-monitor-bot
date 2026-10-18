"""声の元WAVを、ゲームに入れる直前の形(MP3 24kHz モノラル 64kbps)に整える。ゲーム本体・audio.json は触らない(音声担当の道具)。
整音: 前後の無音を除去・80Hz以下をカット・音量を -13 LUFS にそろえる(短い声は繰り返してから測る)・ピーク -1 dB。
使い方: python3 game/tools/make_voice_ready.py <元WAVのフォルダ> <出力フォルダ> [目標LUFS]"""
import os, sys, glob, re, subprocess, io, wave, tempfile

FF = os.environ.get('FFMPEG', 'ffmpeg')
TRIM = ("silenceremove=start_periods=1:start_duration=0.01:start_threshold=-42dB,areverse,"
        "silenceremove=start_periods=1:start_duration=0.01:start_threshold=-42dB,areverse,highpass=f=80")


def decode(src, af):
    r = subprocess.run([FF, '-v', 'error', '-i', src, '-af', af, '-ac', '1', '-ar', '24000', '-f', 'f32le', '-'], capture_output=True, check=True)
    return r.stdout


def lufs(pcm):
    # 0.4秒より短い声は ebur128 が測れないので、3秒ぶん繰り返して(ゲートされた)平均の大きさを測る
    n = len(pcm) // 4 or 1
    reps = max(1, int(3 * 24000 / n) + 1)
    r = subprocess.run([FF, '-hide_banner', '-nostats', '-f', 'f32le', '-ar', '24000', '-ac', '1', '-i', '-', '-af', 'ebur128', '-f', 'null', '-'], input=pcm * reps, capture_output=True)
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr.decode(errors='ignore'))[-1])


src_dir, out_dir = sys.argv[1], sys.argv[2]
target = float(sys.argv[3]) if len(sys.argv) > 3 else -13.0
os.makedirs(out_dir, exist_ok=True)
for f in sorted(glob.glob(os.path.join(src_dir, '*.wav'))):
    pcm = decode(f, TRIM)
    gain = target - lufs(pcm)
    mp3 = subprocess.run([FF, '-v', 'error', '-i', f, '-af', f"{TRIM},volume={gain:.2f}dB,alimiter=limit=0.89:attack=2:release=60", '-ac', '1', '-ar', '24000', '-b:a', '64k', '-f', 'mp3', '-'], capture_output=True, check=True).stdout
    out = os.path.join(out_dir, os.path.basename(f)[:-4] + '.mp3')
    open(out, 'wb').write(mp3)
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', out], capture_output=True, text=True).stdout)
    print(os.path.basename(out), '長さ', round(dur, 2), '秒 / 音量補正', round(gain, 1), 'dB')

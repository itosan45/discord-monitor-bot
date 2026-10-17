"""assets/voice/narration/opening_1..7.wav(オープニングのナレーション、Gemini生成)を整音して game/data/audio.json の nr / nrd に入れる。
nr: MP3(base64)7本。nrd: 各本の長さ(秒)。ゲームはこの長さで各カードの表示時間を決める(声が字幕より長ければカードを延ばす)。
整音: 前後の無音を除去(声の頭が0.05秒以内に始まる)、80Hz以下をカット、-16 LUFS にそろえる、ピーク -1 dB。
使い方: python3 game/tools/import_narration.py  → そのあと cd game && python3 build.py"""
import os, json, base64, subprocess, re, glob

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
V = os.path.join(R, 'assets', 'voice', 'narration')
J = os.path.join(R, 'game', 'data', 'audio.json')
FF = os.environ.get('FFMPEG', 'ffmpeg')
TARGET = -16.0
TRIM = ("silenceremove=start_periods=1:start_duration=0.02:start_threshold=-42dB,areverse,"
        "silenceremove=start_periods=1:start_duration=0.02:start_threshold=-42dB,areverse,highpass=f=80")


def loudness(af, src):
    r = subprocess.run([FF, '-hide_banner', '-i', src, '-af', af + ',ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True)
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr)[-1])


def encode(src):
    gain = TARGET - loudness(TRIM, src)
    af = f"{TRIM},volume={gain:.2f}dB,alimiter=limit=0.89:attack=2:release=60"
    mp3 = subprocess.run([FF, '-v', 'error', '-i', src, '-af', af, '-ac', '1', '-ar', '24000', '-b:a', '64k', '-f', 'mp3', '-'], capture_output=True, check=True).stdout
    tmp = os.path.join(os.environ.get('TEMP', '/tmp'), 'nr_probe.mp3')
    open(tmp, 'wb').write(mp3)
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', tmp], capture_output=True, text=True).stdout)
    return base64.b64encode(mp3).decode(), round(dur, 2), round(gain, 1)


files = sorted(glob.glob(os.path.join(V, 'opening_*.wav')), key=lambda p: int(re.findall(r'(\d+)\.wav$', p)[0]))
assert len(files) == 7, files
d = json.load(open(J))
nr, nrd = [], []
for f in files:
    b, dur, g = encode(f)
    nr.append(b); nrd.append(dur)
    print(os.path.basename(f), '長さ', dur, '秒 / 音量補正', g, 'dB')
d['nr'] = nr
d['nrd'] = nrd
json.dump(d, open(J, 'w'))
print('合計', round(sum(nrd), 1), '秒 / audio.json', os.path.getsize(J) // 1024, 'KB')

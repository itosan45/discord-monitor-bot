"""雑魚の死亡声(audio.json の dv.foot)の入れ替え。
- 元の foot_1・foot_2(声が低くてゾンビのように聞こえる。オーナー指示 2026-10-12)を外す。外した2本は assets/voice/old_vo/ に MP3 で残す。
- assets/voice/grunt_death/shi_*.wav(Gemini TTS で作った「ぐわー」「ぎゃああ」の断末魔)を整音して dv.foot に足す。
  整音: 前後の無音を除去・80Hz以下をカット・残す元の声(-14 LUFS 前後)と同じ音量にそろえる・ピーク -1 dB・MP3 24kHz 64kbps。
何度実行しても同じ結果になる(外す声は内容のハッシュで、足した声は dvn に控えたハッシュで見分ける)。
使い方: python3 game/tools/import_grunt_death.py  → そのあと cd game && python3 build.py"""
import os, json, base64, subprocess, re, glob, hashlib, statistics, tempfile

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
V = os.path.join(R, 'assets', 'voice', 'grunt_death')
OLD = os.path.join(R, 'assets', 'voice', 'old_vo')
J = os.path.join(R, 'game', 'data', 'audio.json')
FF = os.environ.get('FFMPEG', 'ffmpeg')
REMOVE = {'6da9ab56b81f': 'dv_foot_old_1.mp3', '6411bed900cf': 'dv_foot_old_2.mp3'}  # 元の foot_1, foot_2
TRIM = ("silenceremove=start_periods=1:start_duration=0.02:start_threshold=-42dB,areverse,"
        "silenceremove=start_periods=1:start_duration=0.02:start_threshold=-42dB,areverse,highpass=f=80")
sha = lambda b: hashlib.sha1(b.encode()).hexdigest()[:12]


def loud(af, src):
    r = subprocess.run([FF, '-hide_banner', '-i', src, '-af', af + ',ebur128', '-f', 'null', '-'], capture_output=True, text=True)
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr)[-1])


def tmpfile(b):
    p = os.path.join(tempfile.gettempdir(), 'gd_probe.mp3')
    open(p, 'wb').write(base64.b64decode(b))
    return p


def encode(src, target):
    gain = target - loud(TRIM, src)
    af = f"{TRIM},volume={gain:.2f}dB,alimiter=limit=0.89:attack=2:release=60"
    mp3 = subprocess.run([FF, '-v', 'error', '-i', src, '-af', af, '-ac', '1', '-ar', '24000', '-b:a', '64k', '-f', 'mp3', '-'], capture_output=True, check=True).stdout
    return base64.b64encode(mp3).decode(), round(gain, 1)


d = json.load(open(J))
prev_new = set(d.get('dvn', []))
foot = d['dv']['foot']
# 1) 外す声を old_vo に残す(初回のみ中身が見つかる)
for b in foot:
    h = sha(b)
    if h in REMOVE:
        out = os.path.join(OLD, REMOVE[h])
        if not os.path.exists(out):
            open(out, 'wb').write(base64.b64decode(b))
keep = [b for b in foot if sha(b) not in REMOVE and sha(b) not in prev_new]
target = round(statistics.median(loud('anull', tmpfile(b)) for b in keep), 1)
# 2) 新しい声を足す
files = sorted(glob.glob(os.path.join(V, 'shi_*.wav')))
new = []
for f in files:
    b, g = encode(f, target)
    new.append(b)
    p = tmpfile(b)
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout)
    print(os.path.basename(f), '長さ', round(dur, 2), '秒 / 音量補正', g, 'dB')
d['dv']['foot'] = keep + new
d['dvn'] = [sha(b) for b in new]
json.dump(d, open(J, 'w'))
print('残した元の声', len(keep), '本 + 新しい声', len(new), '本 = dv.foot', len(d['dv']['foot']), '本 / 目標音量', target, 'LUFS / audio.json', os.path.getsize(J) // 1024, 'KB')

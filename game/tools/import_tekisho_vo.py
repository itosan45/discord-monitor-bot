"""「敵将、討ち取ったり」(オーナー録音)を6人分の声に加工して audio.json の vo に格納し、assets/voice/vo_v4/ にも保存する。
v4(2026-10-10): v3 の加工に RNNoise(声専用のノイズ除去)と、こもり取り(プレゼンス・レゾナンス)を追加。v3 は assets/voice/vo_v3/ に残す。"""
import base64
import json
import os
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "assets" / "voice" / "user" / "tekisho_uchitottari_owner.m4a"
OUT_DIR = ROOT / "assets" / "voice" / "vo_v4"
OUTPUT = ROOT / "game" / "data" / "audio.json"
FF = os.environ.get("FFMPEG", "ffmpeg")
MODEL = ROOT / "game" / "tools" / "rnnoise" / "sh.rnnn"
PITCH = {"yuki": 0.97, "kage": 0.93, "mitsu": 1.01, "nobu": 0.99, "shin": 0.88, "musashi": 0.97}


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout)


def chain(r):
    end = dur(SRC) - 1.3
    # v3 は頭1秒を雑音として切っていたが、そこに「敵将」が入っていた(文字起こしで判明)。v4 は頭を切らず RNNoise で雑音だけ消す
    return (f"atrim=start=0.05:end={end:.2f},asetpts=PTS-STARTPTS,highpass=f=95,aresample=48000,arnndn=m='{MODEL}':mix=1,arnndn=m='{MODEL}':mix=1,afftdn=nf=-50:tn=1,lowpass=f=8500,"
            "silenceremove=start_periods=1:start_duration=0.03:start_threshold=-45dB,"
            f"asetrate=48000*{r},aresample=48000,"
            "equalizer=f=120:t=q:w=1:g=4,equalizer=f=350:t=q:w=1.2:g=-4,equalizer=f=1500:t=q:w=1:g=2,equalizer=f=2600:t=q:w=1:g=6,"
            "equalizer=f=3400:t=q:w=1.2:g=5,equalizer=f=4200:t=q:w=1.2:g=2,equalizer=f=6000:t=q:w=1.5:g=2,deesser=i=0.3,"
            "acompressor=threshold=-20dB:ratio=5:attack=5:release=180:makeup=3dB,agate=threshold=0.008:ratio=4:attack=1:release=250:range=0.01:knee=6,areverse,afade=t=in:d=0.05,areverse,afade=t=in:d=0.01,"
            "aecho=0.85:0.75:80|170|290:0.22|0.13|0.07")


def loud(af):
    r = subprocess.run([FF, "-hide_banner", "-i", str(SRC), "-af", af + ",ebur128", "-f", "null", "-"], capture_output=True, text=True)
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)[-1])


def pregate(af, measure):
    """ゲートの手前で音量を -18 LUFS にそろえる(元の録音の大小でゲートが声まで消さないように)"""
    if "agate" not in af:
        return af
    pre, post = af.split("agate", 1)
    return pre + f"volume={-18 - measure(pre.rstrip(',')):.2f}dB,agate" + post


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = json.loads(OUTPUT.read_text(encoding="utf-8"))
    vo = {}
    for k, r in PITCH.items():
        af = pregate(chain(r), loud)
        g = -13.5 - loud(af)
        out = OUT_DIR / f"vo_{k}.mp3"
        subprocess.run([FF, "-v", "error", "-y", "-i", str(SRC), "-af", f"{af},volume={g:.2f}dB,alimiter=limit=0.92",
                        "-ac", "1", "-ar", "24000", "-b:a", "64k", str(out)], check=True)
        vo[k] = base64.b64encode(out.read_bytes()).decode("ascii")
    data["vo"] = vo
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print("vo v4:", {k: round(dur(OUT_DIR / f"vo_{k}.mp3"), 2) for k in PITCH})


if __name__ == "__main__":
    main()

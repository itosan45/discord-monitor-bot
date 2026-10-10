"""assets/voice/user/*.m4a のユーザー録音を整音して audio.json に格納する。"""
import base64
import json
import os
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
MODEL_S = str(ROOT / "game" / "tools" / "rnnoise" / "sh.rnnn")  # RNNoise を2回重ねて声と重なる「サー」も減らす
SOURCE = ROOT / "assets" / "voice" / "user"
OUTPUT = ROOT / "game" / "data" / "audio.json"
FILES = {
    "charge": "charge.m4a",
    "hey": "hey.m4a",
    "seiya": "seiya.m4a",
    "victory": "victory_v2_mononodomo.m4a",  # 2026-10-10 撮り直し「者ども、勝ち鬨をあげよ」(旧 victory.m4a は残す)
}
FILTERS = (
    "silenceremove=start_periods=1:start_duration=0.08:start_threshold=-34dB,"
    "highpass=f=100,lowpass=f=9000,"
    "acompressor=threshold=-24dB:ratio=2.5:attack=8:release=150:makeup=4dB,"
    "volume=5dB,aecho=0.9:0.8:65|130:0.14|0.08,alimiter=limit=0.92"
)


# スマホ録音のこもり取り(勝鬨の音頭用): 箱鳴り(350Hz)を削り、胸の響き(140Hz)・声の芯(1.5k)・張り(3.2k)・抜け(6k)を上げ、倍音を足す。広い残響
PRESENCE = (
    "silenceremove=start_periods=1:start_duration=0.03:start_threshold=-40dB,areverse,"
    "silenceremove=start_periods=1:start_duration=0.03:start_threshold=-40dB,areverse,"
    "highpass=f=80,aresample=48000,arnndn=m='" + str(ROOT / "game" / "tools" / "rnnoise" / "sh.rnnn") + "':mix=1,arnndn=m='" + MODEL_S + "':mix=1,afftdn=nf=-50:tn=1,lowpass=f=8500,atempo=1.07,"  # RNNoise で背景ノイズを除去  # 少しだけ詰めて、次の「えい・えい・おー」(音頭の3.2秒後)との間を0.4秒以上あける
    "equalizer=f=140:t=q:w=1:g=3,equalizer=f=350:t=q:w=1.2:g=-4,equalizer=f=1500:t=q:w=1:g=3,"
    "equalizer=f=2300:t=q:w=1:g=3,equalizer=f=3200:t=q:w=1.2:g=7,equalizer=f=4200:t=q:w=1.2:g=3,equalizer=f=6000:t=q:w=1.5:g=3,deesser=i=0.3,"
    "acompressor=threshold=-22dB:ratio=3:attack=6:release=160:makeup=2dB,agate=threshold=0.008:ratio=4:attack=1:release=250:range=0.01:knee=6,areverse,afade=t=in:d=0.04,areverse,"
    "aecho=0.85:0.75:90|180|300:0.22|0.13|0.07,volume=-1dB,alimiter=limit=0.92"
)
FILTER_FOR = {"victory": PRESENCE}
# 音量をそろえる目標(LUFS)。勝鬨の音頭は以前 -24 LUFS で他の声より約10dB小さかった(オーナー指摘)
TARGET = {"victory": -12.5}


def loudness(af, source):
    r = subprocess.run([os.environ.get("FFMPEG", "ffmpeg"), "-hide_banner", "-i", str(source), "-af", af + ",ebur128", "-f", "null", "-"],
                       capture_output=True, text=True)
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)[-1])


def pregate(af, measure):
    """ゲートの手前で音量を -18 LUFS にそろえる(元の録音の大小でゲートが声まで消さないように)"""
    if "agate" not in af:
        return af
    pre, post = af.split("agate", 1)
    return pre + f"volume={-18 - measure(pre.rstrip(',')):.2f}dB,agate" + post


def main():
    data = json.loads(OUTPUT.read_text(encoding="utf-8"))
    encoded = {}
    for key, filename in FILES.items():
        source = SOURCE / filename
        af = pregate(FILTER_FOR.get(key, FILTERS), lambda x: loudness(x, source))
        if key in TARGET:
            af = af.rsplit(",alimiter", 1)[0]
            af += f",volume={TARGET[key] - loudness(af, source):.2f}dB,alimiter=limit=0.95"
        result = subprocess.run(
            [
                os.environ.get("FFMPEG", "ffmpeg"), "-hide_banner", "-loglevel", "error",
                "-i", str(source), "-af", af, "-ac", "1", "-ar", "24000",
                "-b:a", "64k", "-f", "mp3", "pipe:1",
            ],
            check=True,
            capture_output=True,
        )
        encoded[key] = base64.b64encode(result.stdout).decode("ascii")
    data["uv"] = encoded
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print("Embedded user voice (KiB):", {k: round(len(v) * 3 / 4 / 1024) for k, v in encoded.items()})


if __name__ == "__main__":
    main()

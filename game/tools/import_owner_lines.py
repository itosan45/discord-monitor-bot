"""assets/voice/user/lines2/*.m4a のオーナー録音(ボスのセリフ・味方の掛け声)を整音して audio.json に格納する。
bv: ボスのセリフ(低く太く・残響)。pk: 味方の掛け声(軽い残響)。ev: 雑魚の断末魔「無念じゃ」・攻撃「死ねいっ」。元の録音は消さない。"""
import base64
import json
import os
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "assets" / "voice" / "user" / "lines2"
OUTPUT = ROOT / "game" / "data" / "audio.json"
FF = os.environ.get("FFMPEG", "ffmpeg")
BOSS = {"onore": "boss_onore", "migoto": "boss_migotonari", "munen": "boss_munenja", "masaka": "boss_masaka_konowashiga",
        "nakanaka": "boss_nakanaka_yarioruwa", "kirisute": "boss_kirisutete_kureruwa", "shine": "boss_shine"}
KIAI = ["kiai_ha", "kiai_orya", "kiai_eiya", "kiai_seia", "kiai_se", "kiai_torya"]
TRIM = ("silenceremove=start_periods=1:start_duration=0.03:start_threshold=-40dB,areverse,"
        "silenceremove=start_periods=1:start_duration=0.03:start_threshold=-40dB,areverse,"
        "highpass=f=90,afftdn=nf=-30,afade=t=in:d=0.01")
# 2026-10-10 オーナー「こもっている、プレゼンスとレゾナンスを上げたら」: 箱鳴り350Hzを削り、胸の響き140Hz・芯1.5k・張り3.2k・抜け6kを上げ、倍音を足す
PRES = ("equalizer=f=350:t=q:w=1.2:g=-4,equalizer=f=1500:t=q:w=1:g=3,equalizer=f=3200:t=q:w=1.2:g=5,"
        "equalizer=f=6000:t=q:w=1.5:g=3,aexciter=amount=1.5:drive=6:freq=3500:blend=0,deesser=i=0.3,")
BOSS_FX = ("asetrate=48000*0.9,aresample=48000,atempo=1.05,equalizer=f=140:t=q:w=1:g=4," + PRES +
           "acompressor=threshold=-22dB:ratio=3:attack=6:release=160:makeup=2dB,areverse,afade=t=in:d=0.04,areverse,"
           "aecho=0.85:0.7:70|150:0.22|0.12")
KIAI_FX = ("lowpass=f=11000," + PRES + "acompressor=threshold=-22dB:ratio=2.5:attack=6:release=150:makeup=2dB,areverse,afade=t=in:d=0.03,areverse,"
           "aecho=0.9:0.8:65|130:0.14|0.08")


def loud(af, src):
    r = subprocess.run([FF, "-hide_banner", "-i", str(src), "-af", af + ",ebur128", "-f", "null", "-"], capture_output=True, text=True)
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)[-1])


def enc(name, fx, target):
    src = SOURCE / f"{name}.m4a"
    af = TRIM + "," + fx
    g = target - loud(af, src)
    out = subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-i", str(src), "-af", f"{af},volume={g:.2f}dB,alimiter=limit=0.92",
                          "-ac", "1", "-ar", "24000", "-b:a", "64k", "-f", "mp3", "pipe:1"], check=True, capture_output=True).stdout
    return base64.b64encode(out).decode("ascii")


def main():
    data = json.loads(OUTPUT.read_text(encoding="utf-8"))
    data["bv"] = {k: enc(v, BOSS_FX, -15) for k, v in BOSS.items()}
    data["pk"] = [enc(n, KIAI_FX, -16) for n in KIAI]
    data["ev"] = {"munen": enc("boss_munenja", KIAI_FX, -17), "shine": enc("boss_shine", KIAI_FX, -16)}  # 雑魚用(軽い加工)
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print("bv KiB", {k: round(len(v) * 3 / 4 / 1024) for k, v in data["bv"].items()}, "pk", len(data["pk"]))


if __name__ == "__main__":
    main()

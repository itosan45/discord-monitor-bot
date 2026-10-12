"""Gemini TTS で作った「敵将、討ち取ったり」「者ども、勝鬨をあげよう」を audio.json に入れる(2026-10-13)。
- vo(6人の主人公の「討ち取ったり」): teki_*.wav を主人公ごとに音の高さを変えて作る(比率は import_tekisho_vo.py の v5 と同じ)。-13.5 LUFS。
- uv.victory(勝鬨の音頭): kachi_*.wav を、次の「えい・えい・おー」(音頭の3.2秒後)に被らないよう 2.7 秒以内に速度をそろえる。-12.5 LUFS。残響なし。
元の素材はきれいなので、オーナー録音用のノイズ除去・こもり取りはしない(前後の無音除去・低域カット・軽い音色調整・圧縮・音量そろえのみ)。
オーナー録音は assets/voice/user/ に残してある。元に戻すには import_tekisho_vo.py と import_user_voice.py を実行する(README 参照)。
使い方: python3 game/tools/import_generated_lines.py [teki_a|teki_b|teki_c|teki_nobi_a|teki_nobi_b] [kachi_a|kachi_b]  → cd game && python3 build.py
引数なしは teki_nobi_a(語尾を長く伸ばした版)と kachi_b。何度実行しても同じ結果になる。"""
import base64
import json
import os
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "assets" / "voice" / "gemini_lines_20261013"
OUT_DIR = ROOT / "assets" / "voice" / "vo_gemini_20261013"
OLD = ROOT / "assets" / "voice" / "old_vo"
OUTPUT = ROOT / "game" / "data" / "audio.json"
FF = os.environ.get("FFMPEG", "ffmpeg")
PITCH = {"yuki": 0.97, "kage": 0.93, "mitsu": 1.01, "nobu": 0.99, "shin": 0.88, "musashi": 0.97}
VO_LUFS, UV_LUFS, VICTORY_MAX = -13.5, -12.5, 2.7
TRIM = ("silenceremove=start_periods=1:start_duration=0.02:start_threshold=-42dB,areverse,"
        "silenceremove=start_periods=1:start_duration=0.02:start_threshold=-42dB,areverse,highpass=f=90")


def run(*a):
    return subprocess.run([FF, "-hide_banner", "-loglevel", "error", *a], check=True, capture_output=True).stdout


def trimmed_dur(src):
    raw = run("-i", str(src), "-af", TRIM, "-ac", "1", "-ar", "24000", "-f", "f32le", "-")
    return len(raw) / 4 / 24000


def loud(src, af):
    r = subprocess.run([FF, "-hide_banner", "-i", str(src), "-af", af + ",ebur128", "-f", "null", "-"], capture_output=True, text=True)
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)[-1])


def encode(src, af, lufs, limit):
    g = lufs - loud(src, af)
    mp3 = run("-i", str(src), "-af", f"{af},volume={g:.2f}dB,alimiter=limit={limit}", "-ac", "1", "-ar", "24000", "-b:a", "64k", "-f", "mp3", "-")
    return mp3, g


def vo_chain(r):
    return (f"{TRIM},aresample=48000,asetrate=48000*{r},aresample=48000,"
            "equalizer=f=120:t=q:w=1:g=3,equalizer=f=350:t=q:w=1.2:g=-2,equalizer=f=2600:t=q:w=1:g=3,equalizer=f=3400:t=q:w=1.2:g=2,"
            "acompressor=threshold=-20dB:ratio=4:attack=5:release=180:makeup=3dB,"
            "afade=t=in:d=0.01,areverse,afade=t=in:d=0.04,areverse")


def uv_chain(tempo):
    return (f"{TRIM},aresample=48000,atempo={tempo:.4f},"
            "equalizer=f=140:t=q:w=1:g=2,equalizer=f=350:t=q:w=1.2:g=-2,equalizer=f=3200:t=q:w=1.2:g=3,"
            "acompressor=threshold=-22dB:ratio=3:attack=6:release=160:makeup=2dB,"
            "afade=t=in:d=0.01,areverse,afade=t=in:d=0.04,areverse")


def mp3_dur(b):
    p = subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-i", "pipe:0", "-f", "f32le", "-ac", "1", "-ar", "24000", "-"], input=b, capture_output=True, check=True)
    return len(p.stdout) / 4 / 24000


def main():
    teki = sys.argv[1] if len(sys.argv) > 1 else "teki_nobi_a"
    kachi = sys.argv[2] if len(sys.argv) > 2 else "kachi_b"
    teki_wav, kachi_wav = SRC / f"{teki}.wav", SRC / f"{kachi}.wav"
    assert teki_wav.exists() and kachi_wav.exists(), (teki_wav, kachi_wav)
    d = json.loads(OUTPUT.read_text(encoding="utf-8"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # 最初の1回だけ、今の勝鬨の音頭(オーナー録音から作ったもの)を old_vo に控える
    keep = OLD / "uv_victory_owner_20261012.mp3"
    if "gen_lines" not in d and not keep.exists() and d.get("uv", {}).get("victory"):
        keep.write_bytes(base64.b64decode(d["uv"]["victory"]))
    vo = {}
    for k, r in PITCH.items():
        mp3, g = encode(teki_wav, vo_chain(r), VO_LUFS, 0.92)
        (OUT_DIR / f"vo_{k}.mp3").write_bytes(mp3)
        vo[k] = base64.b64encode(mp3).decode("ascii")
        print(f"vo {k}: {mp3_dur(mp3):.2f} 秒 / 音量補正 {g:+.1f} dB")
    raw_dur = trimmed_dur(kachi_wav)
    tempo = max(1.0, raw_dur / VICTORY_MAX)
    mp3, g = encode(kachi_wav, uv_chain(tempo), UV_LUFS, 0.95)
    (OUT_DIR / "uv_victory.mp3").write_bytes(mp3)
    print(f"uv.victory: 元 {raw_dur:.2f} 秒 → 速度 x{tempo:.3f} → {mp3_dur(mp3):.2f} 秒 / 音量補正 {g:+.1f} dB")
    d["vo"] = vo
    d.setdefault("uv", {})["victory"] = base64.b64encode(mp3).decode("ascii")
    d["gen_lines"] = {"teki": teki, "kachi": kachi}
    OUTPUT.write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print("audio.json", OUTPUT.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()

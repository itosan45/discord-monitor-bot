"""assets/voice/user/*.m4a のユーザー録音を整音して audio.json に格納する。"""
import base64
import json
import os
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "assets" / "voice" / "user"
OUTPUT = ROOT / "game" / "data" / "audio.json"
FILES = {
    "charge": "charge.m4a",
    "hey": "hey.m4a",
    "seiya": "seiya.m4a",
    "victory": "victory.m4a",
}
FILTERS = (
    "highpass=f=100,lowpass=f=9000,"
    "acompressor=threshold=-24dB:ratio=2.5:attack=8:release=150:makeup=4dB,"
    "volume=5dB,aecho=0.9:0.8:65|130:0.14|0.08,alimiter=limit=0.92"
)


def main():
    data = json.loads(OUTPUT.read_text(encoding="utf-8"))
    encoded = {}
    for key, filename in FILES.items():
        source = SOURCE / filename
        result = subprocess.run(
            [
                os.environ.get("FFMPEG", "ffmpeg"), "-hide_banner", "-loglevel", "error",
                "-i", str(source), "-af", FILTERS, "-ac", "1", "-ar", "24000",
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

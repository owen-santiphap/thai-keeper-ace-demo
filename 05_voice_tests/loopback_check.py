"""Compare loopback recording with the source pieces: per piece, voiced length in source vs in loopback, and ASR text."""
import os
import sys
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf
import torch

sys.stdout.reconfigure(encoding="utf-8")
os.add_dll_directory(str(Path(torch.__file__).parent / "lib"))
os.environ["PATH"] = str(Path(torch.__file__).parent / "lib") + os.pathsep + os.environ["PATH"]
from faster_whisper import WhisperModel  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
D = Path(__file__).resolve().parent / "out" / "e2e"
asr = WhisperModel(str(ROOT / "downloads" / "models" / "typhoon-whisper-turbo-ct2-int8"), device="cuda",
                   compute_type="int8_float16")
lb, sr = sf.read(str(D / "loopback.wav"), dtype="float32")
lb = librosa.resample(lb.mean(axis=1), orig_sr=sr, target_sr=16000)
# voiced regions in the loopback (gaps between pieces are >= 0.45 s of digital silence)
iv = librosa.effects.split(lb, top_db=40, frame_length=1024, hop_length=256)
merged = []
for s, e in iv:  # merge regions closer than 0.3 s (pauses inside a phrase)
    if merged and s - merged[-1][1] < int(0.3 * 16000):
        merged[-1][1] = e
    else:
        merged.append([s, e])
print("voiced regions in loopback:", [(round(s / 16000, 2), round((e - s) / 16000, 2)) for s, e in merged])
src = []
for i in range(3):
    for j in range(2):
        a, r = sf.read(str(D / f"play_{i}_{j}.wav"), dtype="float32")
        a = librosa.resample(a if a.ndim == 1 else a.mean(axis=1), orig_sr=r, target_sr=16000)
        s, e = librosa.effects.split(a, top_db=40)[[0, -1]][:, [0, 1]].flatten()[[0, 3]]
        src.append(round((e - s) / 16000, 2))
print("voiced length of source pieces:", src)
for k, (s, e) in enumerate(merged):
    segs, _ = asr.transcribe(lb[max(0, s - 8000):e + 8000], language="th", beam_size=1)
    print(f"region {k}: {''.join(x.text for x in segs).strip()}")

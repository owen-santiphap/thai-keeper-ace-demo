"""CPU ASR speed check: Typhoon Whisper Turbo converted to CTranslate2 int8 (faster-whisper).

Transcribes the TTS bench outputs and the reference clip, prints seconds per clip and text.
Usage: .venv-voice\\Scripts\\python.exe 05_voice_tests\\asr_ct2_bench.py [threads] [device]
"""
import sys
import time
from pathlib import Path

import librosa
import soundfile as sf
from faster_whisper import WhisperModel

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
MODEL = ROOT / "downloads" / "models" / "typhoon-whisper-turbo-ct2-int8"
OUT = Path(__file__).resolve().parent / "out"
threads = int(sys.argv[1]) if len(sys.argv) > 1 else 8
device = sys.argv[2] if len(sys.argv) > 2 else "cpu"

t = time.time()
model = WhisperModel(str(MODEL), device=device, compute_type="int8", cpu_threads=threads)
print(f"loaded on {device} ({threads} threads) in {time.time() - t:.1f}s")

clips = [ROOT / "tools" / "thonburian-tts" / "assets" / "000000.wav"] + sorted(OUT.glob("keeper_*.wav"))[:3]
for i, clip in enumerate(clips):
    t = time.time()
    audio, sr = sf.read(str(clip), dtype="float32", always_2d=True)
    audio = librosa.resample(audio.mean(axis=1), orig_sr=sr, target_sr=16000) if sr != 16000 else audio.mean(axis=1)
    segs, _ = model.transcribe(audio, language="th", beam_size=1, vad_filter=False)
    text = "".join(s.text for s in segs).strip()
    dt = time.time() - t
    tag = "(warm-up)" if i == 0 else ""
    print(f"{clip.name}: {dt:.2f}s for {sf.info(str(clip)).duration:.1f}s audio {tag} -> {text}")


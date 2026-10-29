"""Standalone Thai speech-to-text test (no Unreal).

Records from your microphone, transcribes with Typhoon Whisper Turbo, prints the Thai text,
the time taken and (on GPU) the VRAM used. Every result is also appended to asr_results.txt (UTF-8),
because the Windows console may not display Thai correctly.

Usage (PowerShell, from the main work folder):
    python 05_voice_tests\test_thai_asr.py          # 5 second recordings
    python 05_voice_tests\test_thai_asr.py 8        # 8 second recordings

Model loading follows the model's own README (transformers pipeline, language="thai").
"""
import sys
import time
from pathlib import Path

import numpy as np
import sounddevice as sd
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = Path(__file__).resolve().parent
MODEL_DIR = HERE.parent / "downloads" / "models" / "typhoon-whisper-turbo"
LOG = HERE / "asr_results.txt"
SR = 16000
SECONDS = float(sys.argv[1]) if len(sys.argv) > 1 else 5.0

cuda = torch.cuda.is_available()
device = "cuda:0" if cuda else "cpu"
dtype = torch.bfloat16 if cuda else torch.float32
print(f"device={device}  dtype={dtype}")
if not cuda:
    print("WARNING: running on CPU. Install a CUDA build of torch to use the GPU (see README.md).")

t0 = time.time()
model = AutoModelForSpeechSeq2Seq.from_pretrained(
    str(MODEL_DIR), torch_dtype=dtype, low_cpu_mem_usage=True, use_safetensors=True
).to(device)
processor = AutoProcessor.from_pretrained(str(MODEL_DIR))
pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    chunk_length_s=30,
    torch_dtype=dtype,
    device=device,
)
print(f"model loaded in {time.time() - t0:.1f}s")
if cuda:
    print(f"GPU memory allocated: {torch.cuda.memory_allocated() / 1024**2:.0f} MiB")

print(f"\nMic test: press Enter, then speak Thai for {SECONDS:.0f} seconds. Ctrl+C to quit.")
while True:
    try:
        input("\n[Enter] to record > ")
    except (KeyboardInterrupt, EOFError):
        break
    audio = sd.rec(int(SECONDS * SR), samplerate=SR, channels=1, dtype="float32")
    sd.wait()
    audio = np.asarray(audio[:, 0], dtype=np.float32)
    peak = float(np.abs(audio).max())
    if peak < 0.01:
        print("(very quiet recording - check your microphone / Windows input device)")
    t = time.time()
    out = pipe({"raw": audio, "sampling_rate": SR}, generate_kwargs={"language": "thai"})
    dt = time.time() - t
    text = out["text"].strip()
    print(f"TEXT: {text}   [{dt:.2f}s for {SECONDS:.0f}s of audio, peak={peak:.2f}]")
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"{text}\t{dt:.2f}s\n")

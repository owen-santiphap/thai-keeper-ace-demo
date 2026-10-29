"""End-to-end voice check without a listener: (1) speaking rate at several TTS speeds, (2) play replies exactly like
voice_service.play_loop (two pieces, silent tail) through the speakers while recording the mic, then ASR the recording
to see whether the endings survive. Usage: .venv-voice python voice_e2e_test.py [speed_for_playback]"""
import json
import os
import sys
import threading
import time
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf
import torch
import torchaudio

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools" / "thonburian-tts"))
sys.stdout.reconfigure(encoding="utf-8")


def _sf_load(path, *a, **k):
    data, sr = sf.read(str(path), dtype="float32", always_2d=True)
    return torch.from_numpy(data.T.copy()), sr


def _sf_save(path, tensor, sample_rate, *a, **k):
    sf.write(str(path), tensor.detach().cpu().numpy().T, sample_rate)


torchaudio.load, torchaudio.save = _sf_load, _sf_save
os.add_dll_directory(str(Path(torch.__file__).parent / "lib"))
os.environ["PATH"] = str(Path(torch.__file__).parent / "lib") + os.pathsep + os.environ["PATH"]
from faster_whisper import WhisperModel  # noqa: E402
from flowtts.inference import AudioConfig, FlowTTSPipeline, ModelConfig  # noqa: E402
import librosa  # noqa: E402

PLAY_SPEED = float(sys.argv[1]) if len(sys.argv) > 1 else 0.85
asr = WhisperModel(str(ROOT / "downloads" / "models" / "typhoon-whisper-turbo-ct2-int8"), device="cuda",
                   compute_type="int8_float16")
TTS_DIR = ROOT / "downloads" / "models" / "ThonburianTTS"
OUT = Path(__file__).resolve().parent / "out" / "e2e"
OUT.mkdir(parents=True, exist_ok=True)
tts = FlowTTSPipeline(
    model_config=ModelConfig(language="th", model_type="F5", checkpoint=str(TTS_DIR / "mega_f5_last.safetensors"),
                             vocab_file=str(TTS_DIR / "mega_vocab.txt"), vocoder="vocos", device="cuda"),
    audio_config=AudioConfig(silence_threshold=-45, cfg_strength=2.5, speed=1.0, nfe_step=16),
    temp_dir=str(OUT / "tmp"))
REF = str(ROOT / "tools" / "thonburian-tts" / "assets" / "000000.wav")


def transcribe(a, sr):
    a = librosa.resample(a, orig_sr=sr, target_sr=16000) if sr != 16000 else a
    segs, _ = asr.transcribe(a.astype(np.float32), language="th", beam_size=1)
    return "".join(s.text for s in segs).strip()


ref_a, ref_sr = sf.read(REF, dtype="float32")
ref_text = transcribe(ref_a if ref_a.ndim == 1 else ref_a.mean(axis=1), ref_sr)
LINES = ["กระสือเป็นผีผู้หญิงที่ถอดหัวกับไส้พุงลอยออกไปหากินของคาวของสกปรกตอนกลางคืน มีแสงไฟเรืองๆ เลยนะ",
         "เปรตตัวสูงเท่าต้นตาล ผอมโซ มือโตเท่าใบลาน ปากเล็กเท่ารูเข็ม หิวตลอดเวลา",
         "ประตูเปิดแล้ว เข้ามาสิ ไม่ต้องกลัว ผีเขาไม่กัดหรอก หึ หึ"]


def synth(text, speed, name):
    wav = OUT / f"{name}.wav"
    tts(text=text, ref_voice=REF, ref_text=ref_text, output_file=str(wav), speed=speed)
    a, sr = sf.read(str(wav), dtype="float32")
    a = a if a.ndim == 1 else a.mean(axis=1)
    voiced, _ = librosa.effects.trim(a, top_db=35)
    return a, sr, len(voiced) / sr


# 1. speaking rate
rate = []
for speed in [1.0, 0.9, 0.85, 0.8]:
    for i, line in enumerate(LINES):
        _, _, secs = synth(line, speed, f"rate_{speed}_{i}")
        rate.append({"speed": speed, "line": i, "chars": len(line.replace(" ", "")), "secs": round(secs, 2)})
        print(f"speed {speed} line {i}: {secs:.2f}s voiced", flush=True)

# 2. speaker -> mic round trip, played exactly like play_loop (two pieces, 0.45 s tail each)
rec, rec_on = [], threading.Event()


def on_mic(indata, frames, t, status):
    if rec_on.is_set():
        rec.append(indata[:, 0].copy())


results = []
with sd.InputStream(samplerate=16000, channels=1, dtype="float32", blocksize=800, callback=on_mic):
    for i, line in enumerate(LINES):
        words = line.split(" ")
        half = max(1, len(words) // 2)
        pieces = [" ".join(words[:half]), " ".join(words[half:])]
        audio = [synth(p, PLAY_SPEED, f"play_{i}_{j}")[:2] for j, p in enumerate(pieces)]
        rec.clear()
        rec_on.set()
        time.sleep(0.3)
        for a, sr in audio:
            a = np.concatenate([a, np.zeros(int(sr * 0.45), dtype=a.dtype)])
            sd.play(a, sr)
            sd.wait()
        time.sleep(0.8)
        rec_on.clear()
        mic = np.concatenate(rec)
        sf.write(str(OUT / f"mic_{i}.wav"), mic, 16000)
        heard = transcribe(mic, 16000)
        results.append({"said": line, "pieces": pieces, "heard_through_mic": heard})
        print(f"\nSAID : {line}\nHEARD: {heard}", flush=True)
        time.sleep(1.0)
(OUT / "e2e.json").write_text(json.dumps({"play_speed": PLAY_SPEED, "rate": rate, "roundtrip": results},
                                         ensure_ascii=False, indent=1), encoding="utf-8")

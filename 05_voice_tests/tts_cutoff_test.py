"""Does ThonburianTTS clip the end of short pieces? Synthesize keeper lines as-is and with an end pause, transcribe them
back with the same ASR and compare the last words. Usage: .venv-voice python tts_cutoff_test.py"""
import os
import sys
from pathlib import Path

import numpy as np
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

asr = WhisperModel(str(ROOT / "downloads" / "models" / "typhoon-whisper-turbo-ct2-int8"), device="cuda",
                   compute_type="int8_float16")
TTS_DIR = ROOT / "downloads" / "models" / "ThonburianTTS"
OUT = Path(__file__).resolve().parent / "out" / "cutoff"
OUT.mkdir(parents=True, exist_ok=True)
tts = FlowTTSPipeline(
    model_config=ModelConfig(language="th", model_type="F5", checkpoint=str(TTS_DIR / "mega_f5_last.safetensors"),
                             vocab_file=str(TTS_DIR / "mega_vocab.txt"), vocoder="vocos", device="cuda"),
    audio_config=AudioConfig(silence_threshold=-45, cfg_strength=2.5, speed=1.0, nfe_step=16),
    temp_dir=str(OUT / "tmp"))
REF = str(ROOT / "tools" / "thonburian-tts" / "assets" / "000000.wav")


def transcribe(path):
    a, sr = sf.read(path, dtype="float32", always_2d=True)
    a = librosa.resample(a.mean(axis=1), orig_sr=sr, target_sr=16000)
    segs, _ = asr.transcribe(a.astype(np.float32), language="th", beam_size=1)
    return "".join(s.text for s in segs).strip()


ref_text = transcribe(REF)
print("ref transcript:", ref_text, "| ref seconds:", round(sf.info(REF).duration, 2))
LINES = ["ได้เลย รอแป๊บนะ ลุงเดินไปจุดตะเกียงก่อน",
         "เพราะกระสือกลัวหนามเกี่ยวไส้ล่ะหลาน",
         "กระหังมันขี่สากตำข้าวเป็นหาง แล้วบินออกไปหากินของสกปรก",
         "ถึงแล้ว ดูนั่นสิ เห็นมั้ย หึๆ อย่าเพิ่งวิ่งหนีล่ะ"]
for i, line in enumerate(LINES):
    for tag, text in [("plain", line), ("pause", line + " ...")]:
        wav = OUT / f"{i}_{tag}.wav"
        tts(text=text, ref_voice=REF, ref_text=ref_text, output_file=str(wav), speed=1.0)
        print(f"[{i} {tag:5}] {sf.info(str(wav)).duration:4.1f}s | said: {line}\n            heard: {transcribe(str(wav))}")

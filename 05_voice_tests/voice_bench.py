"""Thai voice bench (no Unreal, no microphone).

1. Loads Typhoon Whisper Turbo (ASR) and transcribes the ThonburianTTS reference clip.
2. Loads ThonburianTTS (megaF5, local weights) and speaks a few keeper lines -> out/*.wav
3. Feeds those wavs back through ASR (round-trip check: is the synthetic speech intelligible?).
Prints load time, generation time, real-time factor and GPU memory for each step.
Results also go to out/bench_results.txt (UTF-8).

Usage (from the main work folder):
    .venv-voice\\Scripts\\python.exe 05_voice_tests\\voice_bench.py [--asr-device cpu|cuda] [--tts-device cpu|cuda]
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

import soundfile as sf
import torch
import torchaudio
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline


# torchaudio 2.9+ decodes through torchcodec, which needs FFmpeg DLLs that are not installed.
# We only handle WAV files, so route torchaudio's load/save through soundfile instead.
def _sf_load(path, *args, **kwargs):
    data, sr = sf.read(str(path), dtype="float32", always_2d=True)
    return torch.from_numpy(data.T.copy()), sr


def _sf_save(path, tensor, sample_rate, *args, **kwargs):
    sf.write(str(path), tensor.detach().cpu().numpy().T, sample_rate)


torchaudio.load = _sf_load
torchaudio.save = _sf_save

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools" / "thonburian-tts"))
from flowtts.inference import AudioConfig, FlowTTSPipeline, ModelConfig  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(exist_ok=True)
LOG = OUT / "bench_results.txt"
ASR_DIR = ROOT / "downloads" / "models" / "typhoon-whisper-turbo"
TTS_DIR = ROOT / "downloads" / "models" / "ThonburianTTS"
REF_WAV = ROOT / "tools" / "thonburian-tts" / "assets" / "000000.wav"

LINES = [
    "โอ้ย! ตะเกียงจุดแล้วล่ะครับ แสงสว่างๆ เงียบๆ เหมือนคืนนั้นเอง",
    "กระสือเป็นผีผู้หญิงที่เห็นเป็นหัวลอยได้ มีไส้ห้อยอยู่ใต้คอ และมีแสงเรืองๆ",
    "ลุงบุญเปิดประตูให้แล้วครับ คุณเดินเข้ามาได้เลยนะ",
]

ap = argparse.ArgumentParser()
ap.add_argument("--asr-device", default="cuda")
ap.add_argument("--tts-device", default="cuda")
ap.add_argument("--nfe", type=int, default=32, help="TTS diffusion steps (32 = model default, 16 = ~2x faster)")
args = ap.parse_args()


def log(msg):
    print(msg)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def gpu_used():
    try:
        q = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=10).stdout.strip()
        used, total = (int(x) for x in q.split(","))
        return f"GPU {used}/{total} MiB"
    except Exception as e:  # noqa: BLE001
        return f"GPU ? ({e})"


log(f"\n===== bench {time.strftime('%Y-%m-%d %H:%M:%S')}  asr={args.asr_device}  tts={args.tts_device}  nfe={args.nfe}  torch {torch.__version__}")
log(f"start: {gpu_used()}")

# ---- ASR
t = time.time()
asr_dtype = torch.float16 if args.asr_device == "cuda" else torch.float32
asr_model = AutoModelForSpeechSeq2Seq.from_pretrained(str(ASR_DIR), torch_dtype=asr_dtype, low_cpu_mem_usage=True,
                                                      use_safetensors=True).to(args.asr_device)
proc = AutoProcessor.from_pretrained(str(ASR_DIR))
asr = pipeline("automatic-speech-recognition", model=asr_model, tokenizer=proc.tokenizer,
               feature_extractor=proc.feature_extractor, chunk_length_s=30, torch_dtype=asr_dtype,
               device=args.asr_device)
log(f"ASR loaded in {time.time() - t:.1f}s  | {gpu_used()}")


def transcribe(path):
    t0 = time.time()
    text = asr(str(path), generate_kwargs={"language": "thai"})["text"].strip()
    dur = sf.info(str(path)).duration
    return text, time.time() - t0, dur


transcribe(REF_WAV)  # warm-up
ref_text, dt, dur = transcribe(REF_WAV)
log(f"ASR ref clip ({dur:.1f}s audio): {dt:.2f}s  -> {ref_text}")

# ---- TTS
t = time.time()
tts = FlowTTSPipeline(
    model_config=ModelConfig(language="th", model_type="F5", checkpoint=str(TTS_DIR / "mega_f5_last.safetensors"),
                             vocab_file=str(TTS_DIR / "mega_vocab.txt"), vocoder="vocos", device=args.tts_device),
    audio_config=AudioConfig(silence_threshold=-45, cfg_strength=2.5, speed=1.0, nfe_step=args.nfe),
    temp_dir=str(OUT / "tmp"),
)
log(f"TTS loaded in {time.time() - t:.1f}s  | {gpu_used()}")

for i, line in enumerate(LINES, 1):
    wav = OUT / f"keeper_{i}_nfe{args.nfe}.wav"
    t0 = time.time()
    tts(text=line, ref_voice=str(REF_WAV), ref_text=ref_text, output_file=str(wav), speed=1.0)
    gen = time.time() - t0
    dur = sf.info(str(wav)).duration
    back, adt, _ = transcribe(wav)
    log(f"TTS line {i}: {gen:.2f}s for {dur:.1f}s audio (RTF {gen / dur:.2f}) | {gpu_used()}")
    log(f"   said : {line}")
    log(f"   heard: {back}   (ASR {adt:.2f}s)")

if torch.cuda.is_available():
    log(f"torch peak allocated: {torch.cuda.max_memory_allocated() / 1024**2:.0f} MiB")
log(f"end: {gpu_used()}")

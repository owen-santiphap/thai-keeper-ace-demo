# Step 1 of voice: Thai listening on its own (no Unreal)

Goal: find out how good and how fast Typhoon Whisper Turbo is on YOUR voice and mic,
and how much VRAM it takes, before we connect anything to Unreal.

## Setup (PowerShell, once)
    cd <repo folder>
    python -m venv .venv-voice
    .\.venv-voice\Scripts\Activate.ps1
    pip install transformers accelerate sounddevice numpy
    # torch: the default Windows wheel is CPU-only. For the GPU, install the CUDA build from
    # https://pytorch.org/get-started/locally/ (pick Windows / Pip / CUDA) instead of plain "pip install torch".

## Run
    python 05_voice_tests\test_thai_asr.py        # then press Enter and speak
Close Unreal first so the GPU memory reading is clean.

## What to do
Say the Thai test questions from 04_keeper\test_questions_th.md (about 10, normal speed),
including the ghost names (กระสือ, กระหัง, นางตานี, กองกอย ...) and a tool request
(ช่วยจุดตะเกียงหน่อย). Results are also saved to asr_results.txt.

## What to report back
- Did it get the ghost names right? Which words went wrong?
- Seconds per 5s of speech, device (cuda or cpu), GPU memory allocated.
- Anything that failed to install or run (paste the error text).

Status: standalone ASR check. The game itself uses voice_service.py (see ../docs/ARCHITECTURE.md).

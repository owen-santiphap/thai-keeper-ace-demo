"""Download and prepare the models for the Thai keeper demo.

Run from the repo root, inside the voice venv (see docs/SETUP.md):
    python scripts/setup_models.py            # everything
    python scripts/setup_models.py --only llm # llm | asr | tts

Creates (all git-ignored):
    downloads/models/typhoon2.5-qwen3-4b-gguf/   original Typhoon GGUF
    downloads/models/typhoon2.5-qwen3-4b-q4_k_m-tools.gguf   GGUF + chat template (this is the file the game loads)
    downloads/models/typhoon-whisper-turbo/      Thai ASR (original)
    downloads/models/typhoon-whisper-turbo-ct2-int8/   Thai ASR, CTranslate2 int8 (what voice_service uses)
    downloads/models/ThonburianTTS/              Thai TTS checkpoint
    tools/thonburian-tts/                        TTS code (git clone, MIT)

STATUS: assembled from the commands we ran by hand during development. Each step is wrapped so one
failure does not stop the others; send the FAILED line to your instructor.
Why the chat-template step exists: the Typhoon GGUF has no chat template, so ACE never sends tool
definitions to the model and tool calls never happen. We add the official template to a copy.
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / "downloads" / "models"

ap = argparse.ArgumentParser()
ap.add_argument("--only", choices=["llm", "asr", "tts"], default=None)
args = ap.parse_args()


def step(name):
    def deco(fn):
        if args.only and not fn.__name__.startswith(args.only):
            return fn
        print(f"\n=== {name}")
        try:
            fn()
            print("OK")
        except Exception as e:  # keep going, report at the end
            print("FAILED:", type(e).__name__, e)
        return fn
    return deco


@step("LLM: Typhoon 2.5 Qwen3 4B Q4_K_M GGUF (~2.5 GB) + chat template")
def llm():
    from huggingface_hub import hf_hub_download, snapshot_download
    d = MODELS / "typhoon2.5-qwen3-4b-gguf"
    snapshot_download("typhoon-ai/typhoon2.5-qwen3-4b-gguf", local_dir=d,
                      allow_patterns=["*q4_k_m*", "*Q4_K_M*"])
    ggufs = [p for p in d.glob("*.gguf") if "q4_k_m" in p.name.lower()]
    if not ggufs:
        raise RuntimeError("no Q4_K_M .gguf found in " + str(d))
    tmpl = None
    for repo in ("scb10x/typhoon2.5-qwen3-4b-preview", "typhoon-ai/typhoon2.5-qwen3-4b"):
        try:
            tmpl = hf_hub_download(repo, "chat_template.jinja")
            break
        except Exception as e:
            print("  template not in", repo, "-", type(e).__name__)
    if not tmpl:
        raise RuntimeError("chat_template.jinja not found; open the model page and download it by hand")
    out = MODELS / "typhoon2.5-qwen3-4b-q4_k_m-tools.gguf"
    subprocess.run([sys.executable, "-m", "gguf.scripts.gguf_new_metadata", str(ggufs[0]), str(out),
                    "--chat-template-file", tmpl], check=True)
    print("  wrote", out)


@step("ASR: Typhoon Whisper Turbo (~1.6 GB) + CTranslate2 int8 conversion")
def asr():
    from huggingface_hub import snapshot_download
    src = MODELS / "typhoon-whisper-turbo"
    snapshot_download("typhoon-ai/typhoon-whisper-turbo", local_dir=src,
                      ignore_patterns=["training_args.bin", ".gitattributes"])
    out = MODELS / "typhoon-whisper-turbo-ct2-int8"
    from ctranslate2.converters import TransformersConverter
    TransformersConverter(str(src), copy_files=["tokenizer.json", "preprocessor_config.json"]).convert(
        str(out), quantization="int8", force=True)
    print("  wrote", out)


@step("TTS: ThonburianTTS checkpoint (CC BY-NC-SA 4.0, non-commercial) + code (MIT)")
def tts():
    from huggingface_hub import snapshot_download
    snapshot_download("biodatlab/ThonburianTTS", local_dir=MODELS / "ThonburianTTS",
                      allow_patterns=["mega_f5_last.safetensors", "mega_vocab.txt"])
    code = ROOT / "tools" / "thonburian-tts"
    if not code.exists():
        subprocess.run(["git", "clone", "--depth", "1", "https://github.com/biodatlab/thonburian-tts", str(code)],
                       check=True)

print("\nDone. Next: docs/SETUP.md step 5.")

"""Thai voice for the keeper demo: mic -> Typhoon Whisper (ASR) -> keeper, and keeper reply -> ThonburianTTS -> speakers.

Run while the game is in Play (start it before or after pressing Play; it waits for the keeper):
    .venv-voice\\Scripts\\python.exe 05_voice_tests\\voice_service.py

Talks to BP_Keeper over Unreal's Remote Control API (http://127.0.0.1:30010), properties only:
  reads  MicMode ("ptt" | "open" | "off"), PTTDown (bool, held V key), ReplyId, ReplyText (streamed), Busy
  writes PendingInput (recognised Thai text), MicLevel (0..1 for the on-screen bar), VoiceStatus (Thai label),
         VoiceOn (the keeper then waits for the voice before showing text), SpeakLine (phrase now being spoken)
The reply is spoken phrase by phrase while the LLM is still writing it. The mic is muted while the keeper thinks
or speaks so it does not hear itself.
"""
import argparse
import os
import queue
import re
import sys
import threading
import time
from pathlib import Path

# ASR (CTranslate2) keeps its own GPU cache next to PyTorch's: cap it at 100 MB (format bin_growth,min_bin,max_bin,
# max_cached_bytes, read from ctranslate2.dll 4.8.3). The service was seen holding 1.8 GB after a morning of
# always-on room speech and Unreal showed "Video memory has been exhausted" (2026-10-21). Must be set before import.
os.environ.setdefault("CT2_CUDA_CACHING_ALLOCATOR_CONFIG", "4,3,12,104857600")

import numpy as np
import sounddevice as sd
import soundfile as sf
import torch
import torchaudio

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "thonburian-tts"))
from keeper_link import KeeperLink  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")


# torchaudio 2.9+ decodes through torchcodec (needs FFmpeg DLLs); we only use WAV, so use soundfile.
def _sf_load(path, *a, **k):
    data, sr = sf.read(str(path), dtype="float32", always_2d=True)
    return torch.from_numpy(data.T.copy()), sr


def _sf_save(path, tensor, sample_rate, *a, **k):
    sf.write(str(path), tensor.detach().cpu().numpy().T, sample_rate)


torchaudio.load, torchaudio.save = _sf_load, _sf_save
from flowtts.inference import AudioConfig, FlowTTSPipeline, ModelConfig  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--asr-device", default="cuda")
ap.add_argument("--asr-engine", default="ct2", choices=["ct2", "hf"], help="ct2 = int8 faster-whisper (less VRAM)")
ap.add_argument("--tts-device", default="cuda")
ap.add_argument("--nfe", type=int, default=16, help="TTS steps (16 fast, 32 best quality)")
ap.add_argument("--speed", type=float, default=0.9,
                help="TTS pace: 1.0 = ~3.9 syllables/s, 0.9 = ~3.5 (calmer old man), 0.85 = ~3.3")
ap.add_argument("--open-threshold", type=float, default=0.04, help="RMS level that starts speech in always-on mode")
ap.add_argument("--stream", action="store_true",
                help="start speaking while the LLM is still writing (faster on a big GPU; on the 8 GB laptop LLM + TTS "
                     "at once slowed both down 2-4x)")
ap.add_argument("--end-silence", type=int, default=600, help="always-on: ms of silence that ends a sentence")
ap.add_argument("--wake", default="ลุง,บุญ",
                help="always-on mode only sends speech containing one of these words (comma list); '' = send everything")
ap.add_argument("--followup", type=float, default=15.0,
                help="seconds after the keeper stops talking during which a reply needs no wake word")
ap.add_argument("--ref-voice", default=str(ROOT / "tools" / "thonburian-tts" / "assets" / "000000.wav"))
ap.add_argument("--ref-text", default=None, help="transcript of --ref-voice (auto-transcribed if omitted)")
ap.add_argument("--selftest", default=None,
                help='"line1|line2": synthesize each line, run it through ASR as if spoken, send it (no mic needed)')
args = ap.parse_args()

SR = 16000
BLOCK = 800  # 50 ms
OUT = Path(__file__).resolve().parent / "out" / "live"
OUT.mkdir(parents=True, exist_ok=True)


LOG_FILE = Path(__file__).resolve().parent / "out" / "voice_live.log"


def log(msg):
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    print(line, flush=True)
    try:  # transcript on disk too, so what was heard / said can be checked later
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


# ------------------------------------------------------------------ models
if args.asr_engine == "ct2":
    # Typhoon Whisper Turbo converted to CTranslate2 int8 (downloads/models/typhoon-whisper-turbo-ct2-int8):
    # about half the VRAM of the fp16 model, same transcripts in our tests. Its CUDA DLLs come from torch.
    import os
    os.add_dll_directory(str(Path(torch.__file__).parent / "lib"))
    os.environ["PATH"] = str(Path(torch.__file__).parent / "lib") + os.pathsep + os.environ["PATH"]
    from faster_whisper import WhisperModel  # noqa: E402

    log("loading ASR (Typhoon Whisper Turbo, int8 CTranslate2)...")
    ASR_PROMPT = "ป่าช้า กระสือ กระหัง ผีปอบ นางตานี ผีโพง ผีกองกอย ผีตายโหง เปรต ตะเกียง"
    _ct2 = WhisperModel(str(ROOT / "downloads" / "models" / "typhoon-whisper-turbo-ct2-int8"), device=args.asr_device,
                        compute_type="int8_float16" if args.asr_device == "cuda" else "int8")

    def transcribe(audio16k):
        # the prompt tells Whisper how the ghost names are spelled (it wrote กระซื้อ, พี่เป๊ก before)
        segs, _ = _ct2.transcribe(audio16k.astype(np.float32), language="th", beam_size=1,
                                  initial_prompt=ASR_PROMPT)
        text = "".join(s.text for s in segs).strip()
        # on noise Whisper may just repeat its prompt: drop that
        return "" if sum(w in text for w in ASR_PROMPT.split()) >= 3 else text
else:
    log("loading ASR (Typhoon Whisper Turbo, transformers fp16)...")
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline  # noqa: E402

    asr_dtype = torch.float16 if args.asr_device == "cuda" else torch.float32
    _mdir = str(ROOT / "downloads" / "models" / "typhoon-whisper-turbo")
    _asr_model = AutoModelForSpeechSeq2Seq.from_pretrained(_mdir, torch_dtype=asr_dtype, low_cpu_mem_usage=True,
                                                           use_safetensors=True).to(args.asr_device)
    _proc = AutoProcessor.from_pretrained(_mdir)
    asr = pipeline("automatic-speech-recognition", model=_asr_model, tokenizer=_proc.tokenizer,
                   feature_extractor=_proc.feature_extractor, chunk_length_s=30, torch_dtype=asr_dtype,
                   device=args.asr_device)

    def transcribe(audio16k):
        return asr({"raw": audio16k.astype(np.float32), "sampling_rate": SR},
                   generate_kwargs={"language": "thai"})["text"].strip()


log("loading TTS (ThonburianTTS)...")
TTS_DIR = ROOT / "downloads" / "models" / "ThonburianTTS"
tts = FlowTTSPipeline(
    model_config=ModelConfig(language="th", model_type="F5", checkpoint=str(TTS_DIR / "mega_f5_last.safetensors"),
                             vocab_file=str(TTS_DIR / "mega_vocab.txt"), vocoder="vocos", device=args.tts_device),
    audio_config=AudioConfig(silence_threshold=-45, cfg_strength=2.5, speed=1.0, nfe_step=args.nfe),
    temp_dir=str(OUT / "tmp"))
ref_text = args.ref_text
if not ref_text:
    a, sr = sf.read(args.ref_voice, dtype="float32", always_2d=True)
    import librosa
    ref_text = transcribe(librosa.resample(a.mean(axis=1), orig_sr=sr, target_sr=SR))
log(f"ref voice transcript: {ref_text}")
if torch.cuda.is_available():
    log(f"GPU memory held by voice service: {torch.cuda.memory_allocated() / 1024**2:.0f} MiB")

# ------------------------------------------------------------------ keeper link
k = KeeperLink()
speaking = threading.Event()
state = {"mode": "ptt", "ptt": False, "level": 0.0}


def set_status(text):
    try:
        k.set("VoiceStatus", text)
    except Exception:  # noqa: BLE001
        pass


def clean_for_tts(text):
    text = re.sub(r"<[^>]+>", " ", text)          # stray tags
    text = re.sub(r"[\*\#_`~]", " ", text)
    # laughs stay in the bubble but are not spoken: the voice model cannot laugh, it reads "เหอะๆ" as the syllables
    text = LAUGH_RE.sub(" ", text)
    # the voice model does not know the repeat mark ("หึๆ" came out as "หึงหยี"): write the word twice ("ติดๆ" -> "ติด ติด")
    text = expand_repeat(text)
    return re.sub(r"\s+", " ", text).strip(" ,")


_LAUGH = r"(?:หึ|เหอะ|แหะ|ฮ่า|ฮึ|เฮอะ)"
# a repeated laugh ("หึๆ", "เหอะ เหอะ") or a lone one between spaces; "ไปเหอะ" (= let's go) is kept
LAUGH_RE = re.compile(_LAUGH + r"(?:\s*ๆ|\s*" + _LAUGH + r")+(?![ก-๙])|(?<![ก-๙])" + _LAUGH + r"(?![ก-๙])")


def expand_repeat(text):
    if "ๆ" not in text:
        return text
    from pythainlp.tokenize import word_tokenize  # loaded once, only when needed
    out = []
    for part in re.split(r"(\s*ๆ)", text):
        if part.strip() == "ๆ":
            words = word_tokenize(out[-1] if out else "", engine="newmm") if out else []
            words = [w for w in words if w.strip()]
            if words:
                out.append(" " + words[-1])
            continue
        out.append(part)
    return "".join(out)


# ------------------------------------------------------------------ speech pipeline
# watch_loop reads the keeper's reply WHILE the LLM streams it and cuts off finished phrases (Thai marks phrase ends
# with a space), synth_loop turns phrases into audio ahead of time, play_loop plays them in order and writes each
# phrase to the keeper's SpeakLine as it starts, so the bubble shows exactly what is being said.
synth_q = queue.Queue()  # (utterance id, phrase)
play_q = queue.Queue()   # (utterance id, phrase, audio, sample rate)
inflight = [0]           # phrases queued or playing
inflight_lock = threading.Lock()
FIRST_MIN, NEXT_MIN = 8, 45  # chars: short first phrase = he starts talking sooner; longer later ones sound better


def cut_phrases(text, first):
    """Split finished phrases off the front of text. Returns (phrases, rest)."""
    out = []
    while True:
        need = FIRST_MIN if first and not out else NEXT_MIN
        cut = next((m for m in re.finditer(r"\s+|(?<=[.!?…])", text) if m.start() >= need), None)
        if cut is None:
            return out, text
        out.append(text[:cut.start()])
        text = text[cut.end():]


def split_for_speech(text):
    """Whole reply known: cut it in two so piece 2 is synthesized while piece 1 plays (no gap) and he starts
    sooner. Measured on the laptop: TTS ~2 s fixed + ~0.35 s per second of audio, speech ~11 Thai chars/s, so piece 1
    should be ~(22 + 0.35 * len) / 1.35 chars. Cut at the space nearest to that."""
    if len(text) <= 30:
        return [text]
    target = (22 + 0.35 * len(text)) / 1.35
    spaces = [m for m in re.finditer(r"\s+", text) if 12 <= m.start() <= len(text) - 8]
    cut = min(spaces, key=lambda m: abs(m.start() - target), default=None)
    return [text] if cut is None else [text[:cut.start()], text[cut.end():]]


def queue_phrase(utt, phrase):
    phrase = clean_for_tts(phrase)
    if len(phrase) < 2:
        return
    with inflight_lock:
        inflight[0] += 1
    speaking.set()
    synth_q.put((utt, phrase))


def watch_loop():
    utt, last_id, last_text, consumed, done, t_start = 0, None, "", 0, True, 0.0
    while True:
        try:
            if not k.path:
                if not k.find(timeout=2):
                    time.sleep(1)
                    continue
                k.set("VoiceOn", True)
                last_id = None
            rid, text = k.get("ReplyId"), k.get("ReplyText") or ""
            if last_id is None:  # (re)connected: don't speak whatever was already on screen
                last_id, last_text, consumed, done = rid, text, len(text), True
            if done and (rid != last_id or text != last_text):
                utt, consumed, done, t_start = utt + 1, 0, False, time.time()
            elif not done and not text.startswith(last_text[:consumed]):
                consumed = 0  # reply was replaced mid-stream (tool call): start over
            if not done and (args.stream or rid != last_id):
                final = rid != last_id
                pending = text[consumed:]
                if args.stream:
                    phrases, rest = cut_phrases(pending, first=(consumed == 0))
                    if final:
                        phrases.append(rest)
                        rest = ""
                else:
                    phrases, rest = split_for_speech(pending), ""
                for p in phrases:
                    if consumed == 0:
                        log(f"first phrase {time.time() - t_start:.1f}s after the question")
                    queue_phrase(utt, p)
                    consumed = len(text) - len(rest)
                if final:
                    log(f"KEEPER: {text}")
                    done, last_id = True, rid
            last_text = text
        except Exception as e:  # noqa: BLE001  (PIE stopped / restarted)
            k.path = None
            last_id = None
            log(f"(waiting for game: {type(e).__name__})")
            time.sleep(1)
        time.sleep(0.05)


def synth_loop():
    n = 0
    while True:
        utt, phrase = synth_q.get()
        n += 1
        wav = OUT / f"reply_{n % 8}.wav"
        t0 = time.time()
        try:
            tts(text=phrase, ref_voice=args.ref_voice, ref_text=ref_text, output_file=str(wav), speed=args.speed)
            data, sr = sf.read(str(wav), dtype="float32")
        except Exception as e:  # noqa: BLE001
            log(f"TTS failed ({type(e).__name__}): {phrase}")
            data, sr = np.zeros(1600, dtype="float32"), 16000
        # give cached TTS memory back to the GPU: each new phrase length cached more, the service grew to ~1.6 GB
        # over a session, the 8 GB laptop card filled and the LLM slowed to ~1 syllable/s (2026-10-21)
        torch.cuda.empty_cache()
        log(f"TTS {time.time() - t0:.1f}s for {len(data) / sr:.1f}s "
            f"(GPU held {torch.cuda.memory_reserved() / 1024**2:.0f} MiB): {phrase}")
        play_q.put((utt, phrase, data, sr))


def play_loop():
    shown_utt, shown = None, ""
    while True:
        utt, phrase, data, sr = play_q.get()
        shown = f"{shown} {phrase}".strip() if utt == shown_utt else phrase
        shown_utt = utt
        try:
            k.set("SpeakLine", shown)  # bubble + chat log update exactly when this phrase starts
        except Exception:  # noqa: BLE001
            pass
        set_status("ลุงบุญกำลังพูด")
        # silent tail: starting the next piece stops the stream while the sound card still holds the last ~0.3 s,
        # which clipped the end of every first piece; the tail is what gets cut instead
        # silent lead-in too: after a pause the sound device wakes up late and swallowed the first word
        # (loopback test 2026-10-20: "เปรต" missing from "เปรตตัวสูง...")
        data = np.concatenate([np.zeros(int(sr * 0.25), dtype=data.dtype), data,
                               np.zeros(int(sr * 0.45), dtype=data.dtype)])
        sd.play(data, sr)
        sd.wait()
        state["spoke_at"] = time.time()
        with inflight_lock:
            inflight[0] -= 1
            idle = inflight[0] == 0
        if idle:
            time.sleep(0.3)  # let the room echo die before listening again
            with inflight_lock:
                if inflight[0] == 0:
                    speaking.clear()
                    set_status("")


def poll_loop():
    """Mirror the in-game mic controls and push the level meter."""
    while True:
        try:
            if k.path:
                state["mode"] = (k.get("MicMode") or "ptt").lower()
                state["ptt"] = bool(k.get("PTTDown"))
                state["busy"] = bool(k.get("Busy"))
                k.set("MicLevel", 0.0 if speaking.is_set() else min(1.0, state["level"] * 6))
        except Exception:  # noqa: BLE001
            pass
        time.sleep(0.08)


audio_q = queue.Queue()


def on_audio(indata, frames, t, status):
    audio_q.put(indata[:, 0].copy())


WAKE = [w.strip() for w in args.wake.split(",") if w.strip()]


def wake_ok(text):
    """Always-on filter: send only lines addressed to the keeper (contain ลุง / บุญ), or replies shortly after he
    spoke (e.g. "ครับ" to his confirmation question). Stops him answering classroom chatter."""
    if not WAKE:
        return True
    if time.time() - state.get("spoke_at", 0.0) <= args.followup:
        return True
    return any(w in text for w in WAKE)


GHOST_WORDS = "กระสือ|กระหัง|ปอบ|โพง|กองกอย|ตายโหง|เปรต|ตานี|ไทย|ตัว|อะไร|ที่|ใน|มี|จริง|ป่า|น่ากลัว"


# near-misses of the ghost names heard in class tests (tone marks and similar consonants swapped)
ASR_ALIASES = [
    (r"ก(?:ระ|ะ)?[สซศ]ื[่้]?อ", "กระสือ"),          # กระซื้อ กระสื่อ กะสือ
    (r"(?<=ดู)ก็[สซ]ื[่้]?อ", "กระสือ"),            # ดูก็สื่อ
    (r"[ผพ]ี่?\s*เป(?:ร)?[๊็่้]?[ดตทกส]", "ผีเปรต"),  # ผีเป๊ก พี่เปรด
    (r"(?<=นาง)ตานี[้่]", "ตานี"),                   # นางตานี้
    (r"กระ[หฮ]ั?[่้]?ง[่้]?", "กระหัง"),
    (r"กอง\s*ก[่้]?อย", "กองกอย"),
]


def fix_asr(text):
    """ASR often hears ผี (rising tone) as พี่ (falling); a kid talking to ลุง about ghosts means ผี."""
    for pat, word in ASR_ALIASES:
        text = re.sub(pat, word, text)
    text = re.sub(r"(เรื่อง|เห็น|กลัว|เป็น)พี่", r"\1ผี", text)
    return re.sub(rf"พี่(?=\s*(?:{GHOST_WORDS}))", "ผี", text)


def send_text(text):
    if not text or len(text) < 2:
        set_status("ไม่ได้ยิน ลองพูดใหม่อีกที")
        return
    fixed = fix_asr(text)
    if fixed != text:
        log(f"(asr fix) {text} -> {fixed}")
        text = fixed
    log(f"YOU: {text}")
    try:
        k.set("PendingInput", text)
    except Exception as e:  # noqa: BLE001  (Play stopped: drop this line, watch_loop re-finds the keeper)
        log(f"(not sent, game not running: {type(e).__name__})")
        k.path = None
        return
    set_status("")


def mic_loop():
    buf, recording, silence_ms, voiced_ms = [], False, 0, 0
    with sd.InputStream(samplerate=SR, channels=1, dtype="float32", blocksize=BLOCK, callback=on_audio):
        log("mic open. In game: hold V to talk, press M to switch push-to-talk / always-on / off.")
        while True:
            block = audio_q.get()
            rms = float(np.sqrt(np.mean(block ** 2)))
            state["level"] = rms
            # muted while he thinks or talks: no second question piles onto the GPU, no hearing himself
            if speaking.is_set() or state.get("busy") or state["mode"] == "off":
                buf, recording, silence_ms, voiced_ms = [], False, 0, 0
                continue
            if state["mode"] == "ptt":
                if state["ptt"]:
                    if not recording:
                        set_status("กำลังฟัง...")
                    recording = True
                    buf.append(block)
                elif recording:
                    recording = False
                    audio = np.concatenate(buf)
                    buf = []
                    if len(audio) > SR * 0.4:
                        set_status("กำลังแปลงเสียง...")
                        t0 = time.time()
                        text = transcribe(audio)
                        log(f"ASR {time.time() - t0:.1f}s for {len(audio) / SR:.1f}s")
                        send_text(text)
            else:  # always-on: simple energy VAD with a little pre-roll and hang-over
                if rms > args.open_threshold:
                    voiced_ms += 50
                    silence_ms = 0
                    if not recording and voiced_ms >= 150:
                        recording = True
                        set_status("กำลังฟัง...")
                else:
                    silence_ms += 50
                    if not recording:
                        voiced_ms = 0
                buf.append(block)
                if not recording:
                    buf = buf[-6:]  # 300 ms pre-roll
                elif silence_ms >= args.end_silence or len(buf) * 50 > 15000:
                    recording = False
                    audio = np.concatenate(buf)
                    buf, voiced_ms = [], 0
                    if len(audio) > SR * 0.6:
                        set_status("กำลังแปลงเสียง...")
                        text = transcribe(audio)
                        if wake_ok(text):
                            send_text(text)
                        else:
                            log(f"(ignored, no wake word): {text}")
                            set_status("")


log("waiting for the keeper (press Play in Unreal)...")
k.find(timeout=3600)
log(f"connected: {k.path}")
k.set("VoiceOn", True)
for target in (watch_loop, synth_loop, play_loop):
    threading.Thread(target=target, daemon=True).start()
threading.Thread(target=poll_loop, daemon=True).start()

if args.selftest:
    import librosa
    for i, line in enumerate(args.selftest.split("|")):
        while speaking.is_set() or k.get("Busy"):
            time.sleep(0.3)
        time.sleep(1.0)
        wav = OUT / f"selftest_{i}.wav"
        tts(text=line, ref_voice=args.ref_voice, ref_text=ref_text, output_file=str(wav), speed=1.0)
        a, sr = sf.read(str(wav), dtype="float32", always_2d=True)
        t0 = time.time()
        heard = transcribe(librosa.resample(a.mean(axis=1), orig_sr=sr, target_sr=SR))
        log(f"SELFTEST said: {line} | ASR heard ({time.time() - t0:.1f}s): {heard}")
        send_text(heard)
        time.sleep(3.0)
        for _ in range(2):  # twice: the reply finishes a moment before the watcher queues its speech
            while speaking.is_set() or k.get("Busy"):
                time.sleep(0.3)
            time.sleep(1.0)
    time.sleep(15)
    log("SELFTEST done")
    sys.exit(0)
try:
    mic_loop()
finally:  # closing with Ctrl+C: let the keeper show text again without waiting for a voice
    try:
        k.set("VoiceOn", False)
    except Exception:  # noqa: BLE001
        pass

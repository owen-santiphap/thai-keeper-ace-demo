# ลุงบุญ: a Thai cemetery keeper you can talk to (NVIDIA ACE + Unreal Engine)

Course demo for **GI282 Disruptive Innovation, Week 10: Digital Human and Real-time Production**
(Bangkok University, Game & Interactive Media).

You walk through a Halloween cemetery in Unreal Engine and **speak Thai**. The keeper, ลุงบุญ, answers
**out loud in Thai**, tells local folklore ghosts from a lore file (กระสือ, นางตานี, กองกอย, เปรต, ...), says
"ไม่เคยได้ยิน" about ghosts he does not know, and can light the lantern, open the gate or walk you to a ghost
**after asking you to confirm**.

Everything runs **locally on one NVIDIA RTX GPU**, no cloud service:

    you speak Thai --> Typhoon Whisper (ASR) --+
                                               |  Unreal Remote Control (127.0.0.1)
    keeper speaks  <-- ThonburianTTS (Thai TTS) <-- Python voice service <--> BP_Keeper + NVIDIA ACE LLM (Typhoon 2.5 4B)

## What is in this repo (and what is not)

| In the repo | |
|---|---|
| `04_keeper/` | The keeper's prompts (current: **G**), lore sources + answer key, 13 Thai test questions, tool definitions, model comparison |
| `05_voice_tests/voice_service.py` | The Thai voice loop (mic, ASR, wake word, TTS, link to Unreal) and its tests |
| `tools/` | Remote Control link, test runners, and the scripts used to build the Blueprints through Epic's UE 5.8 MCP |
| `unreal/` | Project settings to copy, and a **patch for the NVIDIA ACE LLM plugin** (crash fix + Thai text fix) |
| `scripts/setup_models.py` | Downloads and prepares the models |
| `docs/` | Setup, architecture, how the Unreal side works, troubleshooting, class exercises, licenses |

**Not in the repo on purpose:** model weights, NVIDIA's compiled plugin and SDK, MetaHuman and other Epic content,
the cemetery level and third-party art, and the Unreal project itself. Reasons are in `docs/LICENSES.md`.
You build the project locally with `docs/SETUP.md`; the keeper uses the free Manny mannequin unless you make
your own MetaHuman (`docs/METAHUMAN.md`).

## Requirements

- Windows 10/11, NVIDIA RTX GPU with **8 GB VRAM or more** (developed on an RTX 4060 Laptop 8 GB; plug the laptop in)
- Unreal Engine **5.8**, Visual Studio with the C++ workload, Python 3.12, Git, ~40 GB free disk
- A microphone and speakers/headphones (headphones avoid the keeper hearing himself)

## Quick start

1. Read `docs/SETUP.md` and follow it top to bottom (about 2 hours, mostly downloads).
2. Run the voice service: `run_voice.bat`, then press Play in Unreal.
3. Try the demo script: สวัสดีครับ, กระสือคืออะไรครับ, ช่วยจุดตะเกียงหน่อยครับ, ได้ครับ, พาผมไปดูกระสือหน่อยครับ.
4. Do the exercises in `docs/EXERCISES.md` (change the prompt, add a ghost, break the keeper on purpose).

## Honest status

This is a class demo built in about two weeks, not a product. Measured on the developer laptop: keeper reply
2-7 s, ASR 1.2 s per sentence, 5.6 to 7.2 GB VRAM in Play. Known rough edges are listed in
`docs/TROUBLESHOOTING.md`. Pieces not yet tested by a person are marked **untested** in the docs.
The setup scripts in this repo were assembled from the commands used during development and have not
been run from a clean machine.

## Credits and licenses

Original code, prompts and docs: MIT (`LICENSE`). Third-party software and models keep their own licenses
(`docs/LICENSES.md`); note that the ThonburianTTS model is **non-commercial** (CC BY-NC-SA 4.0).

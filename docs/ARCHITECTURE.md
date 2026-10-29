# Architecture

## Pieces

- **BP_Keeper (Blueprint) + ACE LLM component.** Holds the system prompt (prompt G), sends the visitor's text to the
  model, receives streamed tokens and tool calls, drives the speech bubble, chat log, gate, lantern and walking.
- **NVIDIA ACE LLM plugin** (llama.cpp based, runs on the GPU) loading `typhoon2.5-qwen3-4b-q4_k_m-tools.gguf`.
- **Python voice service** (`05_voice_tests/voice_service.py`): microphone -> voice activity -> Typhoon Whisper (CTranslate2
  int8) -> text -> Unreal; keeper reply text -> ThonburianTTS -> speakers. It also does the wake word.
- **Link.** The service talks to Unreal over **Unreal's Remote Control API on 127.0.0.1:30010**, using property
  read/write only (`tools/keeper_link.py`). It writes `PendingInput` on BP_Keeper and reads `ReplyText` when `ReplyId`
  changes. Remote Python and remote function calls stay disabled.

## Why it is built this way (decisions we made, and why)

1. **Thai needs external ASR/TTS.** NVIDIA's ACE ASR and TTS plugins do not do Thai, so Thai speech runs in Python.
   The ACE LLM plugin is used because it runs the Thai LLM on the GPU inside Unreal.
2. **Lore lives in the system prompt.** For 8 short ghost entries this is simplest and works. There is no Blueprint RAG
   in the plugin. Upgrade path: a Data Table of ghosts with keywords and send only the matching entry.
3. **Typhoon needs a chat template added.** The Typhoon GGUF has no `tokenizer.chat_template`, so tool definitions were never
   sent to the model and it never called tools. We write the official template into a copy of the file (`scripts/setup_models.py`).
4. **Confirmation is enforced in Blueprint, not trusted to the model.** The model reliably *asks* "จะให้ลุงเปิดประตูเลยไหม"
   but did not call the tool after "yes". The keeper's question sets a pending action; the next "yes" runs it.
5. **Walking uses waypoints, not a navmesh.** The navmesh did not generate at runtime without a hand-made bounds volume.
6. **Lighter rendering for 8 GB:** Lumen GI, Virtual Shadow Maps and ray tracing off.
7. **Patched ACE LLM plugin.** Two bugs in NVIDIA's source: (a) the inference task can be garbage-collected mid-answer
   (editor crash), (b) `FString(const char*)` widens UTF-8 bytes so Thai is garbled in Full Response and in tool arguments.
   Patch: `unreal/patches/ace_llm_gc_and_thai.patch` (45 lines, two files).

## VRAM budget (RTX 4060 Laptop, 8 GB, measured)

| | GB |
|---|---|
| Typhoon Q4_K_M loaded + Play | ~4.9 |
| Voice service (ASR + TTS), steady | ~0.7 allocated (about 1.2-1.9 held by the process) |
| Total in Play | ~5.6-7.2, peak 7.2 reported |

Q6_K writes slightly cleaner Thai but needs a 16 GB card. Close ComfyUI and other GPU apps. Plug in the charger: on
battery the GPU is capped and replies take about 20 s.

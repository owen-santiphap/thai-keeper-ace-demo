# CLAUDE.md (for students using Claude Code in this repo)

This repo is a class demo: a Thai-speaking cemetery keeper in Unreal Engine 5.8 using the NVIDIA ACE LLM plugin, a Thai LLM (Typhoon 2.5 Qwen3 4B),
Thai ASR (Typhoon Whisper) and Thai TTS (ThonburianTTS), all local. Start with README.md, docs/SETUP.md, docs/ARCHITECTURE.md.

Rules for help in this repo:
- Verify before asserting; mark anything unverified as unverified. Setup scripts were not run from a clean machine.
- Never commit models, plugins/binaries, MetaHuman or other Epic content, tokens, or the Unreal project folder (see docs/LICENSES.md and .gitignore).
- Thai must work end to end. Keep tool arguments ASCII. Streamed Partial Text is correct even without the plugin patch.
- Target 8 GB VRAM. Do not add features that need more without saying so.
- Do not restart the voice service while Unreal is in Play.
- Keep the Remote Control link on 127.0.0.1 only.

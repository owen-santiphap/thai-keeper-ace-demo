# Licenses and what we did not redistribute

This is a summary for students and teachers, not legal advice. Check the original pages before reusing anything.

| Item | License (as we read it) | In this repo? |
|---|---|---|
| This repo's code, prompts, docs | MIT (`LICENSE`) | yes |
| NVIDIA ACE LLM plugin source | Apache-2.0 (`LICENSE(Plugin).txt` inside NVIDIA's ACE_LLM zip) | only a small patch (`unreal/patches/`), no NVIDIA code or binaries otherwise |
| NVIGI SDK / compiled plugin DLLs | NVIDIA terms, see the zip | no, you download them from NVIDIA |
| Typhoon 2.5 Qwen3 4B (LLM) | Apache-2.0 plus the model card terms (read them) | no, downloaded by script |
| Typhoon Whisper Turbo (ASR) | MIT | no, downloaded by script |
| ThonburianTTS code | MIT | no, cloned by script |
| ThonburianTTS model weights | **CC BY-NC-SA 4.0: non-commercial, share-alike, attribution** | no, downloaded by script |
| Epic MetaHuman content | Epic content license: MetaHuman content "may only be used and shared as UE-Only Content", and Licensed Content may not be distributed in source format to third parties; a public repository counts as distribution (https://www.unrealengine.com/eula/content, sections 1, 3, 4) | **no**. Make your own, `docs/METAHUMAN.md` |
| Unreal template content (Manny, ThirdPerson) | Unreal Engine EULA | no, comes with the template you create |
| Poly Haven-style HDRI, palm pack, cat model, ghost art | not verified or not ours to relicense | **no** |

## Rules of thumb for this class

- Do not commit anything from `downloads/`, any `.gguf`, `.safetensors`, `.nemo`, or an Unreal project folder.
- The ThonburianTTS voice is non-commercial. Do not ship a product with it without checking with its authors.
- If you record a voice for the keeper, only use your own voice or someone who agreed in writing.
- Never commit tokens. A leaked token in a public repo must be treated as compromised and replaced.

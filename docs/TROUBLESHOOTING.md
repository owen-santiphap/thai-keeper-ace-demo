# Troubleshooting (every item happened to us)

| Problem | Cause and fix |
|---|---|
| Thai shows as boxes in the editor, log says "Could not find Glyph Index" | The default editor font has no Thai. We replaced the engine's Roboto font file (in the engine's Slate fonts folder) with `NotoSansThai-Regular.ttf` renamed to the Roboto file name. Back up the original first. In your own widgets, use a Font asset made from a Thai .ttf. |
| Thai text garbled (U+FFxx boxes) from the LLM | NVIDIA's plugin widens UTF-8 bytes in Full Response and tool arguments. Apply `unreal/patches/ace_llm_gc_and_thai.patch`. Without it, build the reply from the streamed **Partial Text** and keep tool arguments ASCII. |
| The model never calls tools | The Typhoon GGUF has no chat template, so tool definitions are not sent. Use the `-tools.gguf` made by `scripts/setup_models.py`. |
| Typhoon asks "do you want me to open the gate?", you say yes, nothing happens | Expected. Confirmation is enforced in Blueprint (`docs/UNREAL_BUILD.md`). |
| Editor crashed right after pressing Stop | NVIDIA's inference task can be garbage-collected mid-answer. The patch roots it. Also wait 5 s after a reply before Stop, and use one Play session in class. |
| Changed Max Context Size, nothing changed | The engine loads once per editor session. Restart the editor. "Destroy Engine on End Play" does nothing. |
| Parameters Schema Json invalid | Paste raw JSON; remove any markdown code fences. |
| System prompt gone after restart | You did not Compile and File > Save All before closing. |
| Replies take ~20 s | Laptop on battery: plug in. Close ComfyUI and other GPU apps. |
| "Video memory has been exhausted" in Play | Make sure only ONE voice service is running (two ate the GPU). The service empties the PyTorch cache after each line and caps the CTranslate2 cache. On 8 GB, keep Lumen/VSM/ray tracing off. |
| Editor hangs or crashes when you restart the voice service | Stop Play first, restart the service, then Play. Start the service before Play. |
| The keeper answers background chatter | Always-on mic only reacts to lines containing ลุง or บุญ (and for 15 s after he speaks). Raise `--open-threshold` (default 0.04), change `--wake`, or use push-to-talk (hold V). |
| Keeper says a laugh like "หึงหยี" | ๆ after laughs is expanded in the service; other ๆ is dropped. |
| Windows unzip takes forever on NVIDIA's zip | Use 7-Zip. |
| Q6_K model runs out of VRAM with the voice service | Use Q4_K_M on 8 GB. Q6_K writes cleaner Thai but fits only a 16 GB card. |

## Things not verified yet

- The keeper's direct tool-call path (model calls a tool directly, Blueprint turns it into a confirmation question): **untested**, Typhoon never did it.
- Wake word and mic switching with several people in a real classroom: tested on recorded classroom lines, not live in Play.
- The setup scripts from a clean machine.

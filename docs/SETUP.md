# Setup (Windows)

Plan about 2 hours, mostly downloads. Do the steps in order. If a step fails, copy the error text; do not skip ahead.

## 0. What you need installed

1. NVIDIA driver, current.
2. Unreal Engine **5.8** (Epic Games Launcher > Library).
3. Visual Studio with the **"Game development with C++"** workload (needed once, to build the patched ACE plugin).
   Check Epic's page "Setting up Visual Studio for Unreal Engine" for the version your engine supports.
4. Python **3.12**, Git, 7-Zip.
5. Free disk: about 40 GB (models ~6 GB, plugin and engine intermediates, venv with CUDA PyTorch).

## 1. Get the repo

    git clone <this repo URL> thai-keeper-ace-demo
    cd thai-keeper-ace-demo

## 2. Python environment for the voice service

    py -3.12 -m venv .venv-voice
    .\.venv-voice\Scripts\Activate.ps1
    # PyTorch WITH CUDA first (the default Windows wheel is CPU-only). Pick Windows / Pip / CUDA at
    # https://pytorch.org/get-started/locally/ and run the command it prints (torch + torchaudio).
    pip install -r requirements-voice.txt

Check the GPU is visible: `python -c "import torch; print(torch.cuda.is_available())"` must print `True`.

## 3. Download and prepare the models (about 6 GB)

    python scripts/setup_models.py

Each model prints OK or FAILED. Re-running skips finished downloads. See the header of the script for what it creates.
You can run one part: `--only llm`, `--only asr`, `--only tts`.

## 4. Check Thai listening on its own (no Unreal)

    python 05_voice_tests\test_thai_asr.py

Press Enter, speak a test question from `04_keeper/test_questions_th.md` (include a ghost name such as กระสือ), and see what the
model heard, how many seconds it took and how much GPU memory it used. Results are appended to `asr_results.txt`.
This only checks the ASR model. The full voice service (`run_voice.bat`) also needs Unreal running in Play, because it
talks to the keeper through Unreal's Remote Control API; `run_voice.bat --selftest "<Thai line>"` runs the spoken loop without a
microphone, but also needs Unreal in Play.

## 5. Create the Unreal project

1. Unreal Engine 5.8 > Games > **Third Person**, **Blueprint**, name it **TheKeepr_Demo**, location = the repo folder
   (so the project is `thai-keeper-ace-demo\TheKeepr_Demo`; it is git-ignored). Starter content off.
2. Close the editor.
3. Plugins enabled in the `.uproject`: `LLMPlugin` (step 6), `RemoteControl`, `PythonScriptPlugin`, `EditorScriptingUtilities`.
   Settings to copy are in `unreal/config_snippets.md`.

## 6. NVIDIA ACE LLM plugin, patched

NVIDIA's prebuilt plugins list UE 5.5 to 5.7, not 5.8, so on 5.8 you build it from source with our patch.

1. Download **ACE_LLM** (the "Character Intelligence (LLM)" plugin) from NVIDIA: https://developer.nvidia.com/ace-for-games.
   We used `ACE_LLM_5.7_v0.5.zip`. It contains `Source/` and the license. Extract with 7-Zip to a short path, e.g. `C:\ace\ACE_LLM`.
   (Windows' built-in unzip is very slow on this archive.)
2. Apply the patch (Git Bash or `git apply` from inside the extracted plugin folder):

       cd C:\ace\ACE_LLM
       git apply --directory=Source <path-to-repo>\unreal\patches\ace_llm_gc_and_thai.patch

   (If `git apply` complains outside a git repo, use `patch -p1 -d Source < ...` from Git Bash.) The patch was checked to apply cleanly to the v0.5 source.
3. In `LLMPlugin.uplugin` set `"EngineVersion": "5.8.0"`.
4. Build it for your engine (Visual Studio required):

       "C:\Program Files\Epic Games\UE_5.8\Engine\Build\BatchFiles\RunUAT.bat" BuildPlugin -Plugin="C:\ace\ACE_LLM\LLMPlugin.uplugin" -Package="C:\ace\out\ACE_LLM_5.8" -TargetPlatforms=Win64 -Rocket

5. Copy `C:\ace\out\ACE_LLM_5.8` to `TheKeepr_Demo\Plugins\ACE_LLM_5.8`. If NVIDIA's zip has a `ThirdParty` folder or DLLs
   that the packaged output lacks, copy them from the original plugin folder as well.
6. Copy `downloads\models\typhoon2.5-qwen3-4b-q4_k_m-tools.gguf` into `TheKeepr_Demo\Plugins\`.
7. Open the project. In **Project Settings > Plugins > NVIDIA ACE LLM** set the model file to `../Plugins/typhoon2.5-qwen3-4b-q4_k_m-tools.gguf`
   and add the three tools from `04_keeper/tools_registered.md` / `unreal/config_snippets.md`.

## 7. Thai text in the Unreal editor

The default editor font has no Thai (you see boxes). Fix: replace the engine's Roboto font file with a Thai font renamed
as Roboto, as described in `docs/TROUBLESHOOTING.md` ("Thai shows as boxes"). In your own UMG widgets use a Font asset made
from a Thai `.ttf` (for example Noto Sans Thai, SIL OFL).

## 8. Build the keeper

Follow `docs/UNREAL_BUILD.md`. It is the part this repo cannot ship as ready-made assets.

## 9. Run

1. **Plug in the charger.** Close other GPU apps.
2. Double-click `run_voice.bat` and wait until it reports the models are loaded.
3. Open the project and press Play. Start the voice service **before** Play; to restart it, stop Play first
   (restarting it during Play crashed the editor once).
4. Enter = type, hold V = push-to-talk, M = mic mode. In always-on mode say ลุง or บุญ first ("ลุงครับ กระสือคืออะไร").

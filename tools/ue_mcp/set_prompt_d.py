"""Push a keeper prompt from 04_keeper to BP_Keeper's KeeperLLM (class default AND the placed instance in
/Game/Maps/Cemetery, which keeps its own copy) and save both.
Usage: python set_prompt_d.py [file name in 04_keeper]   (default keeper_prompt_E_spoken_th.txt)"""
from pathlib import Path as _P
REPO_ROOT = _P(__file__).resolve().parents[2]
import sys

from bpkit import comp_ref, compile_save, set_props
from ue import ASSET, call, ref

name = sys.argv[1] if len(sys.argv) > 1 else "keeper_prompt_E_spoken_th.txt"
with open(str(REPO_ROOT / "04_keeper" / name), encoding="utf-8-sig") as f:
    prompt = f.read().strip()
set_props(comp_ref("/Game/Keeper/BP_Keeper", "KeeperLLM"), {"systemPrompt": prompt})
print("bp saved:", compile_save("/Game/Keeper/BP_Keeper"))
set_props(ref("/Game/Maps/Cemetery.Cemetery:PersistentLevel.BP_Keeper_C_0.KeeperLLM"), {"systemPrompt": prompt})
print("level saved:", call(ASSET, "save_assets", asset_paths=["/Game/Maps/Cemetery"]))
print("prompt:", name)

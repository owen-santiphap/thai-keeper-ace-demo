"""Ask BP_KeeperTest one question in PIE and print what happened.

Usage: python run_question.py "<Thai question>" [A|B]
Rewrites the OnLLMReady SendMessage text from keeper_graph.dsl, sets the system prompt
(A = guarded, B = unguarded), compiles, presses Play, prints new keeper/tool lines, stops Play.
Leaves the Blueprint with the last question/prompt used; run with the lantern line + A to reset.
"""
from pathlib import Path as _P
REPO_ROOT = _P(__file__).resolve().parents[2]
import json
import sys
import time

from ue import ASSET, BP, OBJ, call, ref

DEFAULT_Q = "ช่วยจุดตะเกียงหน่อยครับ"
PROMPTS = {
    "A": str(REPO_ROOT.joinpath('04_keeper', 'keeper_prompt_A_guarded_th.txt')),
    "B": str(REPO_ROOT.joinpath('04_keeper', 'keeper_prompt_B_unguarded_th.txt')),
    "C": str(REPO_ROOT.joinpath('04_keeper', 'keeper_prompt_C_storyteller_th.txt')),
}
SCENE = "editor_toolset.toolsets.scene.SceneTools"
APP = "EditorToolset.EditorAppToolset"
LOGS = "EditorToolset.LogsToolset"
PATTERN = "TOOL CALLED|ACTION:|ลุงบุญ|LLM ERROR|Keeper LLM ready"

question = sys.argv[1]
which = sys.argv[2] if len(sys.argv) > 2 else "A"

bp = ref("/Game/Keeper/BP_KeeperTest.BP_KeeperTest")
graph = ref("/Game/Keeper/BP_KeeperTest.BP_KeeperTest:EventGraph")
comp = ref("/Game/Keeper/BP_KeeperTest.BP_KeeperTest_C:KeeperLLM_GEN_VARIABLE")

with open("keeper_graph.dsl", encoding="utf-8") as f:
    code = f.read()
assert DEFAULT_Q in code
call(BP, "write_graph_dsl", graph=graph, code=code.replace(DEFAULT_Q, question))

with open(PROMPTS[which], encoding="utf-8-sig") as f:
    prompt = f.read().strip()
assert call(OBJ, "set_properties", instance=comp, values=json.dumps({"systemPrompt": prompt}, ensure_ascii=False))
call(BP, "compile_blueprint", blueprint=bp, warnings_as_errors=False)
call(ASSET, "save_assets", asset_paths=["/Game/Keeper/BP_KeeperTest"])

if not call(SCENE, "find_actors", name="BP_KeeperTest", tag="", collision_channels=[]):
    call(SCENE, "add_to_scene_from_asset", asset_path="/Game/Keeper/BP_KeeperTest", name="BP_KeeperTest",
         xform={"location": {"x": 0, "y": 0, "z": 100}})

if call(APP, "IsPIERunning"):
    call(APP, "StopPIE")
    time.sleep(2)


def lines():
    e = call(LOGS, "GetLogEntries", category="", pattern=PATTERN, maxEntries=300)
    return [x if isinstance(x, str) else json.dumps(x, ensure_ascii=False) for x in (e if isinstance(e, list) else str(e).splitlines())]


old = set(lines())
print(f"Q: {question}   prompt {which}")
t0 = time.time()
call(APP, "StartPIE", options={"bSimulate": False, "playMode": "PlayMode_InViewPort"})
done = False
while time.time() - t0 < 180 and not done:
    time.sleep(2)
    for s in lines():
        if s in old:
            continue
        old.add(s)
        msg = s.split("] ", 2)[-1] if "LogBlueprintUserMessages" in s else s
        print(f"  +{time.time() - t0:5.1f}s  {msg[:500]}")
        if "ลุงบุญ:" in s or "LLM ERROR" in s:
            done = True
# Give the plugin's worker threads time to finish before ending PIE: stopping right away
# has crashed the editor (LLMInferenceTask.cpp:119 touches a GC'd task on a worker thread).
time.sleep(5)
call(APP, "StopPIE")
print("  done" if done else "  TIMED OUT (180 s)")

"""Place BP_KeeperTest in the current level, start PIE, and report what the keeper did."""
import json
import re
import time

from ue import call, ref

SCENE = "editor_toolset.toolsets.scene.SceneTools"
APP = "EditorToolset.EditorAppToolset"
LOGS = "EditorToolset.LogsToolset"

print("level:", call(SCENE, "get_current_level"))
found = call(SCENE, "find_actors", name="BP_KeeperTest", tag="", collision_channels=[])
if not found:
    actor = call(SCENE, "add_to_scene_from_asset", asset_path="/Game/Keeper/BP_KeeperTest", name="BP_KeeperTest", xform={"location": {"x": 0, "y": 0, "z": 100}})
    print("placed:", actor)
else:
    print("already placed:", found)

if call(APP, "IsPIERunning"):
    call(APP, "StopPIE")
    time.sleep(2)
print("StartPIE:", call(APP, "StartPIE", options={"bSimulate": False, "playMode": "PlayMode_InViewPort"}))

PAT = r"TOOL CALLED|ACTION:|ลุงบุญ|LLM ERROR|Keeper LLM ready|LogACELLM"
deadline = time.time() + 240
seen = set()
done = False
while time.time() < deadline and not done:
    time.sleep(5)
    entries = call(LOGS, "GetLogEntries", category="", pattern="TOOL CALLED|ACTION:|ลุงบุญ|LLM ERROR|Keeper LLM ready|ACELLM", maxEntries=200)
    lines = entries if isinstance(entries, list) else str(entries).splitlines()
    for ln in lines:
        s = ln if isinstance(ln, str) else json.dumps(ln, ensure_ascii=False)
        if s not in seen:
            seen.add(s)
            print(s[:400])
        if "ลุงบุญ:" in s or "LLM ERROR" in s:
            done = True
print("finished" if done else "timed out after 240 s")

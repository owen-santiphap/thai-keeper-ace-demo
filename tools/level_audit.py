"""Level audit in PIE: light the lanterns, then have the keeper guide to each ghost, waiting for GhostsSeen to rise.
Saves editor screenshots to the folder given as argv[1]. Usage: python level_audit.py <out_dir>"""
import base64
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "ue_mcp"))
from keeper_link import KeeperLink  # noqa: E402
from ue import _SID, call  # noqa: E402
from ue_mcp import post  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
APP = "EditorToolset.EditorAppToolset"
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)


def shot(name):
    r, _ = post({"jsonrpc": "2.0", "id": 7, "method": "tools/call",
                 "params": {"name": "call_tool", "arguments": {"toolset_name": APP, "tool_name": "CaptureEditorImage",
                                                                "arguments": {}}}}, _SID)
    for c in r["result"]["content"]:
        data = c["data"] if c.get("type") == "image" else None
        if data is None:
            v = json.loads(c["text"])["returnValue"]
            data = v["image"]["data"] if "image" in v else v["data"]
        (OUT / f"{name}.png").write_bytes(base64.b64decode(data))
        return


def say(k, line, wait=60):
    rid = k.get("ReplyId")
    k.say(line)
    rid, reply = k.wait_reply(rid, wait)
    print(f"YOU : {line}\nKEEP: {reply}", flush=True)
    return reply


if call(APP, "IsPIERunning"):
    call(APP, "StopPIE")
    time.sleep(3)
call(APP, "StartPIE", options={"bSimulate": False, "playMode": "PlayMode_InViewPort"})
k = KeeperLink()
print("keeper:", k.find(60))
t = time.time()
while k.get("ReplyId") < 1 and time.time() - t < 90:
    time.sleep(0.5)
time.sleep(2)
shot("00_start_dark")
say(k, "ช่วยจุดไฟหน่อยครับ")
say(k, "ได้ครับ")
time.sleep(14)  # keeper walks to the gate lantern, then lights it
shot("01_lanterns_lit")
for name in ["กระสือ", "นางตานี", "ผีกองกอย", "เปรต"]:
    seen = k.get("GhostsSeen")
    say(k, f"พาผมไปดู{name}หน่อยครับ")
    say(k, "ไปเลยครับ")
    t0 = time.time()
    while k.get("GhostsSeen") == seen and time.time() - t0 < 90:
        time.sleep(0.5)
    ok = k.get("GhostsSeen") > seen
    print(f"  -> {name}: {'ARRIVED' if ok else 'DID NOT ARRIVE'} in {time.time() - t0:.0f}s, GhostsSeen={k.get('GhostsSeen')}",
          flush=True)
    time.sleep(1)
    shot(f"02_{len(name)}_{['krasue', 'tani', 'kong_koi', 'pret'][['กระสือ', 'นางตานี', 'ผีกองกอย', 'เปรต'].index(name)]}")
print("final GhostsSeen:", k.get("GhostsSeen"), flush=True)
time.sleep(5)  # let the plugin's worker thread finish before stopping Play (GC crash)
call(APP, "StopPIE")

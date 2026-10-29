"""Scripted conversation test of the keeper game in PIE (no mic): confirmation rule, gate, guide, lore."""
from pathlib import Path as _P
REPO_ROOT = _P(__file__).resolve().parents[1]
import sys
import time

sys.path.insert(0, str(REPO_ROOT.joinpath('tools', 'ue_mcp')))
from keeper_link import KeeperLink  # noqa: E402
from ue import call  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
APP = "EditorToolset.EditorAppToolset"
if call(APP, "IsPIERunning"):
    call(APP, "StopPIE")
    time.sleep(3)
call(APP, "StartPIE", options={"bSimulate": False, "playMode": "PlayMode_InViewPort"})
k = KeeperLink()
print("keeper:", k.find())
time.sleep(8)  # LLM load

LINES = sys.argv[1:] or ["สวัสดีครับลุง", "ช่วยเปิดประตูให้หน่อยครับ", "ครับ เปิดเลย",
                         "พาผมไปดูกระสือหน่อยครับ", "ไปเลยครับ", "นางตานีคืออะไรครับ"]
rid = k.get("ReplyId")
for line in LINES:
    while k.get("Busy"):
        time.sleep(0.3)
    t0 = time.time()
    k.say(line)
    rid, reply = k.wait_reply(rid, timeout=90)
    print(f"\nYOU : {line}\nKEEP: {reply}   ({time.time() - t0:.1f}s)")
    time.sleep(1.0)
    print(f"      ghosts_seen={k.get('GhostsSeen')}")
time.sleep(30)
print("\nfinal ghosts_seen:", k.get("GhostsSeen"))

time.sleep(5)
call(APP, "StopPIE")


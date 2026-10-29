"""Walk test: does the keeper ever cross the fence line (x=1000) while the gate is closed?
Runs scenarios in PIE (no mic), logs keeper position + gate state every 0.3 s.
Usage: python gate_walk_test.py [scenario ...]   scenarios: lantern, guide_<ghost>, gate"""
import json
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / "ue_mcp"))
import keeper_link  # noqa: E402
from keeper_link import KeeperLink  # noqa: E402
from ue import call  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
APP = "EditorToolset.EditorAppToolset"
NAMES = {"krasue": "กระสือ", "tani": "นางตานี", "kong_koi": "ผีกองกอย", "pret": "เปรต"}
SCEN = sys.argv[1:] or ["lantern", "guide_krasue", "guide_pret", "lantern", "guide_tani"]

if call(APP, "IsPIERunning"):
    call(APP, "StopPIE")
    time.sleep(3)
call(APP, "StartPIE", options={"bSimulate": False, "playMode": "PlayMode_InViewPort"})
k = KeeperLink()
path = k.find()
gate = path.replace("BP_Keeper_C_0", "BP_Gate_C_0")
root = path + ".CollisionCylinder"
k.set("MicMode", "off")
time.sleep(10)


def rd(obj, prop):
    r = keeper_link._put({"objectPath": obj, "access": "READ_ACCESS", "propertyName": prop})
    return r.get(prop, next(iter(r.values())))


log, stop = [], threading.Event()
problems = []


def watch():
    last = None
    while not stop.is_set():
        try:
            p = rd(root, "RelativeLocation")
            g = rd(gate, "IsOpen")
        except Exception as e:  # noqa: BLE001
            print("read error", e)
            time.sleep(1)
            continue
        x, y = p["X"], p["Y"]
        if last is not None and (last[0] - 1000) * (x - 1000) < 0 and not g:
            problems.append((round(time.time() - t0, 1), round(last[0]), round(last[1]), round(x), round(y)))
        if last is not None and (last[0] - 1000) * (x - 1000) < 0 and abs(y) > 150:
            problems.append(("crossed outside the gate opening", round(x), round(y)))
        last = (x, y)
        log.append((round(time.time() - t0, 1), round(x), round(y), g))
        time.sleep(0.3)


t0 = time.time()
th = threading.Thread(target=watch)
th.start()
rid = k.get("ReplyId")
for s in SCEN:
    if s == "lantern":
        lines = ["ลุงช่วยจุดไฟหน่อย", "ได้ครับ"]
    elif s == "gate":
        lines = ["ลุงช่วยเปิดประตูหน่อย", "ได้ครับ"]
    else:
        lines = [f"ลุงพาไปดู{NAMES[s[6:]]}หน่อย", "ไปเลยครับ"]
    for line in lines:
        while k.get("Busy"):
            time.sleep(0.3)
        k.say(line)
        rid, reply = k.wait_reply(rid, timeout=90)
        print(f"{time.time() - t0:6.1f}  YOU: {line}  KEEP: {reply}")
        time.sleep(2)
    t = time.time()
    while k.get("Walking") and time.time() - t < 60:
        time.sleep(0.5)
    print(f"{time.time() - t0:6.1f}  {s} done, keeper at {log[-1][1:3]} gate open={log[-1][3]}")
    time.sleep(3)
stop.set()
th.join()
call(APP, "StopPIE")
Path(__file__).with_name("gate_walk_log.json").write_text(json.dumps(log))
print("PROBLEMS:", problems or "none")

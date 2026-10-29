"""Ask the keeper a fixed set of open questions in one Play session, save replies + GPU memory for a model comparison.
Usage: python typo_run.py <label> <out.json>"""
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "ue_mcp"))
from keeper_link import KeeperLink  # noqa: E402
from ue import call  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
APP = "EditorToolset.EditorAppToolset"
QUESTIONS = ["สวัสดีลุง คืนนี้เป็นยังไงบ้าง", "เล่าเรื่องกระสือให้ฟังหน่อย", "กระหังหน้าตาเป็นยังไง", "ผีปอบมาจากไหน",
             "นางตานีชอบอะไร", "ทำไมคนโบราณไม่ปลูกกล้วยตานีใกล้บ้าน", "ผีโพงมีไฟที่ไหน", "ผีกองกอยร้องว่ายังไง",
             "ผีตายโหงคืออะไร", "เปรตหน้าตาเป็นยังไง", "ลุงกลัวผีมั้ย", "ลุงเฝ้าป่าช้านี้มากี่ปีแล้ว"]


def vram():
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True).stdout.strip()
    return int(out.splitlines()[0])


label, out_path = sys.argv[1], sys.argv[2]
if call(APP, "IsPIERunning"):
    call(APP, "StopPIE")
    time.sleep(3)
call(APP, "StartPIE", options={"bSimulate": False, "playMode": "PlayMode_InViewPort"})
k = KeeperLink()
k.find(60)
t = time.time()
while k.get("ReplyId") < 1 and time.time() - t < 90:
    time.sleep(0.5)
rows, peak = [], vram()
for q in QUESTIONS:
    rid = k.get("ReplyId")
    t0 = time.time()
    k.say(q)
    rid, reply = k.wait_reply(rid, 90)
    peak = max(peak, vram())
    rows.append({"q": q, "a": reply, "s": round(time.time() - t0, 1)})
    print(f"{q}\n  -> {reply} ({rows[-1]['s']}s)", flush=True)
    time.sleep(1)
time.sleep(5)
call(APP, "StopPIE")
Path(out_path).write_text(json.dumps({"label": label, "vram_peak_mib": peak, "rows": rows}, ensure_ascii=False, indent=1),
                          encoding="utf-8")
print("VRAM peak MiB:", peak)

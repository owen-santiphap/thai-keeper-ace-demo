"""Hallucination comparison on the real game keeper (BP_Keeper in /Game/Maps/Cemetery).

Usage: python run_hallu.py <model label> <prompt letter C|D> <repeats> "<q1>" "<q2>" ...
Sets the system prompt on the placed keeper in memory only (not saved), starts a fresh Play per question
(fresh chat history), asks by Remote Control, appends the answer to 04_keeper/hallucination_results.jsonl.
Afterwards run set_prompt_d.py to put prompt D back (it also saves).
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from keeper_link import KeeperLink  # noqa: E402
from bpkit import set_props  # noqa: E402
from ue import call, ref  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
APP = "EditorToolset.EditorAppToolset"
ROOT = Path(__file__).resolve().parents[2]
PROMPTS = {"C": "keeper_prompt_C_storyteller_th.txt", "D": "keeper_prompt_D_game_th.txt",
           "E": "keeper_prompt_E_spoken_th.txt", "F": "keeper_prompt_F_th.txt", "G": "keeper_prompt_G_th.txt"}
OUT = ROOT / "04_keeper" / "hallucination_results.jsonl"

model, which, reps, questions = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4:]
prompt = (ROOT / "04_keeper" / PROMPTS[which]).read_text(encoding="utf-8-sig").strip()
set_props(ref("/Game/Maps/Cemetery.Cemetery:PersistentLevel.BP_Keeper_C_0.KeeperLLM"), {"systemPrompt": prompt})

k = KeeperLink()
for q in questions:
    for rep in range(reps):
        if call(APP, "IsPIERunning"):
            call(APP, "StopPIE")
            time.sleep(3)
        call(APP, "StartPIE", options={"bSimulate": False, "playMode": "PlayMode_InViewPort"})
        time.sleep(2)
        k.find(60)
        t0 = time.time()
        while k.get("ReplyId") < 1 and time.time() - t0 < 90:  # greeting = LLM ready
            time.sleep(0.5)
        rid = k.get("ReplyId")
        t0 = time.time()
        k.say(q)
        rid, answer = k.wait_reply(rid, timeout=120)
        secs = round(time.time() - t0, 1)
        print(f"[{model} / prompt {which} / {rep + 1}] {q} ({secs}s)\n  {answer}", flush=True)
        with OUT.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"time": time.strftime("%Y-%m-%d %H:%M"), "model": model, "prompt": which,
                                "question": q, "answer": answer, "seconds": secs}, ensure_ascii=False) + "\n")
        time.sleep(5)  # let the plugin's worker thread finish before stopping Play (GC crash)
call(APP, "StopPIE")

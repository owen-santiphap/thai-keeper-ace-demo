"""Print keeper state changes (Remote Control) for a while: used to verify key presses during a live test.
Usage: python watch_keeper.py <seconds>"""
import sys
import time

from keeper_link import KeeperLink

sys.stdout.reconfigure(encoding="utf-8")
k = KeeperLink()
print("keeper:", k.find(60), flush=True)
props = ["MicMode", "PTTDown", "Busy", "LastPlayerLine", "ReplyId", "VoiceStatus", "PendingTool", "GhostsSeen"]
last = {}
end = time.time() + float(sys.argv[1] if len(sys.argv) > 1 else 120)
while time.time() < end:
    for p in props:
        try:
            v = k.get(p)
        except Exception:  # noqa: BLE001
            continue
        if last.get(p) != v:
            print(f"{time.strftime('%H:%M:%S')} {p} = {v!r}", flush=True)
            last[p] = v
    time.sleep(0.1)

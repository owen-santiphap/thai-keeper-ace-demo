"""Capture the level viewport from a camera position to a PNG.
Usage: python capture.py out.png x y z pitch yaw
"""
import base64
import json
import sys

from ue import _SID
from ue_mcp import post

out = sys.argv[1]
x, y, z, pitch, yaw = (float(v) for v in sys.argv[2:7])
xform = {"location": {"x": x, "y": y, "z": z}, "rotation": {"pitch": pitch, "yaw": yaw, "roll": 0}}
args = {"captureTransform": xform, "annotations": [], "bShowUI": False}
r, _ = post({"jsonrpc": "2.0", "id": 6, "method": "tools/call",
             "params": {"name": "call_tool", "arguments": {"toolset_name": "EditorToolset.EditorAppToolset",
                                                            "tool_name": "CaptureViewport", "arguments": args}}}, _SID)
for c in r.get("result", {}).get("content", []):
    data = None
    if c.get("type") == "image":
        data = c["data"]
    elif c.get("type") == "text":
        try:
            data = json.loads(c["text"])["returnValue"]["image"]["data"]
        except (ValueError, KeyError, TypeError):
            print(c["text"][:600])
    if data:
        with open(out, "wb") as f:
            f.write(base64.b64decode(data))
        print("saved", out)

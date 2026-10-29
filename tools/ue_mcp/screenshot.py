"""Save a screenshot of the whole editor (including the Play viewport) to a PNG. Usage: python screenshot.py out.png"""
import base64
import json
import sys

from ue import _SID
from ue_mcp import post

r, _ = post({"jsonrpc": "2.0", "id": 7, "method": "tools/call",
             "params": {"name": "call_tool", "arguments": {"toolset_name": "EditorToolset.EditorAppToolset",
                                                            "tool_name": "CaptureEditorImage", "arguments": {}}}}, _SID)
for c in r["result"]["content"]:
    if c.get("type") == "image":
        data = c["data"]
    else:
        v = json.loads(c["text"])["returnValue"]
        data = v["image"]["data"] if "image" in v else v["data"]
    with open(sys.argv[1], "wb") as f:
        f.write(base64.b64decode(data))
    print("saved", sys.argv[1])
    break

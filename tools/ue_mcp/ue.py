"""Helpers on top of ue_mcp.py: one session, call toolset tools, return parsed values."""
import json
import sys

from ue_mcp import post, session

sys.stdout.reconfigure(encoding="utf-8")
_SID = session()

BP = "editor_toolset.toolsets.blueprint.BlueprintTools"
ACTOR = "editor_toolset.toolsets.actor.ActorTools"
OBJ = "editor_toolset.toolsets.object.ObjectTools"
ASSET = "editor_toolset.toolsets.asset.AssetTools"


def ref(path):
    return {"refPath": path}


def call(toolset, tool, **args):
    res, _ = post({"jsonrpc": "2.0", "id": 9, "method": "tools/call",
                   "params": {"name": "call_tool",
                              "arguments": {"toolset_name": toolset, "tool_name": tool, "arguments": args}}},
                  _SID)
    if "result" not in res:
        raise RuntimeError(json.dumps(res, ensure_ascii=False))
    text = "".join(c.get("text", "") for c in res["result"].get("content", []))
    if res["result"].get("isError"):
        raise RuntimeError(f"{tool} failed: {text}")
    try:
        val = json.loads(text)
    except ValueError:
        return text
    return val.get("returnValue", val) if isinstance(val, dict) else val

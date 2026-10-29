"""Tiny client for Epic's Unreal MCP (http://127.0.0.1:8000/mcp).

Usage:
  python ue_mcp.py list [filter]          list tools (names + short descriptions)
  python ue_mcp.py schema <tool>          print one tool's full schema
  python ue_mcp.py call <tool> <json>     call a tool with JSON arguments ('@file.json' reads a file)
"""
import json
import sys
import urllib.request

URL = "http://127.0.0.1:8000/mcp"
HEADERS = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}


def post(body, sid=None):
    h = dict(HEADERS)
    if sid:
        h["Mcp-Session-Id"] = sid
    req = urllib.request.Request(URL, data=json.dumps(body).encode("utf-8"), headers=h, method="POST")
    with urllib.request.urlopen(req, timeout=600) as r:
        raw = r.read().decode("utf-8")
        new_sid = r.headers.get("Mcp-Session-Id") or sid
    if raw.lstrip().startswith("event:") or raw.lstrip().startswith("data:"):
        datas = [ln[5:].strip() for ln in raw.splitlines() if ln.startswith("data:")]
        raw = datas[-1] if datas else "{}"
    return (json.loads(raw) if raw.strip() else {}), new_sid


def session():
    _, sid = post({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                   "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                              "clientInfo": {"name": "claude-code-helper", "version": "1"}}})
    post({"jsonrpc": "2.0", "method": "notifications/initialized"}, sid)
    return sid


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    cmd = sys.argv[1]
    sid = session()
    if cmd in ("list", "schema"):
        res, _ = post({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, sid)
        tools = res["result"]["tools"]
        if cmd == "list":
            flt = sys.argv[2].lower() if len(sys.argv) > 2 else ""
            for t in tools:
                if flt in t["name"].lower() or flt in t.get("description", "").lower():
                    print("-", t["name"], ":", t.get("description", "")[:200].replace("\n", " "))
            print(len(tools), "tools")
        else:
            for t in tools:
                if t["name"] == sys.argv[2]:
                    print(json.dumps(t, indent=1, ensure_ascii=False))
    elif cmd == "call":
        arg = sys.argv[3] if len(sys.argv) > 3 else "{}"
        if arg.startswith("@"):
            with open(arg[1:], encoding="utf-8") as f:
                arg = f.read()
        res, _ = post({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                       "params": {"name": sys.argv[2], "arguments": json.loads(arg)}}, sid)
        if "result" in res:
            for c in res["result"].get("content", []):
                print(c.get("text", c))
            if res["result"].get("isError"):
                print("[isError]")
        else:
            print(json.dumps(res, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()

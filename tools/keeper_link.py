"""Text link to BP_Keeper during Play-In-Editor, over Unreal's Remote Control API (http://127.0.0.1:30010).

Python writes the keeper's PendingInput variable (the keeper's Tick passes it to Ask) and reads ReplyText when
ReplyId changes. No remote function calls or remote Python are needed: only property read/write on one actor.
"""
import http.client
import json
import threading
import time

RC_HOST, RC_PORT, RC_PATH = "127.0.0.1", 30010, "/remote/object/property"
EDITOR_PATH = "/Game/Maps/Cemetery.Cemetery:PersistentLevel.BP_Keeper_C_0"
_local = threading.local()  # one kept-alive connection per thread: ~0.1-0.3 s per call instead of ~1 s


def _put(body):
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    for attempt in range(2):
        conn = getattr(_local, "conn", None)
        if conn is None:
            conn = _local.conn = http.client.HTTPConnection(RC_HOST, RC_PORT, timeout=5)
        try:
            conn.request("PUT", RC_PATH, data, {"Content-Type": "application/json"})
            r = conn.getresponse()
            raw = r.read().decode("utf-8")
        except (OSError, http.client.HTTPException):
            conn.close()
            _local.conn = None
            if attempt:
                raise
            continue
        if r.status >= 400:
            raise RuntimeError(f"Remote Control {r.status}: {raw[:200]}")
        return json.loads(raw) if raw.strip() else {}


class KeeperLink:
    def __init__(self, path=None):
        self.path = path

    def find(self, timeout=60.0):
        """Find the keeper in the running PIE world (UEDPIE_<n>_ prefix)."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            for n in range(0, 4):
                p = EDITOR_PATH.replace("/Game/Maps/Cemetery.", f"/Game/Maps/UEDPIE_{n}_Cemetery.")
                try:
                    self.path = p
                    self.get("ReplyId")
                    return p
                except Exception:  # noqa: BLE001
                    pass
            time.sleep(1.0)
        self.path = None
        return None

    def get(self, prop):
        r = _put({"objectPath": self.path, "access": "READ_ACCESS", "propertyName": prop})
        return r[prop] if prop in r else next(iter(r.values()))

    def set(self, prop, value):
        _put({"objectPath": self.path, "access": "WRITE_TRANSACTION_ACCESS", "propertyName": prop,
              "propertyValue": {prop: value}})

    def say(self, text):
        self.set("PendingInput", text)

    def wait_reply(self, last_id, timeout=60.0):
        deadline = time.time() + timeout
        while time.time() < deadline:
            rid = self.get("ReplyId")
            if rid != last_id:
                return rid, self.get("ReplyText")
            time.sleep(0.3)
        return last_id, None

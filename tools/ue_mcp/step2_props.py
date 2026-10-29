from pathlib import Path as _P
REPO_ROOT = _P(__file__).resolve().parents[2]
import json

from ue import ASSET, BP, OBJ, call, ref

PROMPT_FILE = str(REPO_ROOT.joinpath('04_keeper', 'keeper_prompt_A_guarded_th.txt'))
with open(PROMPT_FILE, encoding="utf-8-sig") as f:
    prompt = f.read().strip()

comp = ref("/Game/Keeper/BP_KeeperTest.BP_KeeperTest_C:KeeperLLM_GEN_VARIABLE")
ok = call(OBJ, "set_properties", instance=comp, values=json.dumps({
    "systemPrompt": prompt,
    "maxContextSize": 4096,
    "bAutoInitialize": True,
    "bAutoCreateChat": True,
    "bSaveChatHistory": True,
    "bAutoRunTools": True,
}, ensure_ascii=False))
print("set_properties:", ok)
got = call(OBJ, "get_properties", instance=comp,
           properties=["systemPrompt", "maxContextSize", "bAutoInitialize", "bAutoCreateChat", "bAutoRunTools"])
got = json.loads(got) if isinstance(got, str) else got
sp = got.get("systemPrompt", "")
print("prompt chars set:", len(sp), "file chars:", len(prompt), "match:", sp == prompt)
print({k: v for k, v in got.items() if k != "systemPrompt"} if isinstance(got, dict) else got)

bp = ref("/Game/Keeper/BP_KeeperTest.BP_KeeperTest")
names = [v if isinstance(v, str) else v.get("name") for v in (call(BP, "list_variables", blueprint=bp) or [])]
if "ReplyText" not in str(names):
    call(BP, "add_variable", blueprint=bp, name="ReplyText", type_name="string")
print("variables:", call(BP, "list_variables", blueprint=bp))

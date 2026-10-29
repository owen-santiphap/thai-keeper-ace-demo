"""Wire Enter / V / M in BP_ThirdPersonPlayerController (replaces wire_keys.py).

Why: BP_Keeper is a Pawn possessed by an AI controller, so EnableInput on it fails
("LogPawn: Error: EnableInput can only be specified on a Pawn for its Controller") and its key nodes never fire.
The player controller always receives the player's keys, so the keys live here and call into the keeper:
  Enter pressed -> keeper.ChatW.FocusInput
  V pressed/released -> keeper.PTTDown = true/false
  M pressed -> keeper.CycleMicMode
Also removes the old key nodes + the EnableInput call from BP_Keeper. Safe to re-run.
"""
from bpkit import compile_save
from ue import BP, call, ref

PC = "/Game/ThirdPerson/Blueprints/BP_ThirdPersonPlayerController"
KP = "/Game/Keeper/BP_Keeper"
g = ref(f"{PC}.BP_ThirdPersonPlayerController:EventGraph")
kg = ref(f"{KP}.BP_Keeper:EventGraph")


def node(graph, type_id, x, y):
    return call(BP, "create_node", graph=graph, type_id=type_id, pos={"x": x, "y": y}, declaring_class=None)


def info(n):
    return call(BP, "get_node_infos", nodes=[n])[0]


def pin(n, name, out):
    i = info(n)
    pins = i["output_pins" if out else "input_pins"]
    for p in pins:
        if p["name"] == name:
            return p
    for p in pins:  # cast output is "AsBP Keeper" / "As BP Keeper" depending on version
        if p["name"].replace(" ", "").replace("_", "").lower() == name.replace(" ", "").replace("_", "").lower():
            return p
    raise KeyError(f"{name} not in {[p['name'] for p in i['input_pins'] + i['output_pins']]}")


def link(src, src_pin, dst, dst_pin):
    call(BP, "connect_pins", output_pin=pin(src, src_pin, True)["pin_id"], input_pin=pin(dst, dst_pin, False)["pin_id"])


def find_keys(graph, title):
    return call(BP, "find_nodes", graph=graph, title=title, node_class="/Script/BlueprintGraph.K2Node_InputKey",
                entry_points_only=False) or []


def delete_chain(n, seen=None):
    """Delete a node and everything hanging off it (exec + data), staying inside what we created."""
    seen = seen if seen is not None else set()
    key = n["refPath"]
    if key in seen:
        return
    seen.add(key)
    i = info(n)
    for p in i["output_pins"] + i["input_pins"]:
        for c in p.get("connected_pins", []):
            delete_chain(c["node"], seen)
    call(BP, "delete_node", node=n)


# 1) clean the controller (re-run safety): drop our key nodes and everything wired to them
for title in ("Enter", "V", "M"):
    for k in find_keys(g, title):
        delete_chain(k)


def keeper_cast(exec_src, exec_pin, x, y):
    """exec_src.exec_pin -> Cast(GetActorOfClass(BP_Keeper)); returns the cast node."""
    get = node(g, "Actor|GetActorOfClass", x, y + 120)
    call(BP, "set_pin_value", pin=pin(get, "ActorClass", False)["pin_id"], value="/Game/Keeper/BP_Keeper.BP_Keeper_C")
    cast = node(g, "Utilities|Casting|CastToBP_Keeper", x + 300, y)
    link(get, "ReturnValue", cast, "Object")
    link(exec_src, exec_pin, cast, "execute")
    return cast


y = 600
enter = node(g, "Input|KeyboardEvents|Enter", 0, y)
c = keeper_cast(enter, "Pressed", 250, y)
chatw = node(g, "Class|BPKeeper|GetChatW", 650, y + 150)
link(c, "AsBP_Keeper", chatw, "self")
focus = node(g, "Class|WBPChat|FocusInput", 900, y)
link(c, "then", focus, "execute")
link(chatw, "ChatW", focus, "self")

y = 1000
v = node(g, "Input|KeyboardEvents|V", 0, y)
for pname, val, dy in (("Pressed", "true", 0), ("Released", "false", 300)):
    c = keeper_cast(v, pname, 250, y + dy)
    s = node(g, "Class|BPKeeper|SetPTTDown", 900, y + dy)
    call(BP, "set_pin_value", pin=pin(s, "PTTDown", False)["pin_id"], value=val)
    link(c, "then", s, "execute")
    link(c, "AsBP_Keeper", s, "self")

y = 1700
m = node(g, "Input|KeyboardEvents|M", 0, y)
c = keeper_cast(m, "Pressed", 250, y)
cyc = node(g, "Class|BPKeeper|CycleMicMode", 900, y)
link(c, "then", cyc, "execute")
link(c, "AsBP_Keeper", cyc, "self")

print("controller saved:", compile_save(PC))

# 2) remove the dead key nodes and the failing EnableInput from BP_Keeper
for title in ("Enter", "V", "M"):
    for k in find_keys(kg, title):
        i = info(k)
        for p in i["output_pins"]:
            if p["name"] in ("Pressed", "Released"):
                for cp in p.get("connected_pins", []):
                    delete_chain(cp["node"])
        try:
            call(BP, "delete_node", node=k)
        except RuntimeError:
            pass  # already removed by delete_chain
for n in call(BP, "find_nodes", graph=kg, title="Enable Input", node_class=None, entry_points_only=False) or []:
    i = info(n)
    ins = {p["name"]: p for p in i["input_pins"]}
    outs = {p["name"]: p for p in i["output_pins"]}
    prev = ins["execute"]["connected_pins"]
    nxt = outs["then"]["connected_pins"]
    call(BP, "delete_node", node=n)
    for a in prev:
        for b in nxt:
            call(BP, "connect_pins", output_pin=a, input_pin=b)
print("keeper saved:", compile_save(KP))

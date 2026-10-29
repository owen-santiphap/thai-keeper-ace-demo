"""Hand-wire BP_Keeper key events (the DSL cannot author key-event nodes):
  Enter pressed -> ChatW.FocusInput
  V pressed -> PTTDown = true, V released -> PTTDown = false
  M pressed -> CycleMicMode
Safe to re-run: removes previously wired targets of these keys first.
"""
from bpkit import compile_save
from ue import BP, call, ref

P = "/Game/Keeper/BP_Keeper"
g = ref(f"{P}.BP_Keeper:EventGraph")


def node(type_id, x, y):
    return call(BP, "create_node", graph=g, type_id=type_id, pos={"x": x, "y": y}, declaring_class=None)


def info(n):
    return call(BP, "get_node_infos", nodes=[n])[0]


def pin(n, name, out):
    i = info(n)
    for p in i["output_pins" if out else "input_pins"]:
        if p["name"] == name:
            return p
    raise KeyError(f"{name} not in {[p['name'] for p in i['input_pins'] + i['output_pins']]}")


def key_node(title, type_id, y):
    found = call(BP, "find_nodes", graph=g, title=title, node_class="/Script/BlueprintGraph.K2Node_InputKey",
                 entry_points_only=False) or []
    k = found[0] if found else node(type_id, 0, y)
    for pname in ("Pressed", "Released"):  # drop whatever these exec pins drove before
        p = pin(k, pname, True)
        for c in p.get("connected_pins", []):
            call(BP, "delete_node", node=c["node"])
    return k


def link(src, src_pin, dst, dst_pin):
    call(BP, "connect_pins", output_pin=pin(src, src_pin, True)["pin_id"], input_pin=pin(dst, dst_pin, False)["pin_id"])


y = 3200
enter = key_node("Enter", "Input|KeyboardEvents|Enter", y)
focus = node("Class|WBPChat|FocusInput", 400, y)
getw = node("Variables|Default|GetChatW", 150, y + 150)
link(enter, "Pressed", focus, "execute")
link(getw, "ChatW", focus, "self")

y = 3600
v = key_node("V", "Input|KeyboardEvents|V", y)
for pname, val, dy in (("Pressed", "true", 0), ("Released", "false", 150)):
    s = node("Variables|Default|SetPTTDown", 400, y + dy)
    call(BP, "set_pin_value", pin=pin(s, "PTTDown", False)["pin_id"], value=val)
    link(v, pname, s, "execute")

y = 4000
m = key_node("M", "Input|KeyboardEvents|M", y)
cyc = node("CallFunction|CycleMicMode", 400, y)
link(m, "Pressed", cyc, "execute")

print("saved:", compile_save(P))
for title in ("Enter", "V", "M"):
    k = call(BP, "find_nodes", graph=g, title=title, node_class="/Script/BlueprintGraph.K2Node_InputKey",
             entry_points_only=False)[0]
    i = info(k)
    print(title, {p["name"]: [c["node"]["refPath"].rsplit(".", 1)[-1] for c in p.get("connected_pins", [])]
                  for p in i["output_pins"] if p["name"] in ("Pressed", "Released")})

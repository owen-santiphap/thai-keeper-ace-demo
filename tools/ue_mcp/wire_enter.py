"""Hand-wire BP_Keeper: Enter key (Pressed) -> ChatW.FocusInput (the DSL cannot author key-event nodes)."""
import json

from bpkit import compile_save
from ue import BP, call, ref

P = "/Game/Keeper/BP_Keeper"
g = ref(f"{P}.BP_Keeper:EventGraph")

keys = call(BP, "find_nodes", graph=g, title="Enter", node_class=None, entry_points_only=False) or []
key = keys[0] if keys else call(BP, "create_node", graph=g, type_id="Input|KeyboardEvents|Enter",
                                pos={"x": 0, "y": 3200}, declaring_class=None)
focus = call(BP, "create_node", graph=g, type_id="Class|WBPChat|FocusInput", pos={"x": 400, "y": 3200},
             declaring_class=None)
getw = call(BP, "create_node", graph=g, type_id="Variables|Default|GetChatW", pos={"x": 150, "y": 3350},
            declaring_class=None)
info = call(BP, "get_node_infos", nodes=[key, focus, getw])


def pin(node_info, name, direction):
    for p in node_info["output_pins" if direction == "out" else "input_pins"]:
        if p["name"] == name:
            return p["pin_id"]
    raise KeyError(f"{name} not in {[p['name'] for p in node_info['input_pins'] + node_info['output_pins']]}")


ki, fi, gi = info
print(call(BP, "connect_pins", output_pin=pin(ki, "Pressed", "out"), input_pin=pin(fi, "execute", "in")))
print(call(BP, "connect_pins", output_pin=pin(gi, "ChatW", "out"), input_pin=pin(fi, "self", "in")))
print("saved:", compile_save(P))
d = call(BP, "read_graph_dsl", graph=g)
print([l for l in d.splitlines() if "Enter" in l or "FocusInput" in l])

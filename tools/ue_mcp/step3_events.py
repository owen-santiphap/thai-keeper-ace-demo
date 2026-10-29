import json

from ue import BP, call, ref

comp = ref("/Game/Keeper/BP_KeeperTest.BP_KeeperTest_C:KeeperLLM_GEN_VARIABLE")
graph = ref("/Game/Keeper/BP_KeeperTest.BP_KeeperTest:EventGraph")

for ev in ["OnLLMReady", "OnTokenStreamed", "OnResponseComplete", "OnToolCalled", "OnLLMError"]:
    print(ev, "->", call(BP, "add_component_bound_event", component=comp, event_name=ev, graph=graph))

print("----- DSL now:")
print(call(BP, "read_graph_dsl", graph=graph))

for flt in ["Send Message", "Submit Tool Result", "Print String", "Append"]:
    types = call(BP, "find_node_types", graph=graph, type_id_filter=flt)
    print("=====", flt, json.dumps(types, ensure_ascii=False)[:700])

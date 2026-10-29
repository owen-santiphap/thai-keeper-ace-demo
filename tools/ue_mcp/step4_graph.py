from ue import ASSET, BP, call, ref

graph = ref("/Game/Keeper/BP_KeeperTest.BP_KeeperTest:EventGraph")
bp = ref("/Game/Keeper/BP_KeeperTest.BP_KeeperTest")

with open("keeper_graph.dsl", encoding="utf-8") as f:
    code = f.read()

print("write:", call(BP, "write_graph_dsl", graph=graph, code=code))
print("compile:", call(BP, "compile_blueprint", blueprint=bp, warnings_as_errors=False))
print("----- graph now:")
print(call(BP, "read_graph_dsl", graph=graph))
print("save:", call(ASSET, "save_assets", asset_paths=["/Game/Keeper/BP_KeeperTest"]))

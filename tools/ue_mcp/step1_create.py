from ue import ACTOR, ASSET, BP, call, ref

PATH = "/Game/Keeper/BP_KeeperTest"

if call(ASSET, "exists", path=PATH):
    print("BP already exists")
    bp = ref(PATH + ".BP_KeeperTest")
else:
    bp = call(BP, "create", folder_path="/Game/Keeper", asset_name="BP_KeeperTest",
              asset_type=ref("/Script/Engine.Actor"))
    print("created:", bp)

llm = call(ACTOR, "add_component", owner=bp, component_type=ref("/Script/LLMPlugin.ACELLMComponent"),
           name="KeeperLLM")
print("added component:", llm)
print("events:", call(BP, "list_component_events", component=llm))
print("graphs:", call(BP, "list_graphs", blueprint=bp))

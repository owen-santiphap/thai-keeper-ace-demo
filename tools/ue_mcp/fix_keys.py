"""Keys by polling (Owen 2026-10-21: Enter did nothing until the chat box was clicked).
The InputKey events in BP_ThirdPersonPlayerController never fired in PIE (UE 5.8, Enhanced Input project), so
BP_Keeper.HandleKeys asks the player controller every frame: Enter -> focus chat box, M -> cycle mic mode,
V held -> push-to-talk. The old InputKey nodes are deleted from the controller so M cannot toggle twice.
Note: BP_Keeper variables are in categories, so the DSL names them Variables|<category>|GetX."""
from bpkit import compile_save, prune_graph
from ue import BP, call, ref

P = "/Game/Keeper/BP_Keeper"
G = lambda n: ref(f"{P}.BP_Keeper:{n}")  # noqa: E731
try:
    call(BP, "get_graph", blueprint=ref(f"{P}.BP_Keeper"), graph_name="HandleKeys")
except RuntimeError:
    call(BP, "add_function_graph", blueprint=ref(f"{P}.BP_Keeper"), graph_name="HandleKeys")
call(BP, "write_graph_dsl", graph=G("HandleKeys"), code="""
(fn HandleKeys ()
  ; Enter = type to the keeper, M = change mic mode, hold V = push-to-talk
  (bind pc (Game|GetPlayerController :PlayerIndex 0))
  (if (Game|Player|WasInputKeyJustPressed :self pc :Key "Enter")
    (Class|WBPChat|FocusInput :self (Variables|5SceneandUI|GetChatW)))
  (if (Game|Player|WasInputKeyJustPressed :self pc :Key "M")
    (CallFunction|CycleMicMode))
  (bind v (Game|Player|IsInputKeyDown :self pc :Key "V"))
  (if (not (== v (Variables|2Voicelink|GetPTTDown)))
    (Variables|2Voicelink|SetPTTDown v)))
""")
call(BP, "write_graph_dsl", graph=G("UpdateMicBar"), code="""
(fn UpdateMicBar ()
  ; keys + mic level bar, status text and mode icon in the chat window
  (CallFunction|HandleKeys)
  (bind cw (Variables|5SceneandUI|GetChatW))
  (Utilities|IsValid cw
    (:"Is Valid"
      (Class|WBPChat|SetMic :self cw :Level (Variables|2Voicelink|GetMicLevel) :Label (CallFunction|MicLabel)))
    (:"Is Not Valid")))
""")
for g in ("HandleKeys", "UpdateMicBar"):
    print(g, prune_graph(G(g)))
    call(BP, "arrange_nodes", nodes=call(BP, "find_nodes", graph=G(g), title="", entry_points_only=False))
print("keeper saved:", compile_save(P))

PC = "/Game/ThirdPerson/Blueprints/BP_ThirdPersonPlayerController"
pg = ref(f"{PC}.BP_ThirdPersonPlayerController:EventGraph")
keys = [n for n in call(BP, "find_nodes", graph=pg, title="", entry_points_only=False) or []
        if "K2Node_InputKey" in n["refPath"]]
for n in keys:
    call(BP, "delete_node", node=n)
print("controller key nodes deleted:", len(keys), "pruned:", prune_graph(pg))
print("controller saved:", compile_save(PC))

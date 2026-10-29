"""BP_Keeper skeleton: Manny + ACE LLM (prompt D) + speech bubble widget + variables + Ask(Text) function."""
from pathlib import Path as _P
REPO_ROOT = _P(__file__).resolve().parents[2]
import json

from bpkit import add_comp, bp_ref, compile_save, ensure_bp, ensure_var, set_props
from ue import BP, OBJ, call, ref

P = "/Game/Keeper/BP_Keeper"
ensure_bp(P, "/Script/Engine.Character")
bp = bp_ref(P)
cdo = "/Game/Keeper/BP_Keeper.Default__BP_Keeper_C"

# inherited components on the class default object
set_props(ref(f"{cdo}:CharacterMesh0"), {
    "skeletalMeshAsset": "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple.SKM_Manny_Simple",
    "animClass": "/Game/Characters/Mannequins/Anims/Unarmed/ABP_Unarmed.ABP_Unarmed_C",
    "relativeLocation": {"x": 0, "y": 0, "z": -90},
    "relativeRotation": {"pitch": 0, "yaw": -90, "roll": 0},
})
set_props(ref(f"{cdo}:CharMoveComp"), {"maxWalkSpeed": 230.0, "bOrientRotationToMovement": True})
set_props(ref(cdo), {"bUseControllerRotationYaw": False, "autoPossessAI": "PlacedInWorldOrSpawned"})

with open(str(REPO_ROOT.joinpath('04_keeper', 'keeper_prompt_D_game_th.txt')), encoding="utf-8-sig") as f:
    prompt = f.read().strip()
add_comp(P, "/Script/LLMPlugin.ACELLMComponent", "KeeperLLM", None, {
    "systemPrompt": prompt, "maxContextSize": 4096, "bAutoInitialize": True, "bAutoCreateChat": True,
    "bSaveChatHistory": True, "bAutoRunTools": True})
add_comp(P, "/Script/UMG.WidgetComponent", "Bubble", None, {
    "widgetClass": "/Game/UI/WBP_Bubble.WBP_Bubble_C", "space": "Screen",
    "drawSize": {"x": 600, "y": 180}, "relativeLocation": {"x": 0, "y": 0, "z": 125},
    "pivot": {"x": 0.5, "y": 1.0}})

for name, t in [("ReplyText", "string"), ("PendingInput", "string"), ("LastPlayerLine", "string"),
                ("ReplyId", "int"), ("Busy", "bool"), ("GhostsSeen", "int")]:
    ensure_var(P, name, t)
for name in ("ReplyText", "PendingInput", "ReplyId", "Busy"):
    call(BP, "set_variable_instance_editable", blueprint=bp, variable_name=name, instance_editable=True)
ensure_var(P, "BubbleW", object_class="/Game/UI/WBP_Bubble.WBP_Bubble_C")
ensure_var(P, "Gate", object_class="/Game/Keeper/BP_Gate.BP_Gate_C")
ensure_var(P, "Lantern", object_class="/Game/Keeper/BP_Lantern.BP_Lantern_C")

ask = ref(f"{P}.BP_Keeper:Ask")
try:
    call(BP, "get_graph", blueprint=bp, graph_name="Ask")
except RuntimeError:
    call(BP, "add_function_graph", blueprint=bp, graph_name="Ask")
    call(BP, "add_function_param", graph=ask, param_name="Text", param_type="string", input_param=True)
print(compile_save(P))
print(call(OBJ, "get_properties", instance=ref(f"{cdo}:CharacterMesh0"), properties=["skeletalMeshAsset", "animClass"]))

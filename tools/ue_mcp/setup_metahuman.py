"""Hook the MetaHuman (BP_LungBoon child actor 'LungBoonMH') to BP_Keeper: Manny stays as the invisible animation
driver, the MetaHuman body copies its pose (leader pose; face/clothes/grooms follow the body inside BP_LungBoon).
Writes only SetupMetaHuman + SetupScene so the comment boxes in the other graphs stay aligned."""
from bpkit import bp_ref, compile_save, ensure_var, prune_graph, set_props
from ue import BP, call, ref

P = "/Game/Keeper/BP_Keeper"
ensure_var(P, "UseMetaHuman", "bool")  # untick in Details to fall back to Manny (e.g. if the laptop runs out of VRAM)
call(BP, "set_variable_instance_editable", blueprint=bp_ref(P), variable_name="UseMetaHuman", instance_editable=True)
G = lambda n: ref(f"{P}.BP_Keeper:{n}")  # noqa: E731
try:
    call(BP, "get_graph", blueprint=ref(f"{P}.BP_Keeper"), graph_name="SetupMetaHuman")
except RuntimeError:
    call(BP, "add_function_graph", blueprint=ref(f"{P}.BP_Keeper"), graph_name="SetupMetaHuman")
call(BP, "write_graph_dsl", graph=G("SetupMetaHuman"), code="""
(fn SetupMetaHuman ()
  ; Manny (Mesh) keeps playing the walk/idle animation but is hidden; the MetaHuman body copies its pose.
  ; To use another MetaHuman: change the class on the Set Child Actor Class node below.
  (if (not (Variables|Default|GetUseMetaHuman))
    (return))
  (bind m (Variables|Character|GetMesh))
  (Class|SkinnedMeshComponent|SetVisibilityBasedAnimTickOption :self m :VisibilityBasedAnimTickOption "AlwaysTickPoseAndRefreshBones")
  (Rendering|SetVisibility :self m :bNewVisibility false)
  ; set the class at runtime: the keeper placed in the level keeps its own (empty) copy of the component settings
  (ChildActorComponent|SetChildActorClass :self (Variables|Default|GetLungBoonMH) :InClass "/Game/Keeper/MetaHuman/Built/LungBoon/BP_LungBoon.BP_LungBoon_C")
  (bind mh (Utilities|Casting|CastToBP_LungBoon :Object (Class|ChildActorComponent|GetChildActor :self (Variables|Default|GetLungBoonMH)))
    (:then (Components|SkinnedMesh|SetLeaderPoseComponent :self (Class|BPLungBoon|GetBody :self mh) :NewLeaderBoneComponent m))
    (:CastFailed (Development|PrintString :InString "SETUP: MetaHuman missing, showing Manny")
      (Rendering|SetVisibility :self m :bNewVisibility true))))
""")
call(BP, "write_graph_dsl", graph=G("SetupScene"), code="""
(fn SetupScene ()
  ; at start: MetaHuman body, greeting, find the gate and the gate lantern, chat window
  (CallFunction|SetupMetaHuman)
  (CallFunction|ShowSpeech :Line "เดี๋ยวนะ ลุงเพิ่งตื่น ขอบิดขี้เกียจแป๊บ เหอะๆ")
  (CallFunction|FindGate)
  (CallFunction|FindGateLantern)
  (CallFunction|SetupChat))
""")
for g in ("SetupMetaHuman", "SetupScene"):
    print(g, prune_graph(G(g)))
    call(BP, "arrange_nodes", nodes=call(BP, "find_nodes", graph=G(g), title="", entry_points_only=False))
print("saved:", compile_save(P))
cdo = ref(f"{P}.Default__BP_Keeper_C")
set_props(cdo, {"UseMetaHuman": True})
lvl = ref("/Game/Maps/Cemetery.Cemetery:PersistentLevel.BP_Keeper_C_0")
set_props(lvl, {"UseMetaHuman": True})
print("saved:", compile_save(P), call("editor_toolset.toolsets.asset.AssetTools", "save_assets", asset_paths=["/Game/Maps/Cemetery"]))

"""Scary mood pass (Owen 2026-10-20): pitch-dark scene, paler (less yellow) lamps, thick fog, invisible boundary walls,
sugar-palm blockouts replaced by Owen's palm model (/Game/free-game-ready-palm/source/Palm). Saves the level."""
import json

from bpkit import set_props
from ue import ASSET, OBJ, call, ref

SCENE = "editor_toolset.toolsets.scene.SceneTools"
ACTOR = "editor_toolset.toolsets.actor.ActorTools"
L = "/Game/Maps/Cemetery.Cemetery:PersistentLevel."


def find(name):
    return call(SCENE, "find_actors", name=name, tag="", collision_channels=[]) or []


# 1. palms: remove the basic-shape sugar palms, keep Owen's placed Palm, add a second one at the other spot
for a in find("SugarPalm"):
    call(SCENE, "remove_from_scene", actor=a)
palms = [a for a in find("Palm") if call(ACTOR, "get_label", actor=a).startswith("Palm")]
print("palms placed by Owen:", [call(ACTOR, "get_label", actor=a) for a in palms])
if len(palms) < 2:
    call(SCENE, "add_to_scene_from_asset", asset_path="/Game/free-game-ready-palm/source/Palm", name="Palm_2",
         xform={"location": {"x": 2520, "y": 1420, "z": 0}, "rotation": {"pitch": 0, "yaw": 47, "roll": 0},
                "scale": {"x": 0.27, "y": 0.27, "z": 0.27}})

# 2. pitch dark
set_props(ref(L + "DirectionalLight_0.LightComponent0"), {"intensity": 0.15})
set_props(ref(L + "HDRIBackdrop_C_0"), {"Intensity": 0.04})

# 3. paler lamps (warm white instead of yellow-orange)
PALE = {"r": 255, "g": 226, "b": 190, "a": 255}
for cls in ["BP_LightPole_C_", "BP_Lantern_C_"]:
    for i in range(12):
        try:
            set_props(ref(f"{L}{cls}{i}.Light"), {"lightColor": PALE})
        except RuntimeError:
            pass
for bp in ["/Game/Keeper/BP_LightPole.BP_LightPole_C:Light_GEN_VARIABLE",
           "/Game/Keeper/BP_Lantern.BP_Lantern_C:Light_GEN_VARIABLE"]:
    try:
        set_props(ref(bp), {"lightColor": PALE})
    except RuntimeError as e:
        print("class default not set:", bp, str(e)[:120])

# 4. thick, dark fog
set_props(ref(L + "ExponentialHeightFog_0.HeightFogComponent0"), {
    "fogDensity": 0.12, "fogHeightFalloff": 0.25, "startDistance": 0.0,
    "fogInscatteringLuminance": {"r": 0.012, "g": 0.016, "b": 0.026, "a": 1.0},
    "bEnableVolumetricFog": True, "volumetricFogExtinctionScale": 2.0})

# 5. invisible walls around the play area (village approach + ป่าช้า)
for label, loc, scale in [("Bound_North", (1700, 1850, 200), (56, 0.5, 6)),
                          ("Bound_South", (1700, -1850, 200), (56, 0.5, 6)),
                          ("Bound_West", (-1050, 0, 200), (0.5, 38, 6)),
                          ("Bound_East", (4450, 0, 200), (0.5, 38, 6))]:
    for a in find(label):
        call(SCENE, "remove_from_scene", actor=a)
    w = call(SCENE, "add_to_scene_from_asset", asset_path="/Engine/BasicShapes/Cube", name=label,
             xform={"location": dict(zip("xyz", loc)), "scale": dict(zip("xyz", scale))})
    set_props(ref(w["refPath"] + ".StaticMeshComponent0"), {"bHiddenInGame": True, "castShadow": False})

print("level saved:", call(ASSET, "save_assets", asset_paths=["/Game/Maps/Cemetery"]))

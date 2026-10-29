"""Place gate, lantern, keeper and the 4 ghost spots in /Game/Maps/Cemetery and save the level."""
import json

from ue import ASSET, OBJ, call

SCENE = "editor_toolset.toolsets.scene.SceneTools"
assert call(SCENE, "get_current_level") == "/Game/Maps/Cemetery", "Cemetery level must be open"


def place(asset, name, x, y, z, yaw=0.0):
    found = call(SCENE, "find_actors", name=name, tag="", collision_channels=[])
    for a in found or []:
        call(SCENE, "remove_from_scene", actor=a)
    return call(SCENE, "add_to_scene_from_asset", asset_path=asset, name=name,
                xform={"location": {"x": x, "y": y, "z": z}, "rotation": {"pitch": 0, "yaw": yaw, "roll": 0}})


place("/Game/Keeper/BP_Gate", "Gate", 1000, 0, 0)
place("/Game/Keeper/BP_Lantern", "Lantern", 700, -330, 0)
place("/Game/Keeper/BP_Keeper", "Keeper_LungBoon", 700, 220, 100, yaw=180)
for gid, x, y in (("krasue", 2000, -1100), ("tani", 3550, -1050), ("kong_koi", 3550, 1050), ("pret", 2000, 1150)):
    a = place("/Game/Keeper/BP_GhostSpot", f"GhostSpot_{gid}", x, y, 0)
    call(OBJ, "set_properties", instance=a, values=json.dumps({"GhostId": gid}))
    print(gid, call(OBJ, "get_properties", instance=a, properties=["GhostId"]))
print("save:", call(ASSET, "save_assets", asset_paths=["/Game/Maps/Cemetery"]))

"""Create the empty /Game/UI/Fonts/F_Thai Font asset (typeface is filled in through MCP afterwards)."""
import os

import unreal

LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "make_font.log")
eal = unreal.EditorAssetLibrary
msgs = []
path = "/Game/UI/Fonts/F_Thai"
if not eal.does_asset_exist(path):
    font = unreal.AssetToolsHelpers.get_asset_tools().create_asset("F_Thai", "/Game/UI/Fonts", unreal.Font,
                                                                   unreal.FontFactory())
    msgs.append(f"created {font}")
font = eal.load_asset(path)
try:
    font.set_editor_property("font_cache_type", unreal.FontCacheType.RUNTIME)
except Exception as e:  # noqa: BLE001
    msgs.append(f"cache type: {e}")
msgs.append(f"saved: {eal.save_asset(path)}")
msgs.append("DONE")
with open(LOG, "w", encoding="utf-8") as f:
    f.write("\n".join(msgs) + "\n")

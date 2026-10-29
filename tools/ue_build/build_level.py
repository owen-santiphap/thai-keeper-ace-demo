"""Editor Python build step for the keeper demo (run with UnrealEditor ... -ExecutePythonScript=<this file>).

Creates (idempotent where practical):
  /Game/UI/Fonts/NotoSansThai (FontFace) + /Game/UI/Fonts/F_Thai (Font, default=NotoSansThai, fallback=Roboto)
  /Game/Materials/MI_* colour instances of BasicShapeMaterial
  /Game/Maps/Cemetery level: night lighting, fog, ground, fenced yard (gate gap on the west side),
  gravestones, decor for the 4 ghost spots, PlayerStart, NavMeshBoundsVolume.
Interactive actors (gate, lantern, ghost spots, keeper) are added later as Blueprints.
Log: tools/ue_build/build_level.log
"""
import os
import traceback

import unreal

LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_level.log")
open(LOG, "w", encoding="utf-8").close()


def log(msg):
    unreal.log(f"[build_level] {msg}")
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(str(msg) + "\n")


at = unreal.AssetToolsHelpers.get_asset_tools()
eal = unreal.EditorAssetLibrary


# ---------------------------------------------------------------- font
def build_font():
    face_path = "/Game/UI/Fonts/NotoSansThai"
    if not eal.does_asset_exist(face_path):
        task = unreal.AssetImportTask()
        task.filename = r"C:\Program Files\Epic Games\UE_5.8\Engine\Content\Slate\Fonts\NotoSansThai-Regular.ttf"
        task.destination_path = "/Game/UI/Fonts"
        task.destination_name = "NotoSansThai"
        task.automated = True
        task.save = True
        task.replace_existing = True
        at.import_asset_tasks([task])
        log(f"font import -> {list(task.imported_object_paths)}")
    face = eal.load_asset(face_path)
    log(f"font face: {face} ({type(face).__name__})")
    if not isinstance(face, unreal.FontFace):
        log("WARNING: imported object is not a FontFace")
        return

    font_path = "/Game/UI/Fonts/F_Thai"
    font = eal.load_asset(font_path) if eal.does_asset_exist(font_path) else \
        at.create_asset("F_Thai", "/Game/UI/Fonts", unreal.Font, unreal.FontFactory())
    try:
        font.set_editor_property("font_cache_type", unreal.FontCacheType.RUNTIME)
        cf = font.get_editor_property("composite_font")
        entry = unreal.TypefaceEntry()
        entry.set_editor_property("name", "Regular")
        fd = entry.get_editor_property("font")
        fd.set_editor_property("font_face_asset", face)
        entry.set_editor_property("font", fd)
        tf = cf.get_editor_property("default_typeface")
        tf.set_editor_property("fonts", [entry])
        cf.set_editor_property("default_typeface", tf)
        # Latin / digits fall back to the engine Roboto face
        roboto = eal.load_asset("/Engine/EngineFonts/Faces/RobotoRegular")
        if roboto:
            fb = cf.get_editor_property("fallback_typeface")
            fbt = fb.get_editor_property("typeface")
            fe = unreal.TypefaceEntry()
            fe.set_editor_property("name", "Regular")
            ffd = fe.get_editor_property("font")
            ffd.set_editor_property("font_face_asset", roboto)
            fe.set_editor_property("font", ffd)
            fbt.set_editor_property("fonts", [fe])
            fb.set_editor_property("typeface", fbt)
            cf.set_editor_property("fallback_typeface", fb)
        font.set_editor_property("composite_font", cf)
        eal.save_asset(font_path)
        log("F_Thai composite font set (default NotoSansThai, fallback Roboto)")
    except Exception as e:  # noqa: BLE001
        log(f"WARNING font setup: {e}")


# ---------------------------------------------------------------- materials
BASE_MAT = "/Engine/BasicShapes/BasicShapeMaterial"
COLORS = {
    "MI_Ground": (0.035, 0.05, 0.03),
    "MI_Stone": (0.22, 0.22, 0.24),
    "MI_DarkStone": (0.08, 0.08, 0.09),
    "MI_Wood": (0.16, 0.08, 0.035),
    "MI_Leaf": (0.03, 0.12, 0.03),
    "MI_Banana": (0.05, 0.22, 0.04),
    "MI_TempleRed": (0.35, 0.04, 0.03),
    "MI_Gold": (0.6, 0.42, 0.08),
}


def build_materials():
    base = eal.load_asset(BASE_MAT)
    mel = unreal.MaterialEditingLibrary
    out = {}
    for name, rgb in COLORS.items():
        path = f"/Game/Materials/{name}"
        mi = eal.load_asset(path) if eal.does_asset_exist(path) else at.create_asset(
            name, "/Game/Materials", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        mel.set_material_instance_parent(mi, base)
        mel.set_material_instance_vector_parameter_value(mi, "Color", unreal.LinearColor(*rgb, 1.0))
        eal.save_asset(path)
        out[name] = mi
    log(f"materials: {list(out)}")
    return out


# ---------------------------------------------------------------- level
MESH = {
    "cube": "/Engine/BasicShapes/Cube",
    "cyl": "/Engine/BasicShapes/Cylinder",
    "cone": "/Engine/BasicShapes/Cone",
    "sphere": "/Engine/BasicShapes/Sphere",
    "plane": "/Engine/BasicShapes/Plane",
}


def try_set(obj, prop, value):
    try:
        obj.set_editor_property(prop, value)
    except Exception as e:  # noqa: BLE001
        log(f"  (skip {type(obj).__name__}.{prop}: {e})")


def spawn_mesh(label, mesh, loc, scale, mat, rot=(0, 0, 0), folder="Decor"):
    a = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*loc),
                                                         unreal.Rotator(roll=rot[0], pitch=rot[1], yaw=rot[2]))
    smc = a.static_mesh_component
    smc.set_static_mesh(eal.load_asset(MESH[mesh]))
    smc.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
    a.set_actor_scale3d(unreal.Vector(*scale))
    if mat is not None:
        smc.set_material(0, mat)
    a.set_actor_label(label)
    a.set_folder_path(folder)
    return a


def spawn(cls, label, loc, rot=(0, 0, 0), folder="Lighting"):
    a = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(*loc),
                                                         unreal.Rotator(roll=rot[0], pitch=rot[1], yaw=rot[2]))
    a.set_actor_label(label)
    a.set_folder_path(folder)
    return a


def build_level(m):
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    path = "/Game/Maps/Cemetery"
    if eal.does_asset_exist(path):
        les.load_level(path)
        for a in unreal.EditorLevelLibrary.get_all_level_actors():
            unreal.EditorLevelLibrary.destroy_actor(a)
        log("existing Cemetery level cleared")
    else:
        les.new_level(path)
        log("new level /Game/Maps/Cemetery")

    # --- lighting / atmosphere (night)
    moon = spawn(unreal.DirectionalLight, "Moon", (0, 0, 1000), rot=(0, -35, 140))
    lc = moon.get_component_by_class(unreal.DirectionalLightComponent)
    try_set(lc, "intensity", 0.6)
    try_set(lc, "light_color", unreal.Color(r=150, g=170, b=255, a=255))
    try_set(lc, "atmosphere_sun_light", True)
    spawn(unreal.SkyAtmosphere, "SkyAtmosphere", (0, 0, 0))
    sky = spawn(unreal.SkyLight, "SkyLight", (0, 0, 300))
    sc = sky.get_component_by_class(unreal.SkyLightComponent)
    try_set(sc, "real_time_capture", True)
    try_set(sc, "intensity", 0.6)
    try_set(sc, "mobility", unreal.ComponentMobility.MOVABLE)
    fog = spawn(unreal.ExponentialHeightFog, "Fog", (0, 0, 0))
    fc = fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
    try_set(fc, "fog_density", 0.06)
    try_set(fc, "fog_inscattering_luminance", unreal.LinearColor(0.02, 0.025, 0.05, 1))
    try_set(fc, "enable_volumetric_fog", True)
    pp = spawn(unreal.PostProcessVolume, "PostProcess", (0, 0, 0))
    try_set(pp, "unbound", True)
    s = pp.get_editor_property("settings")
    try_set(s, "override_auto_exposure_method", True)
    try_set(s, "auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL)
    try_set(s, "override_auto_exposure_apply_physical_camera_exposure", True)
    try_set(s, "auto_exposure_apply_physical_camera_exposure", False)
    try_set(s, "override_auto_exposure_bias", True)
    try_set(s, "auto_exposure_bias", 1.0)
    try_set(pp, "settings", s)
    # --- ground
    spawn_mesh("Ground", "plane", (1500, 0, 0), (80, 80, 1), m["MI_Ground"], folder="Ground")

    # --- fenced yard: x 1000..4200, y -1600..1600, gate gap 500 wide at x=1000, y=-250..250
    H = 2.2  # wall height in metres (scale z)
    def wall(label, x0, y0, x1, y1):
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        sx, sy = max(abs(x1 - x0) / 100, 0.3), max(abs(y1 - y0) / 100, 0.3)
        spawn_mesh(label, "cube", (cx, cy, H * 50), (sx, sy, H), m["MI_DarkStone"], folder="Yard")
    wall("Wall_West_N", 1000, 250, 1000, 1600)
    wall("Wall_West_S", 1000, -1600, 1000, -250)
    wall("Wall_North", 1000, 1600, 4200, 1600)
    wall("Wall_South", 1000, -1600, 4200, -1600)
    wall("Wall_East", 4200, -1600, 4200, 1600)

    # --- gravestones (rows in the middle of the yard, leaving paths)
    n = 0
    for x in range(1700, 3700, 350):
        for y in (-450, -200, 200, 450):
            n += 1
            spawn_mesh(f"Grave_{n:02d}", "cube", (x, y, 60), (0.25, 0.7, 1.2), m["MI_Stone"], folder="Graves")
    # --- decor per ghost spot
    # krasue (2000,-1100): thorny fence pieces
    for i, (x, y) in enumerate([(1800, -1300), (2000, -1350), (2200, -1300)]):
        spawn_mesh(f"Krasue_Thorns_{i}", "cone", (x, y, 50), (0.4, 0.4, 1.0), m["MI_Wood"], folder="Spot_krasue")
    # tani (3600,-1100): wild banana clump with cloth
    for i, (x, y) in enumerate([(3800, -1350), (3900, -1200), (3700, -1400)]):
        spawn_mesh(f"Tani_Banana_{i}", "cyl", (x, y, 150), (0.35, 0.35, 3.0), m["MI_Banana"], folder="Spot_tani")
        spawn_mesh(f"Tani_Leaves_{i}", "sphere", (x, y, 330), (1.4, 1.4, 0.6), m["MI_Leaf"], folder="Spot_tani")
    # kong_koi (3600,1100): forest edge, tall trees
    for i, (x, y) in enumerate([(3850, 1350), (3650, 1450), (4000, 1150), (3450, 1400)]):
        spawn_mesh(f"KongKoi_Trunk_{i}", "cyl", (x, y, 200), (0.4, 0.4, 4.0), m["MI_Wood"], folder="Spot_kong_koi")
        spawn_mesh(f"KongKoi_Crown_{i}", "cone", (x, y, 500), (2.2, 2.2, 3.0), m["MI_Leaf"], folder="Spot_kong_koi")
    # pret (2000,1100): temple wall with mural (red + gold)
    spawn_mesh("Pret_TempleWall", "cube", (2000, 1450, 200), (6.0, 0.4, 4.0), m["MI_TempleRed"], folder="Spot_pret")
    spawn_mesh("Pret_Roof", "cube", (2000, 1450, 430), (7.0, 1.2, 0.4), m["MI_Gold"], folder="Spot_pret")

    # --- outside the gate: path and player start
    spawn_mesh("Path", "cube", (300, 0, 1), (16.0, 4.0, 0.02), m["MI_Stone"], folder="Ground")
    spawn(unreal.PlayerStart, "PlayerStart", (-600, 0, 120), folder="Gameplay")

    # --- navmesh
    nav = spawn(unreal.NavMeshBoundsVolume, "NavMeshBounds", (1600, 0, 100), folder="Gameplay")
    nav.set_actor_scale3d(unreal.Vector(30, 20, 4))

    unreal.EditorLevelLibrary.save_current_level()
    log(f"level built and saved: {len(unreal.EditorLevelLibrary.get_all_level_actors())} actors")


try:
    build_font()
except Exception:  # noqa: BLE001
    log("FONT FAILED\n" + traceback.format_exc())
try:
    mats = build_materials()
    build_level(mats)
except Exception:  # noqa: BLE001
    log("LEVEL FAILED\n" + traceback.format_exc())
log("DONE")

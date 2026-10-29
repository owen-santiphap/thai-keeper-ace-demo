"""BP_Lantern (event LightLantern) and BP_GhostSpot (var GhostId, event Reveal)."""
from bpkit import add_comp, bp_ref, compile_save, ensure_bp, ensure_var, read_graph, set_props, write_graph
from ue import BP, call

SM = "/Script/Engine.StaticMeshComponent"
SC = "/Script/Engine.SceneComponent"
PL = "/Script/Engine.PointLightComponent"
CYL = "/Engine/BasicShapes/Cylinder.Cylinder"
SPH = "/Engine/BasicShapes/Sphere.Sphere"
CONE = "/Engine/BasicShapes/Cone.Cone"


def ensure_event(path, name, y=400):
    have = [e["name"] for e in call(BP, "list_events", blueprint=bp_ref(path))]
    if name not in have:
        call(BP, "add_event", blueprint=bp_ref(path), event_name=name, position={"x": 0, "y": y})


# ---------------- lantern
L = "/Game/Keeper/BP_Lantern"
ensure_bp(L, "/Script/Engine.Actor")
add_comp(L, SC, "Root")
add_comp(L, SM, "Post", "Root", {"staticMesh": CYL, "overrideMaterials": ["/Game/Materials/MI_Wood.MI_Wood"],
                                 "relativeLocation": {"x": 0, "y": 0, "z": 90},
                                 "relativeScale3D": {"x": 0.12, "y": 0.12, "z": 1.8}})
add_comp(L, SM, "Lamp", "Root", {"staticMesh": SPH, "overrideMaterials": ["/Game/Materials/MI_Gold.MI_Gold"],
                                 "relativeLocation": {"x": 0, "y": 0, "z": 195},
                                 "relativeScale3D": {"x": 0.3, "y": 0.3, "z": 0.4}})
add_comp(L, PL, "Light", "Root", {"mobility": "Movable", "intensity": 0.0, "attenuationRadius": 1800.0,
                                  "lightColor": {"r": 255, "g": 170, "b": 90, "a": 255},
                                  "relativeLocation": {"x": 0, "y": 0, "z": 200}})
ensure_var(L, "IsLit", "bool")
ensure_event(L, "LightLantern")
compile_save(L)
write_graph(L, """
(event Custom|LightLantern
  (Variables|Default|SetIsLit true)
  (Rendering|Components|Light|SetIntensity :self (Variables|Default|GetLight) :NewIntensity 60.0))
""")
compile_save(L)
print(read_graph(L))

# ---------------- ghost spot
G = "/Game/Keeper/BP_GhostSpot"
ensure_bp(G, "/Script/Engine.Actor")
add_comp(G, SC, "Root")
add_comp(G, SM, "Marker", "Root", {"staticMesh": CYL, "overrideMaterials": ["/Game/Materials/MI_Stone.MI_Stone"],
                                   "relativeLocation": {"x": 0, "y": 0, "z": 15},
                                   "relativeScale3D": {"x": 1.2, "y": 1.2, "z": 0.3}})
add_comp(G, SM, "Ghost", "Root", {"staticMesh": CONE, "bHiddenInGame": True,
                                  "relativeLocation": {"x": 0, "y": 0, "z": 150},
                                  "relativeScale3D": {"x": 0.7, "y": 0.7, "z": 1.8},
                                  "relativeRotation": {"pitch": 180, "yaw": 0, "roll": 0}})
add_comp(G, SM, "GhostHead", "Ghost", {"staticMesh": SPH, "bHiddenInGame": True, "relativeLocation": {"x": 0, "y": 0, "z": -45},
                                       "relativeScale3D": {"x": 0.9, "y": 0.9, "z": 0.45}})
add_comp(G, PL, "GhostLight", "Root", {"mobility": "Movable", "intensity": 0.0, "attenuationRadius": 900.0,
                                       "lightColor": {"r": 120, "g": 255, "b": 200, "a": 255},
                                       "relativeLocation": {"x": 0, "y": 0, "z": 220}})
ensure_var(G, "GhostId", "string")
ensure_var(G, "Revealed", "bool")
call(BP, "set_variable_instance_editable", blueprint=bp_ref(G), variable_name="GhostId", instance_editable=True)
ensure_event(G, "Reveal")
compile_save(G)
write_graph(G, """
(event Custom|Reveal
  (Variables|Default|SetRevealed true)
  (Development|SetHiddeninGame :self (Variables|Default|GetGhost) :NewHidden false :bPropagateToChildren true)
  (Rendering|Components|Light|SetIntensity :self (Variables|Default|GetGhostLight) :NewIntensity 40.0))
""")
compile_save(G)
print(read_graph(G))

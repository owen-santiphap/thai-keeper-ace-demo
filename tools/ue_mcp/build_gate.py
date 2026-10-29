"""BP_Gate: two posts + two hinged doors. Custom event OpenGate swings both doors inward."""
from bpkit import add_comp, compile_save, ensure_bp, ensure_var, read_graph, write_graph

P = "/Game/Keeper/BP_Gate"
CUBE = "/Engine/BasicShapes/Cube.Cube"
STONE = "/Game/Materials/MI_DarkStone.MI_DarkStone"
WOOD = "/Game/Materials/MI_Wood.MI_Wood"
SM = "/Script/Engine.StaticMeshComponent"
SC = "/Script/Engine.SceneComponent"
MOV = {"mobility": "Movable"}

ensure_bp(P, "/Script/Engine.Actor")
add_comp(P, SC, "Root")
for side, y in (("L", -280), ("R", 280)):
    add_comp(P, SM, f"Post{side}", "Root", {"staticMesh": CUBE, "overrideMaterials": [STONE],
                                            "relativeLocation": {"x": 0, "y": y, "z": 160},
                                            "relativeScale3D": {"x": 0.6, "y": 0.6, "z": 3.2}})
add_comp(P, SC, "HingeL", "Root", {**MOV, "relativeLocation": {"x": 0, "y": -250, "z": 0}})
add_comp(P, SC, "HingeR", "Root", {**MOV, "relativeLocation": {"x": 0, "y": 250, "z": 0}})
add_comp(P, SM, "DoorL", "HingeL", {**MOV, "staticMesh": CUBE, "overrideMaterials": [WOOD],
                                    "relativeLocation": {"x": 0, "y": 125, "z": 120},
                                    "relativeScale3D": {"x": 0.15, "y": 2.45, "z": 2.4}})
add_comp(P, SM, "DoorR", "HingeR", {**MOV, "staticMesh": CUBE, "overrideMaterials": [WOOD],
                                    "relativeLocation": {"x": 0, "y": -125, "z": 120},
                                    "relativeScale3D": {"x": 0.15, "y": 2.45, "z": 2.4}})
ensure_var(P, "IsOpen", "bool")
compile_save(P)

DSL = """
(event Custom|OpenGate
  (Variables|Default|SetIsOpen true)
  (Components|MoveComponentTo :Component (Variables|Default|GetHingeL)
     :TargetRelativeLocation (Math|Vector|MakeVector :X 0.0 :Y -250.0 :Z 0.0)
     :TargetRelativeRotation (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw -95.0)
     :OverTime 1.5 :bEaseOut true :bEaseIn true)
  (Components|MoveComponentTo :Component (Variables|Default|GetHingeR)
     :TargetRelativeLocation (Math|Vector|MakeVector :X 0.0 :Y 250.0 :Z 0.0)
     :TargetRelativeRotation (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw 95.0)
     :OverTime 1.5 :bEaseOut true :bEaseIn true))
"""
write_graph(P, DSL)
print(compile_save(P))
print(read_graph(P))


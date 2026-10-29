"""Helpers for pasting comment boxes at exact graph positions (MCP cannot create/move/read comment nodes).
  python place_comments.py knot             -> clipboard = one reroute node (to calibrate screen -> graph)
  python place_comments.py knots <graph>    -> print reroute positions, then delete them
  python place_comments.py comment <graph> <i> -> clipboard = comment i of comments.boxes(graph) at local (0,0)"""
import subprocess
import sys
import uuid
from pathlib import Path

from comments import boxes, graph_ref
from ue import BP, call

HERE = Path(__file__).parent


def clip(text):
    f = HERE / "layout" / "clip.t3d"
    f.write_text(text, encoding="utf-8")
    subprocess.run(["powershell", "-NoProfile", "-Command", f"Set-Clipboard -Value ([IO.File]::ReadAllText('{f}'))"],
                   check=True)


def lin(c):  # linear colour -> T3D
    return f"(R={c[0]:.3f},G={c[1]:.3f},B={c[2]:.3f},A=1.000000)"


def place(graph, s1, g1, s2, g2):
    """Single comment for a function graph: clipboard = the comment, returns the screen point for its top-left."""
    text, col, x, y, w, h = boxes(graph)[0]
    kx, ky = (g2[0] - g1[0]) / (s2[0] - s1[0]), (g2[1] - g1[1]) / (s2[1] - s1[1])
    text = text.replace('"', "'")
    clip("\n".join([f'Begin Object Class=/Script/UnrealEd.EdGraphNode_Comment Name="EdGraphNode_Comment_0"',
                    f"   CommentColor={lin(col)}", "   FontSize=28", "   NodePosX=0", "   NodePosY=0",
                    f"   NodeWidth={int(w)}", f"   NodeHeight={int(h)}", f'   NodeComment="{text}"',
                    f"   NodeGuid={uuid.uuid4().hex.upper()}", "End Object", ""]))
    return round(s1[0] + (x - g1[0]) / kx), round(s1[1] + (y - g1[1]) / ky)


if sys.argv[1] == "knot":
    clip(f'Begin Object Class=/Script/BlueprintGraph.K2Node_Knot Name="K2Node_Knot_0"\n   NodePosX=0\n   NodePosY=0\n'
         f'   NodeGuid={uuid.uuid4().hex.upper()}\nEnd Object\n')
elif sys.argv[1] == "knots":
    ns = [n for n in call(BP, "find_nodes", graph=graph_ref(sys.argv[2]), title="", entry_points_only=False) or []
          if "K2Node_Knot" in n["refPath"]]
    for n in call(BP, "get_node_infos", nodes=ns) if ns else []:
        print(n["node"]["refPath"].rsplit(".", 1)[1], n["position"]["x"], n["position"]["y"])
    for n in ns:
        call(BP, "delete_node", node=n)
elif sys.argv[1] == "all":
    # all boxes of the graph at their true positions; Unreal pastes so the AVERAGE node position lands on the
    # cursor, so put the cursor on the printed average (graph coords)
    bs = boxes(sys.argv[2])
    t3d = ""
    for i, (text, col, x, y, w, h) in enumerate(bs):
        text = text.replace('"', "'")
        t3d += "\n".join([
            f'Begin Object Class=/Script/UnrealEd.EdGraphNode_Comment Name="EdGraphNode_Comment_{i}"',
            f"   CommentColor={lin(col)}", "   FontSize=28", f"   NodePosX={int(x)}", f"   NodePosY={int(y)}",
            f"   NodeWidth={int(w)}", f"   NodeHeight={int(h)}", f'   NodeComment="{text}"',
            f"   NodeGuid={uuid.uuid4().hex.upper()}", "End Object", ""])
    clip(t3d)
    print("avg", sum(b[2] for b in bs) / len(bs), sum(b[3] for b in bs) / len(bs))
elif sys.argv[1] == "comment":
    text, col, x, y, w, h = boxes(sys.argv[2])[int(sys.argv[3])]
    text = text.replace('"', "'")
    clip(f'Begin Object Class=/Script/UnrealEd.EdGraphNode_Comment Name="EdGraphNode_Comment_0"\n'
         f'   CommentColor={lin(col)}\n   FontSize=28\n   NodePosX=0\n   NodePosY=0\n   NodeWidth={int(w)}\n'
         f'   NodeHeight={int(h)}\n   NodeComment="{text}"\n   NodeGuid={uuid.uuid4().hex.upper()}\nEnd Object\n')
    print(int(x), int(y), int(w), int(h))


if sys.argv[1] == "place":  # place <graph> gx1 gy1 gx2 gy2  (knots pasted at screen 400,250 and 1000,750)
    a = list(map(float, sys.argv[3:7]))
    print(place(sys.argv[2], (400, 250), (a[0], a[1]), (1000, 750), (a[2], a[3])))

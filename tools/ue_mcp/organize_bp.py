"""Tidy a Blueprint's graphs so a person can read and edit them:
1. prune: delete dead copies that earlier write_graph_dsl rebuilds left behind (nodes that can never run),
2. arrange every function graph left-to-right,
3. EventGraph: arrange each event chain on its own and stack the chains as rows (one row per event).
Usage: python organize_bp.py /Game/Keeper/BP_Keeper [/Game/...]   (in Git Bash set MSYS_NO_PATHCONV=1)
Writes layout/<name>.json: {graph: {event node: [x, y, w, h]}} so comment boxes can be placed around each row."""
import json
import sys
from pathlib import Path

from bpkit import bp_ref, chain_of, compile_save, node_infos, prune_graph
from ue import BP, call

ROW_GAP = 300                 # empty space between event rows
NODE_W, NODE_H = 360, 200     # rough node size (positions are top-left corners)
OUT = Path(__file__).with_name("layout")
OUT.mkdir(exist_ok=True)


def organize(path):
    name = path.rsplit("/", 1)[1]
    layout = {}
    for g in call(BP, "list_graphs", blueprint=bp_ref(path)) or []:
        gname = g["refPath"].rsplit(":", 1)[1]
        total, dead = prune_graph(g)
        nodes = call(BP, "find_nodes", graph=g, title="", entry_points_only=False) or []
        if not nodes:
            continue
        entries = call(BP, "find_nodes", graph=g, title="", entry_points_only=True) or []
        if len(entries) <= 1:
            call(BP, "arrange_nodes", nodes=nodes)
            print(f"{name}:{gname}: {total} -> {len(nodes)} nodes, arranged")
            continue
        info = {n["node"]["refPath"]: n for n in node_infos(nodes)}
        rows, y = {}, 0
        for e in entries:
            chain = [{"refPath": r} for r in chain_of([e["refPath"]], info)]
            call(BP, "arrange_nodes", nodes=chain)
            pos = node_infos(chain)
            xs = [n["position"]["x"] for n in pos]
            ys = [n["position"]["y"] for n in pos]
            dx, dy = -min(xs), y - min(ys)
            for n in pos:
                call(BP, "set_node_position", node=n["node"],
                     pos={"x": n["position"]["x"] + dx, "y": n["position"]["y"] + dy})
            w, h = max(xs) - min(xs) + NODE_W, max(ys) - min(ys) + NODE_H
            rows[e["refPath"].rsplit(".", 1)[1] + " " + info[e["refPath"]]["type_id"]] = [0, y, w, h]
            y += h + ROW_GAP
        layout[gname] = rows
        print(f"{name}:{gname}: {total} -> {len(nodes)} nodes, {len(rows)} rows")
    print(name, "saved:", compile_save(path))
    (OUT / f"{name}.json").write_text(json.dumps(layout, ensure_ascii=False, indent=1), encoding="utf-8")


for p in sys.argv[1:]:
    organize(p)

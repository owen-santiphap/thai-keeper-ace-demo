"""Small helpers for building Blueprints through Epic's Unreal MCP (EditorToolset)."""
import json

from ue import ACTOR, ASSET, BP, OBJ, call, ref


def bp_ref(path):
    """'/Game/Keeper/BP_Gate' -> ref to the Blueprint asset."""
    return ref(f"{path}.{path.rsplit('/', 1)[1]}")


def ensure_bp(path, parent_class):
    folder, name = path.rsplit("/", 1)
    if call(ASSET, "exists", path=path):
        return bp_ref(path)
    return call(BP, "create", folder_path=folder, asset_name=name, asset_type=ref(parent_class))


def comp_ref(path, comp_name):
    name = path.rsplit("/", 1)[1]
    return ref(f"{path}.{name}_C:{comp_name}_GEN_VARIABLE")


def add_comp(path, cls, name, parent=None, props=None):
    """Add a component to a Blueprint (skips if it already exists), optionally parent it and set properties."""
    bp = bp_ref(path)
    c = comp_ref(path, name)
    try:
        call(OBJ, "get_class", instance=c)
        exists = True
    except RuntimeError:
        exists = False
    if not exists:
        c = call(ACTOR, "add_component", owner=bp, component_type=ref(cls), name=name)
    if parent:
        call(ACTOR, "set_parent_component", component=c, parent=comp_ref(path, parent))
    if props:
        set_props(c, props)
    return c


def set_props(obj, props):
    ok = call(OBJ, "set_properties", instance=obj, values=json.dumps(props, ensure_ascii=False))
    if not ok:
        raise RuntimeError(f"set_properties failed on {obj}: {props}")
    return ok


def ensure_var(path, name, type_name=None, object_class=None):
    bp = bp_ref(path)
    have = call(BP, "list_variables", blueprint=bp) or []
    if name in [v if isinstance(v, str) else v.get("name") for v in have]:
        return
    if object_class:
        call(BP, "add_object_variable", blueprint=bp, name=name, object_class=ref(object_class))
    else:
        call(BP, "add_variable", blueprint=bp, name=name, type_name=type_name)


def graph(path, name="EventGraph"):
    n = path.rsplit("/", 1)[1]
    return ref(f"{path}.{n}:{name}")


def write_graph(path, code, name="EventGraph"):
    return call(BP, "write_graph_dsl", graph=graph(path, name), code=code)


def compile_save(path):
    call(BP, "compile_blueprint", blueprint=bp_ref(path), warnings_as_errors=False)
    return call(ASSET, "save_assets", asset_paths=[path])


def read_graph(path, name="EventGraph"):
    return call(BP, "read_graph_dsl", graph=graph(path, name))


def node_infos(nodes):
    out = []
    for i in range(0, len(nodes), 40):
        out += call(BP, "get_node_infos", nodes=nodes[i:i + 40]) or []
    return out


def prune_graph(graph):
    """Delete nodes that can never run: keep what is reachable along exec wires from an entry point (function
    entry / event), plus the nodes feeding data into those. write_graph_dsl leaves the previous version of a graph
    behind (still wired to the entry's parameter pins), so every rebuild added a dead copy; this removes them."""
    nodes = call(BP, "find_nodes", graph=graph, title="", entry_points_only=False) or []
    entries = call(BP, "find_nodes", graph=graph, title="", entry_points_only=True) or []
    info = {n["node"]["refPath"]: n for n in node_infos(nodes)}
    # start points: entry nodes, plus anything that starts execution itself (exec out, no exec in), e.g. key events
    starts = [e["refPath"] for e in entries] + [
        r for r, n in info.items()
        if any(p["type_id"] == "Exec" for p in n["output_pins"])
        and not any(p["type_id"] == "Exec" for p in n["input_pins"])]
    keep = chain_of(starts, info)
    dead = [n for n in nodes if n["refPath"] not in keep]
    for n in dead:
        call(BP, "delete_node", node=n)
    return len(nodes), len(dead)


def chain_of(starts, info):
    """Nodes reachable along exec wires from starts, plus the nodes feeding data into them."""
    keep, todo = set(), list(starts)
    while todo:  # forward along exec
        r = todo.pop()
        if r in keep or r not in info:
            continue
        keep.add(r)
        for pin in info[r]["output_pins"]:
            if pin["type_id"] == "Exec":
                todo += [c["node"]["refPath"] for c in pin["connected_pins"]]
    todo = list(keep)
    while todo:  # backward along data
        r = todo.pop()
        for pin in info[r]["input_pins"]:
            if pin["type_id"] != "Exec":
                for c in pin["connected_pins"]:
                    src = c["node"]["refPath"]
                    if src not in keep:
                        keep.add(src)
                        todo.append(src)
    return keep

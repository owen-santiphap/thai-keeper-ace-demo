"""Helpers for building widget blueprints through Epic's UMG toolset."""
from ue import ASSET, call, ref

UMG = "UMGToolSet.UMGToolSet"
FONT = "/Game/UI/Fonts/F_Thai.F_Thai"


def font(size):
    return {"fontObject": FONT, "typefaceFontName": "Regular", "size": size}


def ensure_wbp(path):
    folder, name = path.rsplit("/", 1)
    if call(ASSET, "exists", path=path):
        return ref(f"{path}.{name}")
    return call(UMG, "CreateWidgetBlueprint", folderPath=folder, assetName=name,
                parentClass=ref("/Script/UMG.UserWidget"))


def widgets(wbp):
    return call(UMG, "GetWidgets", widgetBlueprint=wbp)


def find_widget(wbp, name):
    info = widgets(wbp)
    items = info.get("widgets", info) if isinstance(info, dict) else info
    for w in items or []:
        wr = w.get("widget") or w.get("Widget")
        n = w.get("widgetName") or (wr or {}).get("refPath", "").rsplit(".", 1)[-1]
        if n == name:
            return w
    return None


def add_widget(wbp, cls, name, parent=None):
    existing = find_widget(wbp, name)
    if existing:
        return existing
    args = {"widgetBlueprint": wbp, "widgetClass": ref(cls), "widgetDisplayName": name}
    if parent is not None:
        args["parentWidget"] = parent
    return call(UMG, "AddWidget", **args)

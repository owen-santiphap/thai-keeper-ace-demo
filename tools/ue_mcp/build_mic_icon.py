"""Mic-mode icon in the chat window (Owen 2026-10-21): green = always-on, amber = push-to-talk (hold V),
red = listening (V held), grey = mic off. Icons from tools/make_mic_icons.py.
Also gives the game keyboard focus at start (SetupChat) so Enter works without clicking first.
Writes only WBP_Chat:SetMicIcon, BP_Keeper:UpdateMicBar and BP_Keeper:SetupChat (no comment boxes there)."""
from pathlib import Path

from bpkit import compile_save, ensure_var, prune_graph, set_props
from ue import ASSET, BP, call, ref
from umgkit import UMG, add_widget, ensure_wbp

SRC = Path(__file__).resolve().parents[2] / "TheKeepr_Demo" / "SourceArt" / "Icons"
FOLDER = "/Game/UI/Icons"
TEX = "editor_toolset.toolsets.texture.TextureTools"
for name in ("T_Mic_Open", "T_Mic_PTT", "T_Mic_Live", "T_Mic_Off"):
    path = f"{FOLDER}/{name}"
    if not call(ASSET, "exists", path=path):
        call(TEX, "import_file", folder_path=FOLDER, asset_name=name, source_file=str(SRC / f"{name}.png"))
    set_props(ref(f"{path}.{name}"), {"LODGroup": "TEXTUREGROUP_UI", "MipGenSettings": "TMGS_NoMipmaps",
                                      "CompressionSettings": "TC_EditorIcon"})
    call(ASSET, "save_assets", asset_paths=[path])

W = "/Game/UI/WBP_Chat"
w = ensure_wbp(W)
root = next(x for x in [add_widget(w, "/Script/UMG.CanvasPanel", "Root")])
ICONS = {"open": "T_Mic_Open", "ptt": "T_Mic_PTT", "live": "T_Mic_Live", "off": "T_Mic_Off"}
for mode, tex in ICONS.items():  # four stacked images in one spot; SetMicIcon shows the one for the current mode
    icon = add_widget(w, "/Script/UMG.Image", f"MicIcon_{mode}", root["widget"])
    # left of the chat panel's bottom row (panel: anchor bottom-centre, left -480, top -250, 960 x 230)
    set_props(icon["slot"], {"layoutData": {"anchors": {"minimum": {"x": 0.5, "y": 1.0}, "maximum": {"x": 0.5, "y": 1.0}},
                                            "offsets": {"left": -580, "top": -120, "right": 88, "bottom": 88},
                                            "alignment": {"x": 0.0, "y": 0.0}}})
    set_props(icon["widget"], {"brush": {"resourceObject": f"{FOLDER}/{tex}.{tex}", "imageSize": {"x": 88, "y": 88}},
                               "visibility": "Visible" if mode == "open" else "Collapsed"})
    call(UMG, "ToggleWidgetAsVariable", widgetBlueprint=w, widget=icon["widget"], bIsVariable=True)
call(UMG, "CompileWidgetBlueprint", widgetBlueprint=w)

g = ref(f"{W}.WBP_Chat:SetMicIcon")
try:
    call(BP, "get_graph", blueprint=ref(f"{W}.WBP_Chat"), graph_name="SetMicIcon")
except RuntimeError:
    call(BP, "add_function_graph", blueprint=ref(f"{W}.WBP_Chat"), graph_name="SetMicIcon")
    call(BP, "add_function_param", graph=g, param_name="Mode", param_type="string", input_param=True)
T = lambda n: f'"{FOLDER}/{n}.{n}"'  # noqa: E731
call(BP, "write_graph_dsl", graph=g, code="""
(fn SetMicIcon (Mode)
  ; Mode: open | ptt | live | off -> show that icon, hide the others
  (if (Utilities|String|EqualExactly(String) Mode "open")
    (Widget|SetVisibility :self (Variables|WBP_Chat|GetMicIcon_open) :InVisibility "Visible")
    (else (Widget|SetVisibility :self (Variables|WBP_Chat|GetMicIcon_open) :InVisibility "Collapsed")))
  (if (Utilities|String|EqualExactly(String) Mode "ptt")
    (Widget|SetVisibility :self (Variables|WBP_Chat|GetMicIcon_ptt) :InVisibility "Visible")
    (else (Widget|SetVisibility :self (Variables|WBP_Chat|GetMicIcon_ptt) :InVisibility "Collapsed")))
  (if (Utilities|String|EqualExactly(String) Mode "live")
    (Widget|SetVisibility :self (Variables|WBP_Chat|GetMicIcon_live) :InVisibility "Visible")
    (else (Widget|SetVisibility :self (Variables|WBP_Chat|GetMicIcon_live) :InVisibility "Collapsed")))
  (if (Utilities|String|EqualExactly(String) Mode "off")
    (Widget|SetVisibility :self (Variables|WBP_Chat|GetMicIcon_off) :InVisibility "Visible")
    (else (Widget|SetVisibility :self (Variables|WBP_Chat|GetMicIcon_off) :InVisibility "Collapsed"))))
""")
print("chat saved:", compile_save(W))

P = "/Game/Keeper/BP_Keeper"
G = lambda n: ref(f"{P}.BP_Keeper:{n}")  # noqa: E731
call(BP, "write_graph_dsl", graph=G("UpdateMicBar"), code="""
(fn UpdateMicBar ()
  ; keys + mic level bar, status text and mode icon in the chat window
  (CallFunction|HandleKeys)
  (bind cw (Variables|5SceneandUI|GetChatW))
  (Utilities|IsValid cw
    (:"Is Valid"
      (Class|WBPChat|SetMic :self cw :Level (Variables|2Voicelink|GetMicLevel) :Label (CallFunction|MicLabel))
      (Class|WBPChat|SetMicIcon :self cw
        :Mode (select (and (Variables|2Voicelink|GetPTTDown) (Utilities|String|EqualExactly(String) (Variables|2Voicelink|GetMicMode) "ptt"))
                "live" (Variables|2Voicelink|GetMicMode))))
    (:"Is Not Valid")))
""")
call(BP, "write_graph_dsl", graph=G("SetupChat"), code="""
(fn SetupChat ()
  ; chat window (log, typing box, mic bar + mode icon, ghost counter); keyboard focus to the game so Enter works at once
  (bind pc (Game|GetPlayerController :PlayerIndex 0))
  (Input|EnableInput :self self :PlayerController pc)
  (Input|SetInputModeGameOnly :PlayerController pc)
  (bind cw (Utilities|Casting|CastToWBP_Chat :Object (UserInterface|CreateWidget :Class "/Game/UI/WBP_Chat.WBP_Chat_C" :OwningPlayer pc))
    (:then
      (Variables|5SceneandUI|SetChatW cw)
      (UserInterface|Viewport|AddtoViewport :self cw))
    (:CastFailed (Development|PrintString :InString "SETUP: chat widget failed"))))
""")
for n in ("UpdateMicBar", "SetupChat"):
    print(n, prune_graph(G(n)))
    call(BP, "arrange_nodes", nodes=call(BP, "find_nodes", graph=G(n), title="", entry_points_only=False))
print("keeper saved:", compile_save(P))

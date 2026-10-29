"""WBP_Chat v2: mic level bar + label (SetMic), UI-only input while typing (no movement), any commit returns to game."""
from bpkit import compile_save, set_props
from ue import BP, call, ref
from umgkit import UMG, add_widget, ensure_wbp, find_widget, font

P = "/Game/UI/WBP_Chat"
w = ensure_wbp(P)
panel = find_widget(w, "Panel")
row = add_widget(w, "/Script/UMG.HorizontalBox", "MicRow", panel["widget"])
mtext = add_widget(w, "/Script/UMG.TextBlock", "MicText", row["widget"])
mbar = add_widget(w, "/Script/UMG.ProgressBar", "MicBar", row["widget"])
set_props(mtext["widget"], {"font": font(16), "text": "ไมค์: กดค้าง V เพื่อพูด  (M เปลี่ยนโหมด)",
                            "colorAndOpacity": {"specifiedColor": {"r": 0.8, "g": 0.9, "b": 1.0, "a": 1}}})
set_props(mbar["widget"], {"percent": 0.0,
                           "fillColorAndOpacity": {"r": 0.3, "g": 1.0, "b": 0.6, "a": 1}})
set_props(mbar["slot"], {"size": {"value": 1.0, "sizeRule": "Fill"}, "verticalAlignment": "VAlign_Center",
                         "padding": {"left": 12, "top": 4, "right": 0, "bottom": 4}})
set_props(find_widget(w, "HintText")["widget"],
          {"text": "Enter = พิมพ์ (Enter ส่ง / Esc ยกเลิก)  •  กดค้าง V = พูด  •  M = เปลี่ยนโหมดไมค์"})
for x in (mtext, mbar):
    call(UMG, "ToggleWidgetAsVariable", widgetBlueprint=w, widget=x["widget"], bIsVariable=True)
call(UMG, "CompileWidgetBlueprint", widgetBlueprint=w)

W = ref(f"{P}.WBP_Chat")
g = ref(f"{P}.WBP_Chat:SetMic")
try:
    call(BP, "get_graph", blueprint=W, graph_name="SetMic")
except RuntimeError:
    call(BP, "add_function_graph", blueprint=W, graph_name="SetMic")
    call(BP, "add_function_param", graph=g, param_name="Level", param_type="float", input_param=True)
    call(BP, "add_function_param", graph=g, param_name="Label", param_type="string", input_param=True)
call(BP, "write_graph_dsl", graph=g, code="""
(fn SetMic (Level Label)
  (Progress|SetPercent :self (Variables|WBP_Chat|GetMicBar) :InPercent Level)
  (Widget|SetText(Text) :self (Variables|WBP_Chat|GetMicText) :InText (Utilities|Text|ToText(String) Label)))
""")
call(BP, "write_graph_dsl", graph=ref(f"{P}.WBP_Chat:FocusInput"), code="""
(fn FocusInput ()
  (bind pc (Game|GetPlayerController :PlayerIndex 0))
  (Input|SetInputModeUIOnly :PlayerController pc :InWidgetToFocus (Variables|WBP_Chat|GetInputBox))
  (Widget|SetKeyboardFocus :self (Variables|WBP_Chat|GetInputBox)))
""")
call(BP, "write_graph_dsl", graph=ref(f"{P}.WBP_Chat:EventGraph"), code="""
(event UserInterface|EventConstruct
  (bind k (Utilities|Casting|CastToBP_Keeper :Object (Actor|GetActorOfClass :ActorClass "/Game/Keeper/BP_Keeper.BP_Keeper_C"))
    (:then
      (Variables|Default|SetKeeper k))
    (:CastFailed)))

(event OnTextCommitted(InputBox) (Text CommitMethod)
  (bind s (Utilities|String|ToString(Text) Text))
  (Widget|SetText(TextBox) :self (Variables|WBP_Chat|GetInputBox) :InText (Utilities|Text|ToText(String) ""))
  (Input|SetInputModeGameOnly :PlayerController (Game|GetPlayerController :PlayerIndex 0))
  (Utilities|FlowControl|Switch|SwitchonETextCommit CommitMethod
    (:OnEnter
      (if (not (Utilities|String|IsEmpty s))
        (Class|BPKeeper|Ask :self (Variables|Default|GetKeeper) :Text s)))))
""")
print(compile_save(P))

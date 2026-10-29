"""WBP_Chat: bottom panel (last exchange log + Thai input box + hint) and a ghost counter top-right."""
from bpkit import compile_save, ensure_var, set_props
from ue import BP, call, ref
from umgkit import UMG, add_widget, ensure_wbp, font

P = "/Game/UI/WBP_Chat"
w = ensure_wbp(P)
root = add_widget(w, "/Script/UMG.CanvasPanel", "Root")
panel = add_widget(w, "/Script/UMG.VerticalBox", "Panel", root["widget"])
logb = add_widget(w, "/Script/UMG.Border", "LogBorder", panel["widget"], )
log = add_widget(w, "/Script/UMG.TextBlock", "LogText", logb["widget"])
inp = add_widget(w, "/Script/UMG.EditableTextBox", "InputBox", panel["widget"])
hint = add_widget(w, "/Script/UMG.TextBlock", "HintText", panel["widget"])
score = add_widget(w, "/Script/UMG.TextBlock", "ScoreText", root["widget"])

set_props(panel["slot"], {"layoutData": {"anchors": {"minimum": {"x": 0.5, "y": 1.0}, "maximum": {"x": 0.5, "y": 1.0}},
                                         "offsets": {"left": -480, "top": -250, "right": 960, "bottom": 230},
                                         "alignment": {"x": 0.0, "y": 0.0}}})
set_props(score["slot"], {"layoutData": {"anchors": {"minimum": {"x": 1.0, "y": 0.0}, "maximum": {"x": 1.0, "y": 0.0}},
                                         "offsets": {"left": -340, "top": 24, "right": 320, "bottom": 50},
                                         "alignment": {"x": 0.0, "y": 0.0}}})
set_props(logb["widget"], {"brushColor": {"r": 0, "g": 0, "b": 0, "a": 0.55},
                           "padding": {"left": 14, "top": 8, "right": 14, "bottom": 8}})
set_props(log["widget"], {"font": font(19), "autoWrapText": True, "wrapTextAt": 920,
                          "colorAndOpacity": {"specifiedColor": {"r": 0.92, "g": 0.92, "b": 0.92, "a": 1}},
                          "text": "ลุงบุญยืนรออยู่หน้าประตูป่าช้า ลองทักทายดูสิ"})
set_props(inp["widget"], {"widgetStyle": {"textStyle": {"font": font(21)}},
                          "hintText": "พิมพ์คุยกับลุงบุญ แล้วกด Enter", "clearKeyboardFocusOnCommit": True})
set_props(hint["widget"], {"font": font(15), "justification": "Center",
                           "colorAndOpacity": {"specifiedColor": {"r": 0.7, "g": 0.75, "b": 0.85, "a": 1}},
                           "text": "กด Enter เพื่อพิมพ์  •  หรือพูดใส่ไมค์ได้เลย (เปิด voice_service ไว้)"})
set_props(score["widget"], {"font": font(24), "justification": "Right",
                            "colorAndOpacity": {"specifiedColor": {"r": 0.55, "g": 1.0, "b": 0.8, "a": 1}},
                            "text": "ผีที่พบ 0/4"})
for x in (log, inp, score):
    call(UMG, "ToggleWidgetAsVariable", widgetBlueprint=w, widget=x["widget"], bIsVariable=True)
ensure_var(P, "Keeper", object_class="/Game/Keeper/BP_Keeper.BP_Keeper_C")
call(UMG, "CompileWidgetBlueprint", widgetBlueprint=w)
print(compile_save(P))

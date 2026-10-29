"""WBP_Bubble: dark rounded box with a Thai TextBlock; function SetBubble(Line)."""
from bpkit import compile_save, set_props
from ue import BP, call, ref
from umgkit import UMG, add_widget, ensure_wbp, font

P = "/Game/UI/WBP_Bubble"
w = ensure_wbp(P)
b = add_widget(w, "/Script/UMG.Border", "BubbleBorder")
t = add_widget(w, "/Script/UMG.TextBlock", "BubbleText", b["widget"])
set_props(b["widget"], {"brushColor": {"r": 0.0, "g": 0.0, "b": 0.0, "a": 0.7},
                        "padding": {"left": 16, "top": 10, "right": 16, "bottom": 12}})
set_props(t["widget"], {"font": font(24), "autoWrapText": True, "wrapTextAt": 520, "justification": "Center",
                        "colorAndOpacity": {"specifiedColor": {"r": 1.0, "g": 0.93, "b": 0.78, "a": 1.0}},
                        "text": "ลุงบุญ"})
call(UMG, "ToggleWidgetAsVariable", widgetBlueprint=w, widget=t["widget"], bIsVariable=True)
call(UMG, "CompileWidgetBlueprint", widgetBlueprint=w)

g = ref(f"{P}.WBP_Bubble:ShowLine")
try:
    call(BP, "get_graph", blueprint=w, graph_name="ShowLine")
except RuntimeError:
    call(BP, "add_function_graph", blueprint=w, graph_name="ShowLine")
    call(BP, "add_function_param", graph=g, param_name="Line", param_type="string", input_param=True)
call(BP, "write_graph_dsl", graph=g, code="""
(fn ShowLine (Line)
  (Widget|SetText(Text) :self (Variables|WBP_Bubble|GetBubbleText) :InText (Utilities|Text|ToText(String) Line)))
""")
print(compile_save(P))
print(call(BP, "read_graph_dsl", graph=g))

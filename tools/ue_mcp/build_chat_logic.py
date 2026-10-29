"""WBP_Chat logic: find the keeper, send typed text on Enter, SetLog/SetScore/FocusInput functions."""
from bpkit import compile_save
from ue import BP, call, ref

P = "/Game/UI/WBP_Chat"
W = ref(f"{P}.WBP_Chat")


def fn(name, params, code):
    g = ref(f"{P}.WBP_Chat:{name}")
    try:
        call(BP, "get_graph", blueprint=W, graph_name=name)
    except RuntimeError:
        call(BP, "add_function_graph", blueprint=W, graph_name=name)
        for p in params:
            call(BP, "add_function_param", graph=g, param_name=p, param_type="string", input_param=True)
    call(BP, "write_graph_dsl", graph=g, code=code)


fn("SetLog", ["Line"], """
(fn SetLog (Line)
  (Widget|SetText(Text) :self (Variables|WBP_Chat|GetLogText) :InText (Utilities|Text|ToText(String) Line)))
""")
fn("SetScore", ["Line"], """
(fn SetScore (Line)
  (Widget|SetText(Text) :self (Variables|WBP_Chat|GetScoreText) :InText (Utilities|Text|ToText(String) Line)))
""")
fn("FocusInput", [], """
(fn FocusInput ()
  (bind pc (Game|GetPlayerController :PlayerIndex 0))
  (Input|SetInputModeGameAndUI :PlayerController pc :InWidgetToFocus (Variables|WBP_Chat|GetInputBox))
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
  (Utilities|FlowControl|Switch|SwitchonETextCommit CommitMethod
    (:OnEnter
      (if (not (Utilities|String|IsEmpty s))
        (Class|BPKeeper|Ask :self (Variables|Default|GetKeeper) :Text s))
      (Widget|SetText(TextBox) :self (Variables|WBP_Chat|GetInputBox) :InText (Utilities|Text|ToText(String) ""))
      (Input|SetInputModeGameOnly :PlayerController (Game|GetPlayerController :PlayerIndex 0)))))
""")
print(compile_save(P))
print(call(BP, "read_graph_dsl", graph=ref(f"{P}.WBP_Chat:EventGraph")))

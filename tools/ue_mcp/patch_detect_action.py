"""One-off patch (2026-10-20): Blueprint recognises action requests itself (guide to a visitable ghost, light the fire,
open the gate) and asks the confirmation question with a scripted line, so actions no longer depend on the LLM (which,
with a fresh chat per question, lost track of which ghost a bare "ไปเลย" meant). Also names the ghost in the event note."""
from ue import BP, call, ref

P = "/Game/Keeper/BP_Keeper"
C = "Utilities|String|Contains"
A = "Utilities|String|Append"
EQ = "Utilities|String|EqualExactly(String)"

# function graphs + params
for fn, ins, outs in [("DetectAction", [("Text", "string")], [("Handled", "bool")]),
                      ("GhostName", [("Id", "string")], [("Name", "string")])]:
    g = ref(f"{P}.BP_Keeper:{fn}")
    try:
        call(BP, "get_graph", blueprint=ref(f"{P}.BP_Keeper"), graph_name=fn)
    except RuntimeError:
        call(BP, "add_function_graph", blueprint=ref(f"{P}.BP_Keeper"), graph_name=fn)
        for n, t in ins:
            call(BP, "add_function_param", graph=g, param_name=n, param_type=t, input_param=True)
        for n, t in outs:
            call(BP, "add_function_param", graph=g, param_name=n, param_type=t, input_param=False)

p = "build_keeper_logic.py"
s = open(p, encoding="utf-8").read()
NEW = f'''    "GhostName": """
(fn GhostName (Id)
  (if ({EQ} Id "krasue")
    (return "กระสือ"))
  (if ({EQ} Id "tani")
    (return "นางตานี"))
  (if ({EQ} Id "kong_koi")
    (return "ผีกองกอย"))
  (if ({EQ} Id "pret")
    (return "เปรต"))
  (return "ผี"))
""",
    "DetectAction": """
(fn DetectAction (Text)
  ; action requests are recognised here, not by the LLM: the keeper asks the confirmation question himself
  (bind gid (CallFunction|GhostIdFrom :S Text))
  (if (and (or ({C} :SearchIn Text :Substring "พา") ({C} :SearchIn Text :Substring "ไปดู"))
           (not (Utilities|String|IsEmpty gid)))
    (Variables|Default|SetPendingTool "guide_to_ghost")
    (Variables|Default|SetPendingArg Text)
    (CallFunction|Speak :Line ({A} ({A} "จะให้ลุงพาไปดู" (CallFunction|GhostName :Id gid)) "เลยมั้ย"))
    (return true))
  (if (or (and ({C} :SearchIn Text :Substring "จุด")
               (or ({C} :SearchIn Text :Substring "ไฟ") ({C} :SearchIn Text :Substring "ตะเกียง")))
          ({C} :SearchIn Text :Substring "เปิดไฟ"))
    (Variables|Default|SetPendingTool "light_lantern")
    (CallFunction|Speak :Line "จะให้ลุงจุดไฟเลยมั้ย")
    (return true))
  (if (and ({C} :SearchIn Text :Substring "เปิด") ({C} :SearchIn Text :Substring "ประตู"))
    (Variables|Default|SetPendingTool "open_gate")
    (CallFunction|Speak :Line "จะให้ลุงเปิดประตูเลยมั้ย")
    (return true))
  (return false))
""",
'''
if '"DetectAction"' not in s:
    s = s.replace('    "Ask": """', NEW + '    "Ask": """', 1)
a = '''    (Variables|Default|SetPendingTool ""))
  (Variables|Default|SetBusy true)'''
b = '''    (Variables|Default|SetPendingTool ""))
  (if (CallFunction|DetectAction :Text Text)
    (return))
  (Variables|Default|SetBusy true)'''
assert s.count(a) == 1, "ask hook"
s = s.replace(a, b)
a = '  (Variables|Default|SetDoneNote "พาหลานมาดูผีแล้ว")'
b = '  (Variables|Default|SetDoneNote (' + A + ' (' + A + ' "พาหลานมาดู" (CallFunction|GhostName :Id (Variables|Default|GetToolArgs))) "แล้ว"))'
assert s.count(a) == 1, "note"
s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("patched")

"""BP_Keeper mic controls: vars, CycleMicMode/MicLabel, Tick -> chat mic bar, keys V (push-to-talk) and M (mode)."""
import json

from bpkit import bp_ref, compile_save, ensure_var, set_props
from ue import BP, call, ref

P = "/Game/Keeper/BP_Keeper"
b = bp_ref(P)
g = ref(f"{P}.BP_Keeper:EventGraph")

for name, t in [("MicMode", "string"), ("PTTDown", "bool"), ("MicLevel", "float"), ("VoiceStatus", "string")]:
    ensure_var(P, name, t)
    call(BP, "set_variable_instance_editable", blueprint=b, variable_name=name, instance_editable=True)
call(BP, "compile_blueprint", blueprint=b, warnings_as_errors=False)
set_props(ref("/Game/Keeper/BP_Keeper.Default__BP_Keeper_C"), {"MicMode": "ptt"})


def fn(name, ins, outs, code):
    gr = ref(f"{P}.BP_Keeper:{name}")
    try:
        call(BP, "get_graph", blueprint=b, graph_name=name)
    except RuntimeError:
        call(BP, "add_function_graph", blueprint=b, graph_name=name)
        for n, t in ins:
            call(BP, "add_function_param", graph=gr, param_name=n, param_type=t, input_param=True)
        for n, t in outs:
            call(BP, "add_function_param", graph=gr, param_name=n, param_type=t, input_param=False)
    call(BP, "write_graph_dsl", graph=gr, code=code)


EQ = "Utilities|String|EqualExactly(String)"
fn("CycleMicMode", [], [], f"""
(fn CycleMicMode ()
  (bind m (Variables|Default|GetMicMode))
  (if ({EQ} m "ptt")
    (Variables|Default|SetMicMode "open")
    (elif ({EQ} m "open")
      (Variables|Default|SetMicMode "off")
      (else
        (Variables|Default|SetMicMode "ptt")))))
""")
fn("MicLabel", [], [("Label", "string")], f"""
(fn MicLabel ()
  (bind st (Variables|Default|GetVoiceStatus))
  (if (not (Utilities|String|IsEmpty st))
    (return (Utilities|String|Append "ไมค์: " st)))
  (bind m (Variables|Default|GetMicMode))
  (if ({EQ} m "open")
    (return "ไมค์: เปิดตลอด พูดได้เลย  (M เปลี่ยนโหมด)"))
  (if ({EQ} m "off")
    (return "ไมค์: ปิด  (M เปลี่ยนโหมด)"))
  (if (Variables|Default|GetPTTDown)
    (return "ไมค์: กำลังฟัง... ปล่อย V เพื่อส่ง"))
  (return "ไมค์: กดค้าง V เพื่อพูด  (M เปลี่ยนโหมด)"))
""")

# Tick: add the mic bar update (keep the PendingInput hand-off from keeper_game.dsl)
with open("keeper_game.dsl", encoding="utf-8") as f:
    dsl = f.read()
old_tick = """(event EventTick (DeltaSeconds)
  (bind p (Variables|Default|GetPendingInput))
  (if (not (Utilities|String|IsEmpty p))
    (CallFunction|Ask :Text p)
    (Variables|Default|SetPendingInput "")))"""
new_tick = """(event EventTick (DeltaSeconds)
  (bind p (Variables|Default|GetPendingInput))
  (if (not (Utilities|String|IsEmpty p))
    (CallFunction|Ask :Text p)
    (Variables|Default|SetPendingInput ""))
  (bind cw (Variables|Default|GetChatW))
  (Utilities|IsValid cw
    (:"Is Valid"
      (Class|WBPChat|SetMic :self cw :Level (Variables|Default|GetMicLevel) :Label (CallFunction|MicLabel)))
    (:"Is Not Valid")))"""
if old_tick in dsl:
    dsl = dsl.replace(old_tick, new_tick)
    with open("keeper_game.dsl", "w", encoding="utf-8") as f:
        f.write(dsl)
print("tick updated:", new_tick in dsl)

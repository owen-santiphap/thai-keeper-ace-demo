"""BP_Keeper text/voice sync: vars VoiceOn + SpeakLine (written by voice_service.py), Waiting + WaitSince
(12 s fallback), functions ShowReply(Line) and WaitVoice(). Then rebuild all logic with build_keeper_logic.py."""
import runpy

from bpkit import bp_ref, ensure_var
from ue import BP, call, ref

P = "/Game/Keeper/BP_Keeper"
b = bp_ref(P)

for name, t, remote in [("VoiceOn", "bool", True), ("SpeakLine", "string", True),
                        ("Waiting", "bool", False), ("WaitSince", "float", False)]:
    ensure_var(P, name, t)
    if remote:  # Remote Control can only read/write instance-editable properties
        call(BP, "set_variable_instance_editable", blueprint=b, variable_name=name, instance_editable=True)

for name, ins in [("ShowReply", [("Line", "string")]), ("WaitVoice", [])]:
    try:
        call(BP, "get_graph", blueprint=b, graph_name=name)
    except RuntimeError:
        call(BP, "add_function_graph", blueprint=b, graph_name=name)
        for n, t in ins:
            call(BP, "add_function_param", graph=ref(f"{P}.BP_Keeper:{name}"), param_name=n, param_type=t,
                 input_param=True)
call(BP, "compile_blueprint", blueprint=b, warnings_as_errors=False)

runpy.run_path("build_keeper_logic.py", run_name="__main__")

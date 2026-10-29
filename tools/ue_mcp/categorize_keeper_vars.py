"""Group BP_Keeper's variables into categories so the My Blueprint panel reads by topic.
The graph DSL names variables by category (Variables|Default|GetX), so build_keeper_logic.py calls
set_categories(default=True) before writing graphs and set_categories() after."""
from bpkit import bp_ref, compile_save
from ue import BP, call

P = "/Game/Keeper/BP_Keeper"
CATS = {
    "1 Conversation": ["ReplyText", "ReplyId", "Busy", "LastPlayerLine", "Ctx", "DoneNote"],
    "2 Voice link": ["PendingInput", "VoiceOn", "SpeakLine", "Waiting", "WaitSince", "MicMode", "PTTDown",
                              "MicLevel", "VoiceStatus"],
    "3 Confirm before acting": ["PendingTool", "PendingArg", "ViaTool", "ToolArgs", "CurTool"],
    "4 Walking": ["Walking", "WpIndex", "Mode", "GoalX", "GoalY", "ReturnY", "TargetSpot"],
    "5 Scene and UI": ["Gate", "Lantern", "ChatW", "BubbleW", "GhostsSeen"],
    "6 Easter egg": ["Dancing", "PartyUntil", "NextHop"],
}


def set_categories(default=False):
    have = set(call(BP, "list_variables", blueprint=bp_ref(P)) or [])
    for cat, names in CATS.items():
        for n in names:
            if n in have:
                call(BP, "set_variable_category", blueprint=bp_ref(P), variable_name=n,
                     category="Default" if default else cat)


if __name__ == "__main__":
    set_categories()
    print("saved:", compile_save(P))

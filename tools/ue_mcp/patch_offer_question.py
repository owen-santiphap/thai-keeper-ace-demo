"""Patch (2026-10-21, Owen): offer questions must be "ให้ลุง...มั้ย", not "ลุงจะ...มั้ย".
The model asked "ลุงจะพาหลานไปดูผีในป่าช้ามั้ย?" (reads as "will uncle take you?") when it meant
"shall I take you?" = "ให้ลุงพาไปดูผีในป่าช้ามั้ย". FixOffer rewrites it in code, inside one sentence only
(Thai sentences are split by spaces): "ลุงจะ" followed by "มั้ย" with no space in between -> "ให้ลุง",
"ให้ลุงพาหลาน" -> "ให้ลุงพา", and the Thai-unusual "?" is dropped. Statements ("เดี๋ยวลุงจะพาไปดูนะ") are untouched.
CleanSpeech calls FixOffer last. Writes only CleanSpeech + FixOffer (not build_keeper_logic.py's other graphs)."""
from bpkit import compile_save, prune_graph
from ue import BP, call, ref

P = "/Game/Keeper/BP_Keeper"
R = "Utilities|String|Replace"
G = lambda n: ref(f"{P}.BP_Keeper:{n}")  # noqa: E731

try:
    call(BP, "get_graph", blueprint=ref(f"{P}.BP_Keeper"), graph_name="FixOffer")
except RuntimeError:
    call(BP, "add_function_graph", blueprint=ref(f"{P}.BP_Keeper"), graph_name="FixOffer")
    call(BP, "add_function_param", graph=G("FixOffer"), param_name="S", param_type="string", input_param=True)
    call(BP, "add_function_param", graph=G("FixOffer"), param_name="Out", param_type="string", input_param=False)

FIX = f"""
(fn FixOffer (S)
  ; offer question: "ลุงจะ...มั้ย" -> "ให้ลุง...มั้ย" when both are in the same sentence (no space between)
  (bind s0 ({R} :SourceString S :From "?" :To ""))
  (bind i (Utilities|String|FindSubstring :SearchIn s0 :Substring "ลุงจะ" :bUseCase true :bSearchFromEnd false :StartPosition -1))
  (if (< i 0) (return s0))
  (bind rest (Utilities|String|RightChop :SourceString s0 :Count i))
  (bind q (Utilities|String|FindSubstring :SearchIn rest :Substring "มั้ย" :bUseCase true :bSearchFromEnd false :StartPosition -1))
  (if (< q 0) (return s0))
  (bind sp (Utilities|String|FindSubstring :SearchIn rest :Substring " " :bUseCase true :bSearchFromEnd false :StartPosition -1))
  (if (and (>= sp 0) (< sp q)) (return s0))
  ; "จะให้ลุง" is already the right form; "ลุงจะ" right after "ให้" would double it
  (bind fixed (Utilities|String|Append (Utilities|String|Left :SourceString s0 :Count i) (Utilities|String|Append "ให้ลุง" (Utilities|String|RightChop :SourceString rest :Count 5))))
  (return ({R} :SourceString fixed :From "ให้ลุงพาหลาน" :To "ให้ลุงพา")))
"""
call(BP, "write_graph_dsl", graph=G("FixOffer"), code=FIX)

CLEAN = f"""
(fn CleanSpeech (S)
  ; Owen's word rules enforced in code (a 4B model does not follow style rules reliably):
  ; ไหม -> มั้ย (keep ไหม้ "burn"), drop ครับ, สุสาน -> ป่าช้า, offer "ลุงจะ...มั้ย" -> "ให้ลุง...มั้ย"
  (bind a ({R} :SourceString S :From "ไหม้" :To "@@"))
  (bind b ({R} :SourceString a :From "ไหม" :To "มั้ย"))
  (bind c ({R} :SourceString b :From "@@" :To "ไหม้"))
  ; the model sometimes slips into the kid's voice ("...ครับลุง"); drop the whole tail, not just ครับ
  (bind c2 ({R} :SourceString c :From "นะครับลุง" :To ""))
  (bind c3 ({R} :SourceString c2 :From "ครับลุง" :To ""))
  (bind d ({R} :SourceString c3 :From "ครับ" :To ""))
  ; FixOffer has exec pins: bind it so it runs in the chain (inlined in return it never executes and gives "")
  (bind out (CallFunction|FixOffer :S ({R} :SourceString d :From "สุสาน" :To "ป่าช้า")))
  (return out))
"""
call(BP, "write_graph_dsl", graph=G("CleanSpeech"), code=CLEAN)
for n in ("FixOffer", "CleanSpeech"):
    print(n, prune_graph(G(n)))
    call(BP, "arrange_nodes", nodes=call(BP, "find_nodes", graph=G(n), title="", entry_points_only=False))
print("saved:", compile_save(P))

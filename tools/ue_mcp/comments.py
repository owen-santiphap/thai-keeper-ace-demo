"""Comment boxes ("groups") for Blueprint graphs.

Epic's MCP cannot create comment nodes, so: `python comments.py clip <graph>` puts N blank comment nodes on the
clipboard (T3D text) -> paste them into the open graph (Ctrl+V in the graph editor) -> `python comments.py fix <graph>`
sets each comment's text, colour, position and size from SPEC through MCP properties.
Graph = "EventGraph" or a function name of BP_Keeper. Positions come from layout/BP_Keeper.json (EventGraph rows) or
from the bounds of all nodes (functions)."""
import json
import subprocess
import sys
import uuid
from pathlib import Path

from bpkit import compile_save, node_infos
from ue import BP, OBJ, call, ref

P = "/Game/Keeper/BP_Keeper"
HERE = Path(__file__).parent
PAD = 80
# colours (linear RGB) by topic
C_START, C_TALK, C_ACT, C_WALK, C_VOICE = ((0.10, 0.45, 0.25), (0.10, 0.30, 0.60), (0.60, 0.35, 0.05),
                                           (0.45, 0.15, 0.55), (0.55, 0.10, 0.30))
EVENT_SPEC = {  # event type_id -> (comment text, colour)
    "AddEvent|EventBeginPlay": ("START  |  ตั้งค่าเกม: หน้าแชท ประตู ตะเกียง", C_START),
    "AddEvent|EventTick": ("EVERY FRAME  |  รับเสียงผู้เล่น · บับเบิลข้อความ · เดิน · แถบไมค์", C_WALK),
    "OnLLMReady": ("LLM READY  |  โมเดลโหลดเสร็จ ลุงทักทาย", C_TALK),
    "OnTokenStreamed": ("REPLY STREAMING  |  ข้อความไหลเข้ามา กรองคำ (ไหม->มั้ย, ตัด ครับ)", C_TALK),
    "OnResponseComplete": ("REPLY DONE  |  ส่งให้ระบบเสียง และจำคำถาม จะให้ลุง...มั้ย", C_TALK),
    "OnToolCalled": ("TOOL REQUEST  |  โมเดลขอใช้เครื่องมือ: ยังไม่ทำ รอหลานตอบตกลง", C_ACT),
    "OnLLMError": ("LLM ERROR  |  แจ้งปัญหา ให้พูดใหม่", C_TALK),
    "GuideToSpot": ("GUIDE  |  หาจุดผีแล้วเดินพาไป", C_ACT),
    "EventActorBeginOverlap": ("UNUSED  |  event ว่างจากเทมเพลต (ลบได้)", (0.20, 0.20, 0.20)),
    "SetBubble": ("SET BUBBLE  |  ผูกบับเบิลข้อความเหนือหัวลุง", C_VOICE),
}
FUNC_SPEC = {  # function -> (comment text, colour)
    "Ask": ("ASK  |  หลานพูดมา: ตอบตกลง? -> ทำ · ขอให้ทำอะไร? -> ถามยืนยัน · นอกนั้นส่งให้ LLM", C_TALK),
    "DetectAction": ("DETECT ACTION  |  จับคำขอ จุดไฟ / เปิดประตู / พาไปดูผี แล้วถามยืนยันเอง", C_ACT),
    "IsYes": ("IS YES  |  คำตอบสั้น มีคำว่า ได้/เอา/ไป และไม่มี ไม่/หน่อย/คำถาม", C_ACT),
    "DoPending": ("DO PENDING  |  หลานตกลงแล้ว: เลือกเป้าหมายแล้วเริ่มเดิน", C_ACT),
    "UpdateWalk": ("UPDATE WALK  |  เดินไปจุดถัดไป · เปิดประตูเมื่อถึง · Arrive เมื่อถึงปลายทาง", C_WALK),
    "GetWaypoint": ("WAYPOINTS  |  เส้นทาง: หน้าประตู -> ในป่าช้า -> จุดหมาย", C_WALK),
    "Arrive": ("ARRIVE  |  ถึงแล้ว: จุดตะเกียง / เปิดประตู / เผยผี แล้วพูด", C_WALK),
    "StartWalk": ("START WALK  |  อยู่ในหรือนอกรั้ว เลือกจุดเริ่มเส้นทาง", C_WALK),
    "CleanSpeech": ("CLEAN SPEECH  |  กฎภาษาลุงบุญในโค้ด: ไหม->มั้ย · ตัด ครับ · สุสาน->ป่าช้า", C_TALK),
    "Speak": ("SPEAK  |  บทพูดที่เขียนไว้ (ไม่ผ่าน LLM) ส่งไปให้ระบบเสียง", C_VOICE),
    "WaitVoice": ("WAIT VOICE  |  ขึ้น ลุงบุญกำลังคิด... รอเสียงท่อนแรก", C_VOICE),
    "ShowReply": ("SHOW REPLY  |  แสดงข้อความในบับเบิลและแชท", C_VOICE),
    "FinishReply": ("FINISH REPLY  |  ตอบจบ: บอกระบบเสียง แสดง และจำคำถามยืนยัน", C_TALK),
    "RememberConfirmQuestion": ("REMEMBER CONFIRM  |  ถ้าลุงถาม จะให้ลุง...มั้ย ให้จำว่ารอทำอะไร", C_ACT),
    "HoldToolCall": ("HOLD TOOL CALL  |  ยังไม่ทำตามโมเดล รอหลานตอบตกลงก่อน", C_ACT),
    "SetupScene": ("SETUP SCENE  |  ทักทาย หาประตูและตะเกียง เปิดหน้าแชท", C_START),
}


def graph_ref(g):
    return ref(f"{P}.BP_Keeper:{g}")


def boxes(g):
    """[(text, colour, x, y, w, h)] for graph g."""
    gr = graph_ref(g)
    nodes = call(BP, "find_nodes", graph=gr, title="", entry_points_only=False) or []
    info = [n for n in node_infos(nodes) if "Comment" not in n["node"]["refPath"]]
    if g == "EventGraph":
        layout = json.loads((HERE / "layout" / "BP_Keeper.json").read_text(encoding="utf-8"))["EventGraph"]
        out = []
        for key, (x, y, w, h) in layout.items():
            tid = key.split(" ", 1)[1]
            spec = next((v for k, v in EVENT_SPEC.items() if k in tid), (tid, C_START))
            out.append((spec[0], spec[1], x - PAD, y - PAD - 40, w + 2 * PAD, h + 2 * PAD + 40))
        return out
    xs = [n["position"]["x"] for n in info]
    ys = [n["position"]["y"] for n in info]
    text, col = FUNC_SPEC[g]
    return [(text, col, min(xs) - PAD, min(ys) - PAD - 40, max(xs) - min(xs) + 360 + 2 * PAD,
             max(ys) - min(ys) + 200 + 2 * PAD + 40)]


def clip(g):
    n = len(boxes(g))
    t3d = ""
    for i in range(n):
        t3d += (f'Begin Object Class=/Script/UnrealEd.EdGraphNode_Comment Name="EdGraphNode_Comment_{i}"\n'
                f'   NodePosX={i * 500}\n   NodePosY=0\n   NodeWidth=400\n   NodeHeight=100\n'
                f'   NodeComment="group {i}"\n   NodeGuid={uuid.uuid4().hex.upper()}\nEnd Object\n')
    f = HERE / "layout" / "comments_clip.t3d"  # via a file: piping into Set-Clipboard joins the lines
    f.write_text(t3d, encoding="utf-8")
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    f"Set-Clipboard -Value ([IO.File]::ReadAllText('{f}'))"], check=True)
    print(f"{n} comment nodes on the clipboard for {g}")


def fix(g):
    gr = graph_ref(g)
    # find_nodes' class filter does not match comment nodes; filter by object name instead
    comments = [n for n in call(BP, "find_nodes", graph=gr, title="", entry_points_only=False) or []
                if "EdGraphNode_Comment" in n["refPath"]]
    want = boxes(g)
    if len(comments) < len(want):
        raise SystemExit(f"{g}: {len(comments)} comments in graph, need {len(want)} - paste first")
    for c, (text, col, x, y, w, h) in zip(comments, want):
        vals = {"NodeComment": text, "NodePosX": int(x), "NodePosY": int(y), "NodeWidth": int(w),
                "NodeHeight": int(h), "CommentColor": {"R": col[0], "G": col[1], "B": col[2], "A": 1.0},
                "FontSize": 28, "bCommentBubbleVisible_InDetailsPanel": False}
        call(OBJ, "set_properties", instance=c, values=json.dumps(vals, ensure_ascii=False))
    for c in comments[len(want):]:
        call(BP, "delete_node", node=c)
    print(f"{g}: {len(want)} comment boxes placed;", "saved:", compile_save(P))


if __name__ == "__main__":
    {"clip": clip, "fix": fix}[sys.argv[1]](sys.argv[2])

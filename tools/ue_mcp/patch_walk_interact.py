"""One-off patch (2026-10-20): walk-to-interact + persona lines in build_keeper_logic.py and keeper_game.dsl.
The keeper walks to the lantern / gate before acting, opens the gate when he reaches it on a guide walk, lights
lanterns he passes once the gate lantern is lit, and every scripted line follows 04_keeper/KEEPER_PERSONA.md."""
p = "build_keeper_logic.py"
s = open(p, encoding="utf-8").read()
EQ = "Utilities|String|EqualExactly(String)"


def swap(name, new):
    global s
    start = s.index(f'    "{name}": """')
    end = s.index('""",', start) + len('""",')
    s = s[:start] + f'    "{name}": """\n' + new.strip("\n") + '\n""",' + s[end:]


swap("DoPending", f"""
(fn DoPending ()
  (bind t (Variables|Default|GetPendingTool))
  (Variables|Default|SetPendingTool "")
  (if (Variables|Default|GetWalking)
    (CallFunction|Speak :Line "ใจเย็นๆ หลาน ลุงยังเดินอยู่เลย เหอะๆ")
    (return))
  (if ({EQ} t "light_lantern")
    (if (Class|BPLantern|GetIsLit :self (Variables|Default|GetLantern))
      (CallFunction|Speak :Line "ตะเกียงจุดอยู่แล้วนะหลาน สว่างแล้วเห็นมั้ย")
      (return))
    (bind ll (Transformation|GetActorLocation :self (Variables|Default|GetLantern)))
    (Variables|Default|SetGoalX (.x ll))
    (Variables|Default|SetGoalY (.y ll))
    (Variables|Default|SetMode "lantern")
    (CallFunction|Speak :Line "ได้เลยหลาน รอแป๊บนะ ลุงเดินไปจุดตะเกียงก่อน")
    (CallFunction|StartWalk)
    (elif ({EQ} t "open_gate")
      (if (Class|BPGate|GetIsOpen :self (Variables|Default|GetGate))
        (CallFunction|Speak :Line "ประตูเปิดอยู่แล้วนะหลาน เข้ามาได้เลย")
        (return))
      (Variables|Default|SetGoalX (select (> (.x (Transformation|GetActorLocation)) 1000.0) 1120.0 880.0))
      (Variables|Default|SetGoalY 0.0)
      (Variables|Default|SetMode "gate")
      (CallFunction|Speak :Line "ได้เลย เดี๋ยวลุงเดินไปเปิดประตูให้นะ")
      (CallFunction|StartWalk)
      (elif ({EQ} t "guide_to_ghost")
        (Variables|Default|SetToolArgs (CallFunction|GhostIdFrom :S (Variables|Default|GetPendingArg)))
        (Variables|Default|SetMode "ghost")
        (CallFunction|Speak :Line "มาเลยหลาน เดินตามลุงมาติดๆ ระวังรากไม้ด้วยนะ")
        (CallFunction|GuidetoSpot))))
  (Variables|Default|SetPendingArg ""))
""")

swap("GetWaypoint", f"""
(fn GetWaypoint (I)
  (if ({EQ} (Variables|Default|GetMode) "ghost")
    (bind t (Transformation|GetActorLocation :self (Variables|Default|GetTargetSpot)))
    (if (== I 0)
      (return (Math|Vector|MakeVector :X 880.0 :Y 0.0 :Z 0.0)))
    (if (== I 1)
      (return (Math|Vector|MakeVector :X 1300.0 :Y 0.0 :Z 0.0)))
    (if (== I 2)
      (return (Math|Vector|MakeVector :X 1300.0 :Y (.y t) :Z 0.0)))
    (return t))
  (if (== I 0)
    (return (Math|Vector|MakeVector :X 1300.0 :Y (Variables|Default|GetReturnY) :Z 0.0)))
  (if (== I 1)
    (return (Math|Vector|MakeVector :X 1300.0 :Y 0.0 :Z 0.0)))
  (if (and (== I 2) (not ({EQ} (Variables|Default|GetMode) "gate")))
    (return (Math|Vector|MakeVector :X 880.0 :Y 0.0 :Z 0.0)))
  (return (Math|Vector|MakeVector :X (Variables|Default|GetGoalX) :Y (Variables|Default|GetGoalY) :Z 0.0)))
""")

swap("Arrive", f"""
(fn Arrive ()
  (bind m (Variables|Default|GetMode))
  (if ({EQ} m "lantern")
    (Class|BPLantern|LightLantern :self (Variables|Default|GetLantern))
    (Variables|Default|SetDoneNote "จุดตะเกียงให้หลานแล้ว")
    (CallFunction|Speak :Line "นั่นไง ไฟติดแล้ว สว่างขึ้นเยอะเลยใช่มั้ยหลาน เหอะๆ")
    (return))
  (if ({EQ} m "gate")
    (Class|BPGate|OpenGate :self (Variables|Default|GetGate))
    (Variables|Default|SetDoneNote "เปิดประตูให้หลานแล้ว")
    (CallFunction|Speak :Line "ประตูเปิดแล้ว เข้ามาสิหลาน ไม่ต้องกลัว ผีเขาไม่กัดหรอก หึๆ")
    (return))
  (bind t (Variables|Default|GetTargetSpot))
  (Variables|Default|SetDoneNote "พาหลานมาดูผีแล้ว")
  (CallFunction|Speak :Line "ถึงแล้วหลาน ดูนั่นสิ เห็นมั้ย หึๆ อย่าเพิ่งวิ่งหนีล่ะ")
  (if (not (Class|BPGhostSpot|GetRevealed :self t))
    (Class|BPGhostSpot|Reveal :self t)
    (Variables|Default|SetGhostsSeen (+ (Variables|Default|GetGhostsSeen) 1))
    (Class|WBPChat|SetScore :self (Variables|Default|GetChatW)
      :Line (Utilities|String|Append (Utilities|String|Append "ผีที่พบ " (Utilities|String|ToString(Integer) (Variables|Default|GetGhostsSeen))) "/4"))))
""")

NEW_FUNCS = f'''    "StartWalk": """
(fn StartWalk ()
  (bind x (.x (Transformation|GetActorLocation)))
  (Variables|Default|SetReturnY (.y (Transformation|GetActorLocation)))
  (if ({EQ} (Variables|Default|GetMode) "ghost")
    (Variables|Default|SetWpIndex (select (> x 1150.0) 1 0))
    (else
      (Variables|Default|SetWpIndex (select (> x 1150.0) 0 3))))
  (Variables|Default|SetWalking true))
""",
    "LightNearby": """
(fn LightNearby ()
  (for a (Actor|GetAllActorsOfClass :ActorClass "/Game/Keeper/BP_Lantern.BP_Lantern_C")
    (bind l (Utilities|Casting|CastToBP_Lantern :Object a)
      (:then
        (if (and (not (Class|BPLantern|GetIsLit :self l)) (< (Transformation|GetDistanceTo :OtherActor l) 320.0))
          (Class|BPLantern|LightLantern :self l)))
      (:CastFailed))))
""",
'''
if '"StartWalk"' not in s:
    s = s.replace('    "Ask": """', NEW_FUNCS + '    "Ask": """', 1)

s = s.replace('"คุณ: "', '"หลาน: "').replace('"ลุงบุญกำลังคิด..."', '"เอ... ลุงขอนึกแป๊บนะหลาน"')

SETUP = '''for _n, _t in [("Mode", "string"), ("GoalX", "float"), ("GoalY", "float"), ("ReturnY", "float")]:
    ensure_var(P, _n, _t)  # walk-to-interact: what he walks for and where
for _fn in ["StartWalk", "LightNearby"]:
    try:
        call(BP, "get_graph", blueprint=ref(f"{P}.BP_Keeper"), graph_name=_fn)
    except RuntimeError:
        call(BP, "add_function_graph", blueprint=ref(f"{P}.BP_Keeper"), graph_name=_fn)
'''
if "walk-to-interact" not in s:
    s = s.replace("for attempt in range(3):", SETUP + "for attempt in range(3):", 1)
open(p, "w", encoding="utf-8").write(s)

p = "keeper_game.dsl"
d = open(p, encoding="utf-8").read()
reps = [
    ('"ลุงบุญกำลังตื่น... รอสักครู่นะหลาน"', '"เดี๋ยวนะหลาน ลุงเพิ่งตื่น ขอบิดขี้เกียจแป๊บ เหอะๆ"'),
    ('"สวัสดีหลาน ลุงบุญเฝ้าป่าช้านี้มาสามสิบปีแล้ว อยากฟังเรื่องผีมั้ย"',
     '"มาๆ หลาน เข้ามาใกล้ๆ ไม่ต้องกลัว ลุงบุญเฝ้าป่าช้านี้มาสามสิบปีแล้ว อยากฟังเรื่องผีมั้ยล่ะ หึๆ"'),
    ('"ยังไม่ได้ทำ ต้องให้ผู้เยี่ยมยืนยันก่อน ให้ถามผู้เยี่ยมสั้นๆ ว่า จะให้ลุงทำเลยมั้ย"',
     '"ยังไม่ได้ทำ ต้องให้หลานตอบตกลงก่อน ให้ถามหลานสั้นๆ ว่า จะให้ลุงทำเลยมั้ยหลาน"'),
    ('"ผีตนนี้ไม่มีที่อยู่ในป่าช้านี้นะหลาน แต่ลุงเล่าเรื่องให้ฟังได้"',
     '"ผีตนนี้ไม่มีที่ให้ไปดูในป่าช้านี้หรอกหลาน แต่ลุงเล่าให้ฟังได้นะ"'),
    ('"ลุงงงนิดหน่อย ถามใหม่อีกทีนะหลาน"', '"แหะ ลุงหูตึงไปหน่อย พูดใหม่อีกทีสิหลาน"'),
    ('''      (if (not (Class|BPGate|GetIsOpen :self (Variables|Default|GetGate)))
        (Class|BPGate|OpenGate :self (Variables|Default|GetGate)))
      (Variables|Default|SetWpIndex (select (> (.x (Transformation|GetActorLocation)) 1150.0) 1 0))
      (Variables|Default|SetWalking true))''',
     '''      (CallFunction|StartWalk))'''),
    ('''    (if (< (Math|Vector|VectorLength d) (select (>= (Variables|Default|GetWpIndex) 3) 170.0 60.0))
      (Variables|Default|SetWpIndex (+ (Variables|Default|GetWpIndex) 1))''',
     '''    (if (Class|BPLantern|GetIsLit :self (Variables|Default|GetLantern))
      (CallFunction|LightNearby))
    (if (< (Math|Vector|VectorLength d) (select (>= (Variables|Default|GetWpIndex) 3) 120.0 60.0))
      (Variables|Default|SetWpIndex (+ (Variables|Default|GetWpIndex) 1))
      (if (and (== (Variables|Default|GetWpIndex) 1) (not (Class|BPGate|GetIsOpen :self (Variables|Default|GetGate))))
        (Class|BPGate|OpenGate :self (Variables|Default|GetGate)))'''),
]
for a, b in reps:
    assert d.count(a) == 1, a[:60]
    d = d.replace(a, b)
open(p, "w", encoding="utf-8").write(d)
print("patched")

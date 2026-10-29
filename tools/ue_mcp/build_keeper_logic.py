"""Write BP_Keeper's functions and event graph (keeper_game.dsl), compile, save.

write_graph_dsl compiles the whole Blueprint after each graph; when another graph still holds stale nodes that
compile fails even though this graph was written, so extra passes are made.
"""
from bpkit import compile_save
from ue import BP, call, ref

P = "/Game/Keeper/BP_Keeper"
C = "Utilities|String|Contains"

FUNCS = {
    "ShowSpeech": """
(fn ShowSpeech (Line)
  (bind bw (Utilities|Casting|CastToWBP_Bubble :Object (UserInterface|GetUserWidgetObject :self (Variables|Default|GetBubble)))
    (:then (Class|WBPBubble|ShowLine :self bw :Line Line))
    (:CastFailed)))
""",
    "IsYes": f"""
(fn IsYes (S)
  ; a yes is a short reply; long lines, new requests (หน่อย) and questions are not, but naming the action is fine
  ; ("เปิดประตูเลยครับ", "จุดเลย", "พาไปเลย")
  (if (or (or (> (Utilities|String|Len :S S) 20) ({C} :SearchIn S :Substring "ไม่"))
          (or (or (or ({C} :SearchIn S :Substring "หน่อย") ({C} :SearchIn S :Substring "มั้ย"))
                  (or ({C} :SearchIn S :Substring "ไหม") ({C} :SearchIn S :Substring "ขอบ")))
              (or (or ({C} :SearchIn S :Substring "คือ") ({C} :SearchIn S :Substring "อะไร"))
                  (or (or ({C} :SearchIn S :Substring "ใคร") ({C} :SearchIn S :Substring "ทำไม"))
                      (or ({C} :SearchIn S :Substring "ที่ไหน") ({C} :SearchIn S :Substring "ยังไง"))))))
    (return false))
  (return (or (or (or ({C} :SearchIn S :Substring "ครับ") ({C} :SearchIn S :Substring "ค่ะ"))
                  (or ({C} :SearchIn S :Substring "ใช่") ({C} :SearchIn S :Substring "ได้")))
              (or (or (or ({C} :SearchIn S :Substring "ตกลง") ({C} :SearchIn S :Substring "โอเค"))
                      (or ({C} :SearchIn S :Substring "เลย") ({C} :SearchIn S :Substring "ok")))
                  (or ({C} :SearchIn S :Substring "เอา") ({C} :SearchIn S :Substring "จ้ะ"))))))
""",
    "GhostIdFrom": f"""
(fn GhostIdFrom (S)
  (if (or ({C} :SearchIn S :Substring "กระสือ") ({C} :SearchIn S :Substring "krasue"))
    (return "krasue"))
  (if (or ({C} :SearchIn S :Substring "ตานี") ({C} :SearchIn S :Substring "tani"))
    (return "tani"))
  (if (or ({C} :SearchIn S :Substring "กองกอย") ({C} :SearchIn S :Substring "kong_koi"))
    (return "kong_koi"))
  (if (or ({C} :SearchIn S :Substring "เปรต") ({C} :SearchIn S :Substring "pret"))
    (return "pret"))
  (return ""))
""",
    "ShowReply": """
(fn ShowReply (Line)
  (CallFunction|ShowSpeech :Line Line)
  (Class|WBPChat|SetLog :self (Variables|Default|GetChatW)
    :Line (Utilities|String|Append (Utilities|String|Append "หลาน: " (Variables|Default|GetLastPlayerLine))
                                   (Utilities|String|Append "\nลุงบุญ: " Line))))
""",
    "WaitVoice": """
(fn WaitVoice ()
  (Variables|Default|SetWaiting true)
  (Variables|Default|SetWaitSince (Utilities|Time|GetGameTimeinSeconds)))
""",
    "Speak": """
(fn Speak (Line)
  (Variables|Default|SetReplyText Line)
  (Variables|Default|SetReplyId (+ (Variables|Default|GetReplyId) 1))
  (if (Variables|Default|GetVoiceOn)
    (CallFunction|ShowSpeech :Line "เอ... ขอลุงนึกแป๊บ")
    (CallFunction|WaitVoice)
    (else
      (CallFunction|ShowReply :Line Line))))
""",
    "DoPending": """
(fn DoPending ()
  ; copy first: a getter re-reads the variable when used, so clearing PendingTool would empty t too
  (Variables|Default|SetCurTool (Variables|Default|GetPendingTool))
  (Variables|Default|SetPendingTool "")
  (bind t (Variables|Default|GetCurTool))
  (if (Variables|Default|GetWalking)
    (CallFunction|Speak :Line "ใจเย็นๆ ลุงยังเดินอยู่เลย เหอะๆ")
    (return))
  (if (Utilities|String|EqualExactly(String) t "light_lantern")
    (if (Class|BPLantern|GetIsLit :self (Variables|Default|GetLantern))
      (CallFunction|Speak :Line "ตะเกียงจุดอยู่แล้ว ดูสิ สว่างดีแล้ว")
      (return))
    (bind ll (Transformation|GetActorLocation :self (Variables|Default|GetLantern)))
    (Variables|Default|SetGoalX (.x ll))
    (Variables|Default|SetGoalY (.y ll))
    (Variables|Default|SetMode "lantern")
    (CallFunction|Speak :Line "ได้เลย รอแป๊บนะ ลุงเดินไปจุดตะเกียงก่อน")
    (CallFunction|StartWalk)
    (elif (Utilities|String|EqualExactly(String) t "open_gate")
      (if (Class|BPGate|GetIsOpen :self (Variables|Default|GetGate))
        (CallFunction|Speak :Line "ประตูเปิดอยู่แล้ว เข้ามาได้เลย")
        (return))
      (Variables|Default|SetGoalX (select (> (.x (Transformation|GetActorLocation)) 1000.0) 1120.0 880.0))
      (Variables|Default|SetGoalY 0.0)
      (Variables|Default|SetMode "gate")
      (CallFunction|Speak :Line "ได้เลย เดี๋ยวลุงเดินไปเปิดประตูให้")
      (CallFunction|StartWalk)
      (elif (Utilities|String|EqualExactly(String) t "guide_to_ghost")
        (Variables|Default|SetToolArgs (CallFunction|GhostIdFrom :S (Variables|Default|GetPendingArg)))
        (Variables|Default|SetMode "ghost")
        (CallFunction|Speak :Line "มาเลย เดินตามลุงมาติดๆ ระวังรากไม้ด้วยนะ")
        (CallFunction|GuidetoSpot))))
  (Variables|Default|SetPendingArg ""))
""",
    "GetWaypoint": """
(fn GetWaypoint (I)
  (if (Utilities|String|EqualExactly(String) (Variables|Default|GetMode) "ghost")
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
  (if (and (== I 2) (not (Utilities|String|EqualExactly(String) (Variables|Default|GetMode) "gate")))
    (return (Math|Vector|MakeVector :X 880.0 :Y 0.0 :Z 0.0)))
  (return (Math|Vector|MakeVector :X (Variables|Default|GetGoalX) :Y (Variables|Default|GetGoalY) :Z 0.0)))
""",
    "Arrive": """
(fn Arrive ()
  (bind m (Variables|Default|GetMode))
  (if (Utilities|String|EqualExactly(String) m "lantern")
    (Class|BPLantern|LightLantern :self (Variables|Default|GetLantern))
    (Variables|Default|SetDoneNote "จุดตะเกียงให้หลานแล้ว")
    (CallFunction|Speak :Line "นั่นไง ไฟติดแล้ว สว่างขึ้นเยอะเลย เหอะๆ")
    (return))
  (if (Utilities|String|EqualExactly(String) m "gate")
    (Class|BPGate|OpenGate :self (Variables|Default|GetGate))
    (Variables|Default|SetDoneNote "เปิดประตูให้หลานแล้ว")
    (CallFunction|Speak :Line "ประตูเปิดแล้ว เข้ามาสิ ไม่ต้องกลัว ผีเขาไม่กัดหรอก หึๆ")
    (return))
  (bind t (Variables|Default|GetTargetSpot))
  (Variables|Default|SetDoneNote (Utilities|String|Append (Utilities|String|Append "พาหลานมาดู" (CallFunction|GhostName :Id (Variables|Default|GetToolArgs))) "แล้ว"))
  (CallFunction|Speak :Line "ถึงแล้ว ดูนั่นสิ หึๆ อย่าเพิ่งวิ่งหนีล่ะ")
  (if (not (Class|BPGhostSpot|GetRevealed :self t))
    (Class|BPGhostSpot|Reveal :self t)
    (Variables|Default|SetGhostsSeen (+ (Variables|Default|GetGhostsSeen) 1))
    (Class|WBPChat|SetScore :self (Variables|Default|GetChatW)
      :Line (Utilities|String|Append (Utilities|String|Append "ผีที่พบ " (Utilities|String|ToString(Integer) (Variables|Default|GetGhostsSeen))) "/4"))))
""",
    "StartWalk": """
(fn StartWalk ()
  (bind x (.x (Transformation|GetActorLocation)))
  (Variables|Default|SetReturnY (.y (Transformation|GetActorLocation)))
  (if (Utilities|String|EqualExactly(String) (Variables|Default|GetMode) "ghost")
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
    "CleanSpeech": """
(fn CleanSpeech (S)
  ; Owen's word rules enforced in code (a 4B model does not follow style rules reliably):
  ; ไหม -> มั้ย (keep ไหม้ "burn"), drop ครับ, สุสาน -> ป่าช้า
  (bind a (Utilities|String|Replace :SourceString S :From "ไหม้" :To "@@"))
  (bind b (Utilities|String|Replace :SourceString a :From "ไหม" :To "มั้ย"))
  (bind c (Utilities|String|Replace :SourceString b :From "@@" :To "ไหม้"))
  ; the model sometimes slips into the kid's voice ("...ครับลุง"); drop the whole tail, not just ครับ
  (bind c2 (Utilities|String|Replace :SourceString c :From "นะครับลุง" :To ""))
  (bind c3 (Utilities|String|Replace :SourceString c2 :From "ครับลุง" :To ""))
  (bind d (Utilities|String|Replace :SourceString c3 :From "ครับ" :To ""))
  (return (Utilities|String|Replace :SourceString d :From "สุสาน" :To "ป่าช้า")))
""",
    "GhostName": """
(fn GhostName (Id)
  (if (Utilities|String|EqualExactly(String) Id "krasue")
    (return "กระสือ"))
  (if (Utilities|String|EqualExactly(String) Id "tani")
    (return "นางตานี"))
  (if (Utilities|String|EqualExactly(String) Id "kong_koi")
    (return "ผีกองกอย"))
  (if (Utilities|String|EqualExactly(String) Id "pret")
    (return "เปรต"))
  (return "ผี"))
""",
    "DetectAction": """
(fn DetectAction (Text)
  ; action requests are recognised here, not by the LLM: the keeper asks the confirmation question himself
  (bind gid (CallFunction|GhostIdFrom :S Text))
  (if (and (or (Utilities|String|Contains :SearchIn Text :Substring "พา") (Utilities|String|Contains :SearchIn Text :Substring "ไปดู"))
           (not (Utilities|String|IsEmpty gid)))
    (Variables|Default|SetPendingTool "guide_to_ghost")
    (Variables|Default|SetPendingArg Text)
    (CallFunction|Speak :Line (Utilities|String|Append (Utilities|String|Append "จะให้ลุงพาไปดู" (CallFunction|GhostName :Id gid)) "เลยมั้ย"))
    (return true))
  (if (or (and (Utilities|String|Contains :SearchIn Text :Substring "จุด")
               (or (Utilities|String|Contains :SearchIn Text :Substring "ไฟ") (Utilities|String|Contains :SearchIn Text :Substring "ตะเกียง")))
          (Utilities|String|Contains :SearchIn Text :Substring "เปิดไฟ"))
    (Variables|Default|SetPendingTool "light_lantern")
    (CallFunction|Speak :Line "จะให้ลุงจุดไฟเลยมั้ย")
    (return true))
  (if (and (Utilities|String|Contains :SearchIn Text :Substring "เปิด") (Utilities|String|Contains :SearchIn Text :Substring "ประตู"))
    (Variables|Default|SetPendingTool "open_gate")
    (CallFunction|Speak :Line "จะให้ลุงเปิดประตูเลยมั้ย")
    (return true))
  (return false))
""",
    "Ask": """
(fn Ask (Text)
  (if (Variables|Default|GetBusy)
    (return))
  (Variables|Default|SetLastPlayerLine Text)
  (if (not (Utilities|String|IsEmpty (Variables|Default|GetPendingTool)))
    (if (CallFunction|IsYes :S Text)
      (CallFunction|DoPending)
      (return))
    (Variables|Default|SetPendingTool ""))
  ; easter egg (Owen): "เต้น" / "ปาร์ตี้" -> dance + light show + cats
  (if (or (Utilities|String|Contains :SearchIn Text :Substring "เต้น") (Utilities|String|Contains :SearchIn Text :Substring "ปาร์ตี้"))
    (Class|WBPChat|SetLog :self (Variables|Default|GetChatW) :Line (Utilities|String|Append "หลาน: " Text))
    (CallFunction|StartParty)
    (return))
  (if (CallFunction|DetectAction :Text Text)
    (return))
  (Variables|Default|SetBusy true)
  (Variables|Default|SetWaiting false)
  ; the plugin's running chat makes the 4B model drift and parrot old answers after a few turns, so every question
  ; starts a fresh conversation; continuity comes from a short note with his previous line (and what he just did)
  ; his previous line is passed on only when the kid asks him to go on (เล่าต่อ, แล้วไงต่อ); otherwise the model kept
  ; summarising the old topic unasked (Owen, 2026-10-20)
  (Variables|Default|SetCtx (select (Utilities|String|Contains :SearchIn Text :Substring "ต่อ")
    (Utilities|String|Append (Utilities|String|Append "[ลุงเพิ่งพูดว่า: " (Variables|Default|GetReplyText)) "] ") ""))
  (if (not (Utilities|String|IsEmpty (Variables|Default|GetDoneNote)))
    (Variables|Default|SetCtx (Utilities|String|Append (Utilities|String|Append (Utilities|String|Append (Variables|Default|GetCtx) "[เหตุการณ์: ลุงเพิ่ง") (Variables|Default|GetDoneNote)) "] ")))
  (Variables|Default|SetReplyText "")
  (Class|WBPChat|SetLog :self (Variables|Default|GetChatW) :Line (Utilities|String|Append "หลาน: " Text))
  (CallFunction|ShowSpeech :Line (select (Variables|Default|GetVoiceOn) "เอ... ขอลุงนึกแป๊บ" "..."))
  (NVIDIAACE|LLM|ResetConversation :self (Variables|Default|GetKeeperLLM))
  (NVIDIAACE|LLM|SendMessage :self (Variables|Default|GetKeeperLLM)
    :UserText (select (Utilities|String|IsEmpty (Variables|Default|GetCtx)) Text
                (Utilities|String|Append (Utilities|String|Append (Variables|Default|GetCtx) "หลานพูดว่า: ") Text)))
  (Variables|Default|SetDoneNote ""))
""",
    # ---- event bodies (the event graph only calls these) ----
    "SetupScene": """
(fn SetupScene ()
  ; at start: chat window on screen, find the gate and the gate lantern
  (CallFunction|ShowSpeech :Line "เดี๋ยวนะ ลุงเพิ่งตื่น ขอบิดขี้เกียจแป๊บ เหอะๆ")
  (CallFunction|FindGate)
  (CallFunction|FindGateLantern)
  (CallFunction|SetupChat))
""",
    "SetupChat": """
(fn SetupChat ()
  ; chat window (log, typing box, mic bar, ghost counter)
  (bind pc (Game|GetPlayerController :PlayerIndex 0))
  (Input|EnableInput :self self :PlayerController pc)
  (bind cw (Utilities|Casting|CastToWBP_Chat :Object (UserInterface|CreateWidget :Class "/Game/UI/WBP_Chat.WBP_Chat_C" :OwningPlayer pc))
    (:then
      (Variables|Default|SetChatW cw)
      (UserInterface|Viewport|AddtoViewport :self cw))
    (:CastFailed (Development|PrintString :InString "SETUP: chat widget failed"))))
""",
    "FindGate": """
(fn FindGate ()
  (bind g (Utilities|Casting|CastToBP_Gate :Object (Actor|GetActorOfClass :ActorClass "/Game/Keeper/BP_Gate.BP_Gate_C"))
    (:then (Variables|Default|SetGate g))
    (:CastFailed (Development|PrintString :InString "SETUP: BP_Gate not in level"))))
""",
    "FindGateLantern": """
(fn FindGateLantern ()
  ; "the lantern" = the gate lantern: the only BP_Lantern outside the fence (x < 1000).
  ; The path lanterns inside the ป่าช้า light themselves as he walks past (LightNearby).
  (for a (Actor|GetAllActorsOfClass :ActorClass "/Game/Keeper/BP_Lantern.BP_Lantern_C")
    (if (< (.x (Transformation|GetActorLocation :self a)) 1000.0)
      (bind l (Utilities|Casting|CastToBP_Lantern :Object a)
        (:then (Variables|Default|SetLantern l))
        (:CastFailed)))))
""",
    "HandleVoiceInput": """
(fn HandleVoiceInput ()
  ; the Python voice service writes what the player said into PendingInput
  (bind p (Variables|Default|GetPendingInput))
  (if (not (Utilities|String|IsEmpty p))
    (CallFunction|Ask :Text p)
    (Variables|Default|SetPendingInput "")))
""",
    "UpdateBubble": """
(fn UpdateBubble ()
  ; show each phrase when its voice starts; after 12 s of silence show the whole reply anyway
  (bind sl (Variables|Default|GetSpeakLine))
  (if (not (Utilities|String|IsEmpty sl))
    (CallFunction|ShowReply :Line sl)
    (Variables|Default|SetSpeakLine "")
    (Variables|Default|SetWaitSince (Utilities|Time|GetGameTimeinSeconds)))
  (if (and (Variables|Default|GetWaiting) (> (- (Utilities|Time|GetGameTimeinSeconds) (Variables|Default|GetWaitSince)) 12.0))
    (Variables|Default|SetWaiting false)
    (CallFunction|ShowReply :Line (Variables|Default|GetReplyText))))
""",
    "UpdateWalk": """
(fn UpdateWalk ()
  ; walk to the next waypoint; the gate opens when he reaches it; Arrive does the action at the end
  (if (Variables|Default|GetWalking)
    (bind loc (Transformation|GetActorLocation))
    (bind wp (CallFunction|GetWaypoint :I (Variables|Default|GetWpIndex)))
    (bind d (Math|Vector|MakeVector :X (- (.x wp) (.x loc)) :Y (- (.y wp) (.y loc)) :Z 0.0))
    (if (Class|BPLantern|GetIsLit :self (Variables|Default|GetLantern))
      (CallFunction|LightNearby))
    (if (< (Math|Vector|VectorLength d) (select (>= (Variables|Default|GetWpIndex) 3) 120.0 60.0))
      (Variables|Default|SetWpIndex (+ (Variables|Default|GetWpIndex) 1))
      (if (and (== (Variables|Default|GetWpIndex) 1) (not (Class|BPGate|GetIsOpen :self (Variables|Default|GetGate))))
        (Class|BPGate|OpenGate :self (Variables|Default|GetGate)))
      (if (> (Variables|Default|GetWpIndex) 3)
        (Variables|Default|SetWalking false)
        (CallFunction|Arrive))
      (else
        (Pawn|Input|AddMovementInput :WorldDirection (Math|Vector|Normalize d) :ScaleValue 1.0)))))
""",
    "UpdateMicBar": """
(fn UpdateMicBar ()
  ; mic level bar + status label in the chat window
  (bind cw (Variables|Default|GetChatW))
  (Utilities|IsValid cw
    (:"Is Valid"
      (Class|WBPChat|SetMic :self cw :Level (Variables|Default|GetMicLevel) :Label (CallFunction|MicLabel)))
    (:"Is Not Valid")))
""",
    "RememberConfirmQuestion": f"""
(fn RememberConfirmQuestion (R)
  ; if the keeper asked "จะให้ลุง...มั้ย", store which action waits for the player's yes
  (if (and (or ({C} :SearchIn R :Substring "จะให้ลุง") ({C} :SearchIn R :Substring "จะพา")) (or ({C} :SearchIn R :Substring "ไหม") (or ({C} :SearchIn R :Substring "มั้ย") ({C} :SearchIn R :Substring "มั๊ย"))))
    (if (or ({C} :SearchIn R :Substring "ตะเกียง") ({C} :SearchIn R :Substring "ไฟ"))
      (Variables|Default|SetPendingTool "light_lantern")
      (elif (and ({C} :SearchIn R :Substring "พา") (not (Utilities|String|IsEmpty (CallFunction|GhostIdFrom :S R))))
        (Variables|Default|SetPendingTool "guide_to_ghost")
        (Variables|Default|SetPendingArg R)
        (elif ({C} :SearchIn R :Substring "ประตู")
          (Variables|Default|SetPendingTool "open_gate"))))))
""",
    "FinishReply": """
(fn FinishReply ()
  ; reply complete: tell the voice service (ReplyId), show it, and remember a "จะให้ลุง...มั้ย" question
  (Variables|Default|SetBusy false)
  (bind r (Variables|Default|GetReplyText))
  (if (not (Utilities|String|IsEmpty r))
    (Variables|Default|SetReplyId (+ (Variables|Default|GetReplyId) 1))
    (if (Variables|Default|GetVoiceOn)
      (CallFunction|WaitVoice)
      (else
        (CallFunction|ShowReply :Line r)))
    (CallFunction|RememberConfirmQuestion :R r)))
""",
    "HoldToolCall": """
(fn HoldToolCall (Tool Args)
  ; the model asked to use a tool: do NOT act yet, wait for the player's yes
  (Variables|Default|SetReplyText "")
  (Variables|Default|SetPendingTool Tool)
  (Variables|Default|SetPendingArg Args)
  (NVIDIAACE|LLM|SubmitToolResult :self (Variables|Default|GetKeeperLLM) :ToolId ""
    :ResultContent "ยังไม่ได้ทำ ต้องให้หลานตอบตกลงก่อน ให้ถามหลานสั้นๆ ว่า จะให้ลุงทำเลยมั้ย"))
""",
    "FindGhostSpot": """
(fn FindGhostSpot ()
  ; TargetSpot = the BP_GhostSpot whose GhostId matches the requested ghost (ToolArgs)
  (Variables|Default|SetTargetSpot)
  (for a (Actor|GetAllActorsOfClass :ActorClass "/Game/Keeper/BP_GhostSpot.BP_GhostSpot_C")
    (bind s (Utilities|Casting|CastToBP_GhostSpot :Object a)
      (:then
        (if (Utilities|String|EqualExactly(String) (Variables|Default|GetToolArgs) (Class|BPGhostSpot|GetGhostId :self s))
          (Variables|Default|SetTargetSpot s)))
      (:CastFailed))))
""",
    # ---- easter egg ----
    "StartParty": """
(fn StartParty ()
  ; 10 s party: he spins and hops (UpdateParty), poles flash rainbow colours, WBP_Party shows the 2D cats,
  ; the 3D OIIA cat spins beside him and its song plays
  (Variables|Default|SetDancing true)
  (Variables|Default|SetPartyUntil (+ (Utilities|Time|GetGameTimeinSeconds) 10.0))
  (CallFunction|Speak :Line "เหอะๆ ปาร์ตี้ป่าช้าเหรอ ได้เลย ดูลุงเต้นนะ")
  (UserInterface|Viewport|AddtoViewport :self (UserInterface|CreateWidget :Class "/Game/UI/WBP_Party.WBP_Party_C" :OwningPlayer (Game|GetPlayerController :PlayerIndex 0)))
  ; cat on the ground 1.3 m to his right (actor location is the capsule centre, ~92 cm above the feet)
  ; set up at runtime: the keeper placed in the level does not pick up these components' Blueprint defaults
  (Transformation|SetAbsolute :self (Variables|Default|GetPartyCat) :bNewAbsoluteLocation true :bNewAbsoluteRotation true :bNewAbsoluteScale true)
  (Components|SkeletalMesh|SetSkeletalMeshAsset :self (Variables|Default|GetPartyCat) :NewMesh "/Game/Characters/oiiaioooooiai-cat/source/OiiaioooooiaiFin.OiiaioooooiaiFin")
  (Transformation|SetWorldScale3D :self (Variables|Default|GetPartyCat) :NewScale (Math|Vector|MakeVector :X 2.0 :Y 2.0 :Z 2.0))
  (Audio|Components|Audio|SetSound :self (Variables|Default|GetPartyMusic) :NewSound "/Game/Characters/oiiaioooooiai-cat/W_W_-_OIIA_OIIA__Spinning_Cat_.W_W_-_OIIA_OIIA__Spinning_Cat_")
  (bind here (Transformation|GetActorLocation))
  (bind side (Transformation|GetActorRightVector))
  (Transformation|SetWorldLocation :self (Variables|Default|GetPartyCat)
    :NewLocation (- (+ here (* side 130.0)) (Math|Vector|MakeVector :X 0.0 :Y 0.0 :Z 92.0)))
  (Rendering|SetVisibility :self (Variables|Default|GetPartyCat) :bNewVisibility true)
  (Components|Animation|PlayAnimation :self (Variables|Default|GetPartyCat) :NewAnimToPlay "/Game/Characters/oiiaioooooiai-cat/source/OiiaioooooiaiFin_Anim.OiiaioooooiaiFin_Anim" :bLooping true)
  (Audio|Components|Audio|Play :self (Variables|Default|GetPartyMusic) :StartTime 0.0))
""",
    "UpdateParty": """
(fn UpdateParty ()
  ; while dancing: spin, hop every 0.7 s, rainbow flicker on every light pole; afterwards back to the poles' colour (255,173,77),
  ; the cat hides and the song stops (FadeOut/AdjustVolume node ids are ambiguous in the DSL)
  (if (Variables|Default|GetDancing)
    (bind now (Utilities|Time|GetGameTimeinSeconds))
    (Transformation|AddActorWorldRotation :DeltaRotation (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw (* (Utilities|Time|GetWorldDeltaSeconds) 540.0)))
    (if (> now (Variables|Default|GetNextHop))
      (Character|Jump)
      (Variables|Default|SetNextHop (+ now 0.7)))
    (bind done (> now (Variables|Default|GetPartyUntil)))
    (for a (Actor|GetAllActorsOfClass :ActorClass "/Game/Keeper/BP_LightPole.BP_LightPole_C")
      (bind lp (Utilities|Casting|CastToBP_LightPole :Object a)
        (:then
          (Rendering|Components|Light|SetLightColor :self (Class|BPLightPole|GetLight :self lp)
            :NewLightColor (select done (Math|Color|HSVtoRGB :H 22.3 :S 0.926 :V 1.0 :A 1.0)
                                        (Math|Color|HSVtoRGB :H (Math|Random|RandomFloatinRange :Min 0.0 :Max 360.0) :S 1.0 :V 1.0 :A 1.0))))
        (:CastFailed)))
    (if done
      (Variables|Default|SetDancing false)
      (Rendering|SetVisibility :self (Variables|Default|GetPartyCat) :bNewVisibility false)
      (Audio|Components|Audio|Stop :self (Variables|Default|GetPartyMusic)))
    (else
      ; no party: keep the cat hidden (the placed keeper does not get the hidden default)
      (Rendering|SetVisibility :self (Variables|Default|GetPartyCat) :bNewVisibility false))))
""",
}
NEW_FUNCS = ["SetupScene", "SetupChat", "FindGate", "FindGateLantern", "HandleVoiceInput", "UpdateBubble", "UpdateWalk", "UpdateMicBar", "FinishReply",
             "RememberConfirmQuestion", "HoldToolCall", "FindGhostSpot", "StartParty", "UpdateParty"]
with open(__file__.replace("build_keeper_logic.py", "keeper_game.dsl"), encoding="utf-8") as f:
    FUNCS["EventGraph"] = f.read()

from bpkit import ensure_var  # noqa: E402
from categorize_keeper_vars import set_categories  # noqa: E402

set_categories(default=True)  # DSL names variables by category; restored at the end

ensure_var(P, "DoneNote", "string")
for _n, _t in [("Dancing", "bool"), ("PartyUntil", "float"), ("NextHop", "float")]:
    ensure_var(P, _n, _t)  # easter egg  # what Blueprint just did; told to the LLM with the player's next line
for _n, _t in [("Ctx", "string"), ("CurTool", "string"), ("Mode", "string"), ("GoalX", "float"), ("GoalY", "float"), ("ReturnY", "float")]:
    ensure_var(P, _n, _t)  # walk-to-interact: what he walks for and where
for _fn in ["StartWalk", "LightNearby", "CleanSpeech"] + NEW_FUNCS:
    try:
        call(BP, "get_graph", blueprint=ref(f"{P}.BP_Keeper"), graph_name=_fn)
    except RuntimeError:
        call(BP, "add_function_graph", blueprint=ref(f"{P}.BP_Keeper"), graph_name=_fn)
for _fn, _params in [("RememberConfirmQuestion", ["R"]), ("HoldToolCall", ["Tool", "Args"])]:
    _g = ref(f"{P}.BP_Keeper:{_fn}")
    _head = str(call(BP, "read_graph_dsl", graph=_g)).splitlines()[0]  # "(fn Name (A B)"
    for _p in _params:
        if _p not in _head.split("(")[-1]:
            call(BP, "add_function_param", graph=_g, param_name=_p, param_type="string", input_param=True)
for attempt in range(3):
    errors = []
    for gname, code in FUNCS.items():
        try:
            call(BP, "write_graph_dsl", graph=ref(f"{P}.BP_Keeper:{gname}"), code=code)
        except RuntimeError as e:
            if "failed to compile" not in str(e):
                raise RuntimeError(f"{gname}: {e}") from e
            errors.append(f"{gname}: {str(e)[:400]}")
    if not errors:
        break
    print(f"pass {attempt + 1} compile errors:", *errors, sep="\n  ")
from bpkit import prune_graph  # noqa: E402

for gname in FUNCS:  # write_graph_dsl leaves the old version behind as dead nodes: remove them
    print(gname, "pruned (total, dead):", prune_graph(ref(f"{P}.BP_Keeper:{gname}")))
set_categories()
print("saved:", compile_save(P))

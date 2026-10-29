; BP_Keeper event graph (game). Each event is short and calls one named function (see build_keeper_logic.py),
; so the graph reads like a table of contents. Text in: Ask(Text) <- typing (WBP_Chat) and PendingInput (Python
; voice). Text out: ReplyText (streamed) + ReplyId (bumped when complete). When the Python voice service runs it sets
; VoiceOn; the bubble/log then show "ลุงบุญกำลังคิด..." and the service writes each phrase to SpeakLine as it starts
; playing, so text and voice stay in sync. Confirmation is enforced in Blueprint, not trusted to the model.

(event EventBeginPlay
  (CallFunction|SetupScene))

(event EventTick (DeltaSeconds)
  (CallFunction|HandleVoiceInput)
  (CallFunction|UpdateBubble)
  (CallFunction|UpdateWalk)
  (CallFunction|UpdateMicBar)
  (CallFunction|UpdateParty))

(event OnLLMReady(KeeperLLM)
  (CallFunction|Speak :Line "มาๆ เข้ามาใกล้ๆ ไม่ต้องกลัว ลุงบุญเฝ้าป่าช้านี้มาสามสิบปีแล้ว หลานอยากฟังเรื่องผีมั้ยล่ะ หึๆ"))

(event OnTokenStreamed(KeeperLLM) (Token PartialText)
  (Variables|Default|SetReplyText (CallFunction|CleanSpeech :S PartialText))
  (if (not (Variables|Default|GetVoiceOn))
    (CallFunction|ShowSpeech :Line (Variables|Default|GetReplyText))))

(event OnResponseComplete(KeeperLLM) (FullResponse ResponseMessage)
  (CallFunction|FinishReply))

(event OnToolCalled(KeeperLLM) (ToolName ToolId ToolArguments)
  (CallFunction|HoldToolCall :Tool ToolName :Args ToolArguments))

(event OnLLMError(KeeperLLM) (ErrorMessage)
  (Variables|Default|SetBusy false)
  (Development|PrintString :InString (Utilities|String|Append "LLM ERROR: " ErrorMessage) :Duration 20.0)
  (CallFunction|ShowSpeech :Line "แหะ ลุงหูตึงไปหน่อย พูดใหม่อีกทีสิ"))

(event Custom|GuideToSpot
  (CallFunction|FindGhostSpot)
  (bind t (Variables|Default|GetTargetSpot))
  (Utilities|IsValid t
    (:"Is Valid"
      (CallFunction|StartWalk))
    (:"Is Not Valid"
      (CallFunction|Speak :Line "ผีตัวนี้ไม่มีที่ให้ไปดูในป่าช้านี้หรอก แต่ลุงเล่าให้ฟังได้นะ"))))

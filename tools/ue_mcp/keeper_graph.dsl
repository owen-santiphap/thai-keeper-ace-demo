; BP_KeeperTest event graph (tool test). Voice input replaces the SendMessage text later.

(event OnLLMReady(KeeperLLM)
  (Development|PrintString :InString "Keeper LLM ready - sending test message" :Duration 10.0)
  (NVIDIAACE|LLM|SendMessage :self (Variables|Default|GetKeeperLLM) :UserText "ช่วยจุดตะเกียงหน่อยครับ"))

; PartialText is the whole reply so far, decoded correctly (Full Response is garbled Thai - do not use it).
(event OnTokenStreamed(KeeperLLM) (Token PartialText)
  (Variables|Default|SetReplyText PartialText))

(event OnResponseComplete(KeeperLLM) (FullResponse ResponseMessage)
  (Development|PrintString :InString (Utilities|String|Append "ลุงบุญ: " (Variables|Default|GetReplyText)) :Duration 30.0))

(event OnToolCalled(KeeperLLM) (ToolName ToolId ToolArguments)
  (bind llm (Variables|Default|GetKeeperLLM))
  (Development|PrintString :InString (Utilities|String|Append (Utilities|String|Append "TOOL CALLED: " ToolName) (Utilities|String|Append " args=" ToolArguments)) :Duration 30.0)
  (if (Utilities|String|EqualExactly(String) ToolName "light_lantern")
    (Development|PrintString :InString "ACTION: lantern lit" :Duration 30.0)
    (NVIDIAACE|LLM|SubmitToolResult :self llm :ToolId "" :ResultContent "สำเร็จแล้ว จุดตะเกียงแล้ว")
    (elif (Utilities|String|EqualExactly(String) ToolName "open_gate")
      (Development|PrintString :InString "ACTION: gate opened" :Duration 30.0)
      (NVIDIAACE|LLM|SubmitToolResult :self llm :ToolId "" :ResultContent "สำเร็จแล้ว เปิดประตูแล้ว")
      (elif (Utilities|String|EqualExactly(String) ToolName "show_on_map")
        (Development|PrintString :InString (Utilities|String|Append "ACTION: show on map " ToolArguments) :Duration 30.0)
        (NVIDIAACE|LLM|SubmitToolResult :self llm :ToolId "" :ResultContent "สำเร็จแล้ว แสดงบนแผนที่แล้ว")
        (else
          (Development|PrintString :InString "ACTION: unknown tool" :Duration 30.0)
          (NVIDIAACE|LLM|SubmitToolResult :self llm :ToolId "" :ResultContent "ไม่รู้จักคำสั่งนี้"))))))

(event OnLLMError(KeeperLLM) (ErrorMessage)
  (Development|PrintString :InString (Utilities|String|Append "LLM ERROR: " ErrorMessage) :Duration 60.0))

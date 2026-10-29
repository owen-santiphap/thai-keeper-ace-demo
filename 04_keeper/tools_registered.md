# Registered Tools (Project Settings > Plugins > NVIDIA ACE LLM > Tools > Registered Tools)

Add three entries with the "+" button. Use these exact values. Tool names and arguments
are English on purpose: the ACE LLM plugin currently turns non-ASCII (Thai) text in tool
call arguments into garbage (see FString(...) at LLMToolCallList.cpp line 47), so the
model only ever passes ASCII ids.

Format follows the plugin README (Name / Description / Parameters Schema Json / Enabled).

## 1. light_lantern
- Enabled: true
- Description: Light the keeper's lantern so the cemetery path becomes visible. Call this when the visitor asks for light or asks to light the lantern. Takes no arguments.
- Parameters Schema Json:
```json
{
  "type": "object",
  "properties": {},
  "additionalProperties": false
}
```

## 2. open_gate
- Enabled: true
- Description: Open the cemetery gate. Call this only when the visitor asks to open the gate or go inside. Takes no arguments.
- Parameters Schema Json:
```json
{
  "type": "object",
  "properties": {},
  "additionalProperties": false
}
```

## 3. show_on_map
- Enabled: true
- Description: Show on the map where a ghost is said to appear. Call this when the visitor asks where a ghost is or wants to see it on the map. Use only the ghost_id values from the allowed list.
- Parameters Schema Json:
```json
{
  "type": "object",
  "properties": {
    "ghost_id": {
      "type": "string",
      "enum": ["krasue", "krahang", "pop", "tani", "phong", "kong_koi", "tai_hong", "pret"],
      "description": "Which ghost to show on the map. Must be exactly one of the allowed ids."
    }
  },
  "required": ["ghost_id"],
  "additionalProperties": false
}
```

## Notes (UNTESTED)
- Whether Typhoon2.5-Qwen3-4B emits tool calls through this plugin is not yet verified.
- If an empty "properties": {} schema is rejected for light_lantern / open_gate, give each a
  dummy optional string argument instead, e.g. "reason" (not required).
- Blueprint wiring: ACE LLM > On Tool Called (ToolName, ToolId, ToolArguments) > Branch on
  ToolName > do the action > ACE LLM > Submit Tool Result (ToolId empty, ResultContent e.g.
  "lantern is now lit"). Parse ToolArguments as JSON and treat it as untrusted input.

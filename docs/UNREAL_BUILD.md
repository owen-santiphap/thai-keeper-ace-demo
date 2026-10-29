# Building the keeper in Unreal (what the repo cannot ship as assets)

The original project used MetaHuman and third-party art, which cannot go in a public repo (`docs/LICENSES.md`), and the Blueprints
reference them. So you build the keeper yourself. This page describes the design that worked. Two routes:

- **By hand**: follow the design below in the Blueprint editor.
- **With Claude Code + Epic's UE 5.8 MCP**: the scripts in `tools/ue_mcp/` created the original graphs (`keeper_game.dsl`, `build_keeper_logic.py`,
  `wire_keys.py`, ...). They name our original assets (`/Game/Keeper/BP_Keeper`, `/Game/Maps/Cemetery`), so on a fresh project they are a
  **reference and starting point, not a one-click build**. They have **not** been run against a clean project. Epic's MCP server
  is loopback only (`http://127.0.0.1:8000/mcp`); enable the `ModelContextProtocol`, `EditorToolset`, `UMGToolSet` plugins.

## Minimum level

A flat ground, a fence with a gate, a lantern, four spots where ghosts "appear" (krasue, tani, kong_koi, pret), and the keeper (Manny mannequin).
Names we used: `BP_Keeper`, `BP_Gate`, `BP_Lantern`, `BP_GhostSpot`, `WBP_Chat`, `WBP_Bubble`.

## BP_Keeper (an AI-controlled Pawn with an ACE LLM component)

Component settings: System Prompt = `04_keeper/keeper_prompt_G_th.txt`, **Max Context Size 4096**, Auto Run Tools on.
Max Context Size is read once when the engine first loads: change it, then restart the editor.

Variables: `PendingInput` (string, written by the voice service), `ReplyText`, `ReplyId` (int, increments per reply), `Busy` (bool), `PendingTool`.

Flow (reconstructed from our development notes; compare with `tools/ue_mcp/keeper_game.dsl` for the exact graph):
1. **Tick**: if `PendingInput` is not empty, copy it, clear it, call **Ask**.
2. **Ask(text)**: if `PendingTool` is set and `IsYes(text)` is true, run the pending action (`DoPending`). If the text contains "ไม่", cancel it.
   Otherwise call ACE **Send Message** and set `Busy`.
3. **On Token Streamed**: append `Partial Text` to `ReplyText` and show it in the bubble and chat log.
4. **On Response Complete**: finish `ReplyText` (with the patched plugin Full Response is also valid Thai), increment `ReplyId`, clear `Busy`.
5. **On Tool Called** (`light_lantern`, `open_gate`, `guide_to_ghost(ghost_id)`): do **not** run it immediately. Store it in `PendingTool` and let the keeper's own question ("ให้ลุง...ไหม")
   be the confirmation; then call **Submit Tool Result** (Tool Id empty) so the model can continue (design suggestion, **untested** because Typhoon never called a tool directly).
6. **IsYes**: ครับ, ใช่, ได้, ตกลง, โอเค, ...เลย. Any text containing "ไม่" is a no.
7. **DoPending**: lantern lights, gate opens, or the keeper walks to the ghost spot (opens the gate first if needed) and the ghost placeholder appears.

Why confirmation lives in Blueprint: Typhoon asks the confirmation question reliably but did not call the tool after "yes" (`docs/ARCHITECTURE.md`).

## Walking

AddMovementInput along waypoints (gate, just inside, side corridor, ghost spot) in Tick. No navmesh.

## Keys

PlayerController key events did not fire in PIE for us, so `BP_Keeper.HandleKeys` polls `WasInputKeyJustPressed` / `IsInputKeyDown` on player controller 0 every Tick:
Enter = chat box, V (hold) = push-to-talk, M = mic mode (push-to-talk, always-on, off).

## UI

`WBP_Chat`: chat log, Thai text input (dark box, white text, Thai font asset), mic level bar, ghost counter "ผีที่พบ x/4". `WBP_Bubble`: speech bubble over the keeper's head,
shows "ลุงบุญกำลังคิด..." until the voice starts.

## Wire the voice service

The service reads and writes `PendingInput`, `ReplyText`, `ReplyId`, `Busy` on the placed `BP_Keeper` via Remote Control. The object path is set in
`tools/keeper_link.py` (`EDITOR_PATH`): change it to match your map and actor name, e.g. `/Game/Maps/<YourMap>.<YourMap>:PersistentLevel.BP_Keeper_C_0`.

## Check list

1. Typed question: กระสือคืออะไรครับ -> Thai answer from the lore.
2. Unknown ghost: แม่นากคือใคร -> "ไม่เคยได้ยิน" (not an invented story).
3. ช่วยจุดตะเกียงหน่อยครับ -> keeper asks to confirm; ได้ครับ -> lantern lights.
4. Voice: say the same lines with the voice service running.
5. `python tools/game_test.py` runs a typed conversation through Remote Control (needs your BP names).

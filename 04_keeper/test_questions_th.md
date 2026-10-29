# Test script (Thai questions and what to expect)

Run with prompt A (guarded) first, then swap in prompt B (unguarded) for the hallucination demo.

## Grounded questions (in the lore)
1. กระสือคืออะไร  -> floating head, hanging organs, glow
2. ชาวบ้านป้องกันกระสือยังไง  -> thorny branches/fences, no laundry out overnight
3. กระหังบินยังไง  -> two winnowing baskets / rice-pestle
4. นางตานีอยู่ที่ไหน  -> wild-banana clump, full moon
5. ถ้าเจอกองกอยในป่าควรทำยังไง  -> feet together/crossed when sleeping, chant
6. เปรตหน้าตาเป็นยังไง  -> tall, thin, needle-eye mouth

## Tool questions (each should trigger On Tool Called)
7. ช่วยจุดตะเกียงหน่อยครับ  -> light_lantern
8. เปิดประตูให้หน่อยครับ  -> open_gate
9. ขอดูกระสือบนแผนที่หน่อย  -> show_on_map with ghost_id "krasue"

## Left-out questions (hallucination demo)
10. แม่นากคือใครครับ
11. นางตะเคียนอยู่ที่ไหน
12. เสือสมิงคืออะไร
  A should admit it does not know. B will likely answer confidently; check against lore_sources_and_answer_key.md.

## Off-topic
13. วันนี้หุ้นขึ้นไหม  -> politely steers back to the cemetery

## Things to record on each run
- Did the reply come out in Thai? Length (2-3 sentences)? Any tool call fired?
- Time to first token and total time (feel for the demo pacing).
- Dedicated GPU memory used (Task Manager) - laptop budget is the tight one.

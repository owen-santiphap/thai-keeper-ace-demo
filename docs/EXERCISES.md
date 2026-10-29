# Exercises

1. **Run the test questions.** `04_keeper/test_questions_th.md` has 13 Thai questions with expected results. Run them typed, then spoken. Note ASR mistakes on ghost names.
2. **Hallucination demo.** Ask about ghosts that are not in the lore (แม่นาก, นางตะเคียน, เสือสมิง) with prompt G, then with prompt C (`keeper_prompt_C_storyteller_th.txt`, "never say you don't know").
   In our runs Typhoon stayed honest, while NVIDIA's bundled Qwen3.5 invented a story for แม่นาก (see `04_keeper/hallucination_results.jsonl`). Why does the same prompt behave differently?
3. **Add a ghost.** Add a lore entry to the prompt (use `04_keeper/lore_sources_and_answer_key.md` for how we checked facts), test that he tells it, and test that he still says "ไม่เคยได้ยิน" for one you left out.
4. **Change the keeper.** Edit the persona (`04_keeper/KEEPER_PERSONA.md`). Keep the answers to 1-2 short sentences: long answers make speech slow.
5. **Measure.** Record reply time and `nvidia-smi` VRAM in Play for Q4_K_M vs a smaller or larger model (`04_keeper/model_compare/`).
6. **Break it on purpose.** Remove the chat template step, or the confirmation rule. What fails and why?
7. **Discuss.** What should a game studio check before shipping an AI voice (licenses of the voice model, consent of voice actors, player data)?

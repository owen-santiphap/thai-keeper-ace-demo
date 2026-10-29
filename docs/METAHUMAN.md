# Your own MetaHuman keeper (optional)

The repo's keeper is the free Manny mannequin. If you want a face, make your own MetaHuman: Epic's content license
does not let us share ours (`docs/LICENSES.md`), and it is free to create one for yourself in Unreal 5.8.

1. Follow Epic's documentation for MetaHuman Creator in UE 5.8: https://dev.epicgames.com/documentation/en-us/metahuman/metahuman-creator
2. Design an older Thai man (ลุงบุญ is about 60, kind, playful). Keep texture and hair quality modest.
3. Put the MetaHuman Blueprint in your level, replace the mannequin mesh in `BP_Keeper`, and keep the same variables and graph.
4. Check VRAM with `nvidia-smi` in Play. On our 8 GB laptop MetaHuman on vs off made no measurable difference (7,424 vs 7,409 MiB peak), but the
   textures and grooms add disk and load time.

Do not commit the MetaHuman folder to a public repo.

## Keeper voice

The keeper speaks with the sample voice that ships with ThonburianTTS. For your own voice record 5-10 seconds of one person speaking clearly
(with their consent) and its exact transcript, then:

    run_voice.bat --ref-voice path\to\voice.wav --ref-text "<transcript>"

"""Play the e2e test pieces exactly like voice_service.play_loop (piece, 0.45 s silent tail, next piece), with a 2 s gap
between replies; used with a loopback recorder to check that endings are not clipped."""
import time
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf

D = Path(__file__).resolve().parent / "out" / "e2e"
time.sleep(1.5)
for i in range(3):
    for j in range(2):
        a, sr = sf.read(str(D / f"play_{i}_{j}.wav"), dtype="float32")
        a = a if a.ndim == 1 else a.mean(axis=1)
        a = np.concatenate([np.zeros(int(sr * 0.25), dtype=a.dtype), a, np.zeros(int(sr * 0.45), dtype=a.dtype)])
        sd.play(a, sr)
        sd.wait()
    time.sleep(2.0)
print("played")

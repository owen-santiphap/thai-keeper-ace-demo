@echo off
rem Keeper voice: mic -> Typhoon Whisper (ASR) -> keeper, keeper reply -> ThonburianTTS -> speakers.
rem Start this, then press Play in Unreal (order does not matter). Close the window to stop.
rem Options: run_voice.bat --nfe 32        (better TTS quality, slower)
rem          run_voice.bat --asr-engine hf (fp16 transformers ASR instead of int8)
cd /d "%~dp0"
".venv-voice\Scripts\python.exe" -u 05_voice_tests\voice_service.py %*
pause

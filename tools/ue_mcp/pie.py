"""Start or stop Play-In-Editor: python pie.py start|stop"""
import sys

from ue import call

APP = "EditorToolset.EditorAppToolset"

if sys.argv[1] == "start":
    if not call(APP, "IsPIERunning"):
        call(APP, "StartPIE", options={"bSimulate": False, "playMode": "PlayMode_InViewPort"})
else:
    call(APP, "StopPIE")
print("PIE running:", call(APP, "IsPIERunning"))

"""Run editor Python through the project's KeeperPyTools MCP toolset.  python pyrun.py file.py | -c "code" """
import sys

from ue import call

code = sys.argv[2] if sys.argv[1] == "-c" else open(sys.argv[1], encoding="utf-8").read()
print(call("init_unreal.KeeperPyTools", "run_python", code=code))

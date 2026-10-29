"""Search node type ids in BP_KeeperTest's event graph. Usage: python find_nodes.py term1 term2 ..."""
import sys

from ue import BP, call, ref

g = ref("/Game/Keeper/BP_Keeper.BP_Keeper:EventGraph")
for term in sys.argv[1:]:
    res = call(BP, "find_node_types", graph=g, type_id_filter=term, context_pins=[])
    print(f"== {term}: {res[:15] if isinstance(res, list) else res}")

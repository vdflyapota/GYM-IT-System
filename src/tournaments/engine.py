from collections import defaultdict
from typing import List, Dict, Any

def compute_leaderboard(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    totals = defaultdict(int)
    names = {}
    for r in results:
        mid = r.get("member_id")
        if mid is None:
            continue
        pts = int(r.get("points", 0))
        totals[mid] += pts
        name = r.get("member_name") or r.get("name")
        if name:
            names[mid] = name
    board = [{"member_id": mid, "name": names.get(mid, str(mid)), "points": pts} for mid, pts in totals.items()]
    board.sort(key=lambda x: (-x["points"], x["name"]))
    return board

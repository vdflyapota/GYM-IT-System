from collections import defaultdict
from typing import List, Dict, Any
import math


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


def generate_single_elimination_bracket(participants: List[Any]) -> List[Dict[str, Any]]:
    """
    Generate a single elimination bracket for the given participants.
    Returns a list of bracket matches organized by rounds.

    Args:
        participants: List of Participant objects

    Returns:
        List of dictionaries representing bracket matches
    """
    if not participants:
        return []

    # Sort participants by seed (if available)
    sorted_participants = sorted(participants, key=lambda p: p.seed if p.seed else 999)

    # Calculate number of rounds needed
    num_participants = len(sorted_participants)
    num_rounds = math.ceil(math.log2(num_participants)) if num_participants > 1 else 1

    # Calculate total slots needed (next power of 2)
    total_slots = 2**num_rounds

    # Pad with None for byes
    padded_participants = sorted_participants + [None] * (total_slots - num_participants)

    # Generate first round matches
    brackets = []
    match_number = 1

    for i in range(0, len(padded_participants), 2):
        p1 = padded_participants[i]
        p2 = padded_participants[i + 1] if i + 1 < len(padded_participants) else None

        bracket_match = {
            "round": 1,
            "match_number": match_number,
            "participant1_id": p1.id if p1 else None,
            "participant2_id": p2.id if p2 else None,
            "winner_id": None,
            "score": None,
        }
        brackets.append(bracket_match)
        match_number += 1

    # Generate subsequent rounds (empty matches to be filled as tournament progresses)
    current_round = 2
    matches_in_previous_round = len(brackets)

    while current_round <= num_rounds:
        matches_in_this_round = matches_in_previous_round // 2
        for i in range(matches_in_this_round):
            bracket_match = {
                "round": current_round,
                "match_number": i + 1,
                "participant1_id": None,
                "participant2_id": None,
                "winner_id": None,
                "score": None,
            }
            brackets.append(bracket_match)
        matches_in_previous_round = matches_in_this_round
        current_round += 1

    return brackets


def generate_double_elimination_bracket(participants: List[Any]) -> List[Dict[str, Any]]:
    """
    Generate a double elimination bracket (placeholder for future implementation).
    For now, returns single elimination.

    Args:
        participants: List of Participant objects

    Returns:
        List of dictionaries representing bracket matches
    """
    # TODO: Implement proper double elimination logic
    # For now, just use single elimination
    return generate_single_elimination_bracket(participants)

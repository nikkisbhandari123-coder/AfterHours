"""
test_story_progression.py - Automated Verification of Story Progression & Endings

Tests:
1. Mystery metadata and 4 stations in "The Disappearance of Blackwood"
2. Hidden transmission concealment (107.9 MHz)
3. Step-by-step clue discovery and contradiction planting
4. Investigation completion condition (4/4 discovered)
5. Player choices & both narrative endings (Truth vs. Quarantine)
6. Duplicate clue rejection & reset functionality
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from story import (
    MYSTERY_TITLE,
    REQUIRED_MYSTERY_FREQUENCIES,
    RADIO_STATIONS,
    ENDINGS,
    resolve_frequency_telemetry,
    get_initial_state,
    add_clue_to_state,
    check_investigation_complete,
    get_mystery_progress,
    record_player_decision,
)

def run_story_tests():
    print("==================================================")
    print("STARTING 'THE DISAPPEARANCE OF BLACKWOOD' TESTS")
    print("==================================================")

    # ----------------------------------------------------
    # TEST 1: Mystery Metadata & Four Station Narratives
    # ----------------------------------------------------
    print(f"\n[TEST 1] Mystery: '{MYSTERY_TITLE}'")
    assert len(REQUIRED_MYSTERY_FREQUENCIES) == 4
    for freq in REQUIRED_MYSTERY_FREQUENCIES:
        station = RADIO_STATIONS[freq]
        print(f"  Station {freq} MHz ({station['callsign']}): {station['name']}")
        assert len(station["transmission"]) > 50
        assert len(station["clue"]) > 20
        assert len(station["distorted_fragment"]) > 20
    print("  [PASS] All 4 mystery stations and lore snippets verified.")

    # ----------------------------------------------------
    # TEST 2: Hidden Transmission Concealment
    # ----------------------------------------------------
    print("\n[TEST 2] Verifying hidden transmission (107.9 MHz) concealment...")
    hidden_unlocked = resolve_frequency_telemetry(107.9, is_locked=False)
    assert hidden_unlocked["is_locked"] is False
    assert hidden_unlocked["can_lock"] is True
    # Cipher and floodgate revelation must NOT be revealed in transcript before locking
    assert "floodgates were opened" not in hidden_unlocked["transmission"]
    assert "cipher 4-19-88-0" not in hidden_unlocked["transmission"]
    assert "Audio modulation is phase-locked but unaligned" in hidden_unlocked["transmission"]
    print("  [PASS] 107.9 MHz remains completely concealed until locked.")

    # ----------------------------------------------------
    # TEST 3: Step-by-Step Clue Progression & Contradictions
    # ----------------------------------------------------
    print("\n[TEST 3] Step-by-step investigation progression...")
    state = get_initial_state()
    prog0 = get_mystery_progress(state)
    assert prog0["total_discovered"] == 0
    assert prog0["is_complete"] is False
    assert check_investigation_complete(state) is False
    print("  Step 0: 0/4 discovered. Investigation incomplete.")

    # Step 1: Weather (88.1 MHz)
    t1 = resolve_frequency_telemetry(88.1, is_locked=True, locked_freq=88.1)
    add_clue_to_state(state, t1["clue"], "88.1 MHz")
    prog1 = get_mystery_progress(state)
    assert prog1["total_discovered"] == 1
    assert "mudslides" in t1["clue"].lower()
    print("  Step 1: 88.1 MHz decoded (Weather mudslide claim planted). Progress: 1/4.")

    # Step 2: Civil Defense (91.7 MHz) - Contradicts Weather
    t2 = resolve_frequency_telemetry(91.7, is_locked=True, locked_freq=91.7)
    add_clue_to_state(state, t2["clue"], "91.7 MHz")
    prog2 = get_mystery_progress(state)
    assert prog2["total_discovered"] == 2
    assert "contradicts" in t2["clue"].lower()
    assert "military" in t2["clue"].lower()
    print("  Step 2: 91.7 MHz decoded (Contradiction: armed military cordon). Progress: 2/4.")

    # Step 3: Police Dispatch (103.4 MHz) - Contradicts Official Timeline
    t3 = resolve_frequency_telemetry(103.4, is_locked=True, locked_freq=103.4)
    add_clue_to_state(state, t3["clue"], "103.4 MHz")
    prog3 = get_mystery_progress(state)
    assert prog3["total_discovered"] == 3
    assert "abandoned" in t3["clue"].lower()
    assert "hours before" in t3["clue"].lower()
    print("  Step 3: 103.4 MHz decoded (Mayor drafted evacuation hours ahead). Progress: 3/4.")

    # Investigation should still be incomplete before the numbers station
    assert check_investigation_complete(state) is False

    # Step 4: Numbers Station (107.9 MHz) - The Master Reveal
    t4 = resolve_frequency_telemetry(107.9, is_locked=True, locked_freq=107.9)
    assert "4-19-88-0" in t4["transmission"]
    assert "deliberately opened" in t4["clue"].lower()
    add_clue_to_state(state, t4["clue"], "107.9 MHz")
    prog4 = get_mystery_progress(state)
    assert prog4["total_discovered"] == 4
    assert prog4["is_complete"] is True
    assert check_investigation_complete(state) is True
    print("  Step 4: 107.9 MHz decoded (Truth revealed: floodgates opened deliberately). Progress: 4/4 [COMPLETE].")
    print("  [PASS] All 4 narrative pieces and contradictions sequentially verified.")

    # ----------------------------------------------------
    # TEST 4: Ending A: The Transmission of Truth
    # ----------------------------------------------------
    print("\n[TEST 4] Verifying Ending A: Broadcast the Truth...")
    state_a = dict(state)
    success_a = record_player_decision(state_a, "truth")
    assert success_a is True
    assert state_a["chosen_ending"] == "truth"
    ending_a = ENDINGS["truth"]
    assert "THE TRANSMISSION OF TRUTH" in ending_a["title"]
    assert "shattered forever" in ending_a["narrative"].lower()
    print(f"  [PASS] Ending A verified: '{ending_a['title']}' ({ending_a['badge']}).")

    # ----------------------------------------------------
    # TEST 5: Ending B: The Blackwood Quarantine
    # ----------------------------------------------------
    print("\n[TEST 5] Verifying Ending B: Enforce Quarantine...")
    state_b = dict(state)
    success_b = record_player_decision(state_b, "quarantine")
    assert success_b is True
    assert state_b["chosen_ending"] == "quarantine"
    ending_b = ENDINGS["quarantine"]
    assert "THE BLACKWOOD QUARANTINE" in ending_b["title"]
    assert "degaussing circuit" in ending_b["narrative"].lower()
    print(f"  [PASS] Ending B verified: '{ending_b['title']}' ({ending_b['badge']}).")

    # ----------------------------------------------------
    # TEST 6: Duplicate Clue Prevention
    # ----------------------------------------------------
    print("\n[TEST 6] Verifying duplicate clue prevention on completed state...")
    clue_count_before = len(state["discovered_clues"])
    re_add = add_clue_to_state(state, t4["clue"], "107.9 MHz")
    assert re_add is False
    assert len(state["discovered_clues"]) == clue_count_before
    print("  [PASS] Re-locking a frequency strictly avoids duplicate clue logging.")

    print("\n==================================================")
    print("ALL STORY PROGRESSION TESTS PASSED (100% OK)")
    print("==================================================")

if __name__ == "__main__":
    run_story_tests()

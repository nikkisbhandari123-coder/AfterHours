"""
test_gameplay.py - Automated Verification of AfterHours Mechanics

Tests:
1. All 4 known stations (88.1, 91.7, 103.4, 107.9 MHz)
2. Unknown / dead air frequencies
3. Proximity-based signal strength ramp
4. Frequency locking rules & hidden transmission concealment
5. Duplicate clue prevention
"""

import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from story import (
    RADIO_STATIONS,
    KNOWN_FREQUENCIES,
    resolve_frequency_telemetry,
    get_initial_state,
    add_clue_to_state,
)

def run_tests():
    print("========================================")
    print("STARTING AFTERHOURS GAMEPLAY TEST SUITE")
    print("========================================")

    # ----------------------------------------------------
    # TEST 1: All Four Known Stations (Unlocked & Locked)
    # ----------------------------------------------------
    print("\n[TEST 1] Verifying all four known stations...")
    expected_stations = [88.1, 91.7, 103.4, 107.9]
    for freq in expected_stations:
        assert freq in RADIO_STATIONS, f"Missing frequency {freq} in RADIO_STATIONS!"
        
        # When dial is on frequency before locking
        unlocked = resolve_frequency_telemetry(freq, is_locked=False)
        assert unlocked["can_lock"] is True, f"Should be lockable at {freq} MHz"
        assert unlocked["signal_percent"] >= 80, f"Signal at {freq} should be strong peak"
        # Concealment: Should NOT reveal full transmission before locking!
        assert "Audio modulation is phase-locked" in unlocked["transmission"] or "STABLE CARRIER" in unlocked["transmission"], (
            f"Prematurely revealed transmission at {freq} before locking!"
        )

        # When locked
        locked = resolve_frequency_telemetry(freq, is_locked=True, locked_freq=freq)
        assert locked["is_locked"] is True
        assert locked["clue"] == RADIO_STATIONS[freq]["clue"]
        assert locked["transmission"] == RADIO_STATIONS[freq]["transmission"]
        print(f"  [PASS] {freq} MHz: {locked['callsign']} verified (Unlocked & Locked).")

    # ----------------------------------------------------
    # TEST 2: Unknown / Dead Air Frequencies
    # ----------------------------------------------------
    print("\n[TEST 2] Verifying unknown dead air frequencies...")
    unknown_frequencies = [80.0, 84.5, 95.0, 100.0, 110.0]
    for freq in unknown_frequencies:
        t = resolve_frequency_telemetry(freq)
        assert t["can_lock"] is False, f"Unknown frequency {freq} should NOT be lockable!"
        assert t["signal_percent"] <= 20, f"Signal at {freq} should be low noise"
        assert t["clue"] is None, f"No clues should be unlocked on dead air {freq}"
        assert t["status"] == "DEAD AIR"
        print(f"  [PASS] {freq} MHz: Correctly categorized as {t['status']} (Signal: {t['signal_percent']}%)")

    # ----------------------------------------------------
    # TEST 3: Signal Strength Ramp (Approaching 88.1 MHz)
    # ----------------------------------------------------
    print("\n[TEST 3] Verifying proximity-based signal strength ramp...")
    test_ramp = [86.5, 87.3, 87.7, 88.0, 88.1]
    strengths = []
    for f in test_ramp:
        t = resolve_frequency_telemetry(f)
        strengths.append((f, t["signal_percent"], t["status"]))
        print(f"  Freq: {f:.1f} MHz -> Strength: {t['signal_percent']}% | Status: {t['status']}")
    
    # Assert monotonic increase as we approach 88.1 MHz
    for i in range(len(strengths) - 1):
        assert strengths[i][1] <= strengths[i+1][1], (
            f"Signal strength should increase approaching carrier: {strengths[i]} vs {strengths[i+1]}"
        )
    print("  [PASS] Signal strength smoothly ramps up as carrier is approached.")

    # ----------------------------------------------------
    # TEST 4: Fringe Spillover / Bleed-over Distortions
    # ----------------------------------------------------
    print("\n[TEST 4] Verifying fringe distorted transmission fragments...")
    fringe_freq = 88.3  # 0.2 MHz away from 88.1 MHz
    fringe_telemetry = resolve_frequency_telemetry(fringe_freq)
    assert fringe_telemetry["status"] == "SIGNAL BLEED"
    assert fringe_telemetry["can_lock"] is False
    assert "CARRIER BLEED" in fringe_telemetry["transmission"]
    print(f"  [PASS] Fringe at {fringe_freq} MHz produces distorted fragment: {fringe_telemetry['transmission'][:60]}...")

    # ----------------------------------------------------
    # TEST 5: Frequency Locking & Clue Awarding
    # ----------------------------------------------------
    print("\n[TEST 5] Verifying frequency locking & duplicate clue prevention...")
    state = get_initial_state()
    initial_clue_count = len(state["discovered_clues"])
    print(f"  Initial clues in notebook: {initial_clue_count}")

    # Discover station 88.1
    t88 = resolve_frequency_telemetry(88.1, is_locked=True, locked_freq=88.1)
    added = add_clue_to_state(state, t88["clue"], "88.1 MHz")
    assert added is True, "First discovery of 88.1 clue should succeed"
    assert len(state["discovered_clues"]) == initial_clue_count + 1
    print(f"  [PASS] Discovered 88.1 clue. Total clues: {len(state['discovered_clues'])}")

    # Attempt to add the exact same clue again
    added_duplicate = add_clue_to_state(state, t88["clue"], "88.1 MHz")
    assert added_duplicate is False, "Duplicate clue must be rejected!"
    assert len(state["discovered_clues"]) == initial_clue_count + 1
    print("  [PASS] Duplicate clue rejected. Total clues remain constant.")

    # Discover remaining stations
    for f in [91.7, 103.4, 107.9]:
        tf = resolve_frequency_telemetry(f, is_locked=True, locked_freq=f)
        add_clue_to_state(state, tf["clue"], f"{f:.1f} MHz")
    
    assert len(state["discovered_clues"]) == initial_clue_count + 4
    print(f"  [PASS] All 4 station clues successfully discovered! Total clues: {len(state['discovered_clues'])}")

    print("\n========================================")
    print("ALL TESTS PASSED SUCCESSFULLY! (100% OK)")
    print("========================================")

if __name__ == "__main__":
    run_tests()

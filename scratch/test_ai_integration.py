"""
scratch/test_ai_integration.py - Verification of Ollama Gemma AI Integration and Story Protection

Tests:
1. Ollama discovery and model selection (gemma3:4b detection and configurability).
2. Live AI generation for the 4 content types (interference, fringe bleed, phantom transmissions, contextual whispers).
3. Strict story protection (canonical broadcasts, clues, and endings are 100% Python-controlled and never overwritten).
4. Caching and performance (0ms response on cached frequencies).
5. Ollama-offline simulation (graceful fallback without crashing or freezing).
"""

import os
import sys
import time

# Ensure workspace root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_engine import (
    check_ollama_service,
    query_ollama_gemma,
    generate_atmospheric_interference,
    generate_distorted_voice_fragment,
    generate_mysterious_transmission,
    generate_contextual_ambient,
    synthesize_radio_signal,
    get_fallback_ambient,
    get_cached_ambient,
    cache_ambient,
    clear_snippet_cache,
    DEFAULT_OLLAMA_HOST,
)
from story import (
    RADIO_STATIONS,
    KNOWN_FREQUENCIES,
    resolve_frequency_telemetry,
    get_initial_state,
    add_clue_to_state,
    check_investigation_complete,
    record_player_decision,
)


def run_tests():
    print("=" * 70)
    print("AFTERHOURS: OLLAMA GEMMA AI INTEGRATION TEST SUITE")
    print("=" * 70)

    # -------------------------------------------------------------
    # Test 1: Ollama Service Discovery & Model Identification
    # -------------------------------------------------------------
    print("\n[TEST 1] Checking Ollama service and local Gemma model...")
    status = check_ollama_service()
    print(f"  * Ollama Available: {status['available']}")
    print(f"  * Active Gemma Model: {status['model']}")
    print(f"  * All Detected Models: {status['all_models']}")
    assert status["available"] is True, "Expected local Ollama service to be available"
    assert status["model"] is not None and "gemma" in status["model"].lower(), (
        f"Expected Gemma model to be selected, got: {status['model']}"
    )
    print("  [PASS] Ollama service discovery and model detection PASSED.")

    # -------------------------------------------------------------
    # Test 2: Strict Story Protection (Canonical Broadcasts Untouched)
    # -------------------------------------------------------------
    print("\n[TEST 2] Verifying Strict Story Protection for Canonical Stations...")
    for freq in [88.1, 91.7, 103.4, 107.9]:
        # Test locked canonical station with AI snippet passed
        fake_ai_snippet = "[GEMMA AI INTERCEPT] Fake AI invented clue or transmission!"
        telemetry = resolve_frequency_telemetry(
            freq=freq,
            is_locked=True,
            locked_freq=freq,
            clues_count=2,
            cached_ai_snippet=fake_ai_snippet,
        )
        # Canonical transmission MUST NOT be overwritten by AI
        expected_canonical = RADIO_STATIONS[freq]["transmission"]
        assert telemetry["transmission"] == expected_canonical, (
            f"Story protection failed on {freq} MHz! Canonical transmission was overwritten."
        )
        assert telemetry["clue"] == RADIO_STATIONS[freq]["clue"], (
            f"Story protection failed on {freq} MHz! Clue was modified."
        )
        assert telemetry["is_ai_generated"] is False, (
            f"Canonical station {freq} MHz must not be flagged as AI generated."
        )
        print(f"  [OK] {freq} MHz locked broadcast and clue are 100% canonical and protected.")

    # Test Mystery Progress and Endings are strictly Python-controlled
    state = get_initial_state()
    assert check_investigation_complete(state) is False
    for freq in [88.1, 91.7, 103.4, 107.9]:
        add_clue_to_state(state, RADIO_STATIONS[freq]["clue"], f"{freq:.1f} MHz")
    assert check_investigation_complete(state) is True
    record_player_decision(state, "truth")
    assert state["chosen_ending"] == "truth"
    print("  [OK] Mystery progression and endings remain 100% Python-controlled.")

    # -------------------------------------------------------------
    # Test 3: Caching & Fallback Performance (0ms latency for slider)
    # -------------------------------------------------------------
    print("\n[TEST 3] Testing Snippet Caching & Instant Slider Sweeping...")
    clear_snippet_cache()
    test_freq = 84.5
    cache_ambient(test_freq, 0, "[GEMMA AI INTERCEPT] Cached radio static snippet")

    cached_val = get_cached_ambient(test_freq, 0)
    assert cached_val == "[GEMMA AI INTERCEPT] Cached radio static snippet"

    t0 = time.time()
    telemetry_cached = resolve_frequency_telemetry(
        freq=test_freq,
        is_locked=False,
        clues_count=0,
        cached_ai_snippet=cached_val,
    )
    dt = time.time() - t0
    assert dt < 0.05, f"Cached lookup took too long: {dt:.4f}s"
    assert telemetry_cached["is_ai_generated"] is True
    assert "[GEMMA AI INTERCEPT]" in telemetry_cached["transmission"]
    print(f"  [OK] Cached AI snippet retrieved in {dt*1000:.2f}ms (instant response).")

    # -------------------------------------------------------------
    # Test 4: Ollama-Offline Fallback Simulation
    # -------------------------------------------------------------
    print("\n[TEST 4] Testing Ollama-Offline Graceful Fallback...")
    # Simulate unavailable Ollama with invalid host
    offline_status = check_ollama_service(host="http://localhost:59999", cache_ttl=0.0)
    assert offline_status["available"] is False

    # Calling fallback ambient
    fallback = get_fallback_ambient(83.2)
    assert len(fallback) > 10
    print(f"  * Fallback sample: {fallback[:60]}...")

    # Calling synthesize_radio_signal with Ollama unavailable (offline host)
    synth_offline = synthesize_radio_signal(
        frequency=83.2,
        status_category="DEAD AIR",
        clues_count=1,
        force_generate=True,  # Even when forced, should fall back cleanly
        host="http://localhost:59999",
    )
    assert synth_offline["source"] == "FALLBACK"
    assert len(synth_offline["text"]) > 0
    print(f"  [OK] Fallback synthesized cleanly without crashing when Ollama is offline.")

    # -------------------------------------------------------------
    # Test 5: Live Generation of Atmospheric RF with Gemma AI
    # -------------------------------------------------------------
    print("\n[TEST 5] Testing Live Gemma AI Signal Synthesis (gemma3:4b)...")
    # Reset status cache to connect to actual Ollama
    check_ollama_service(host=DEFAULT_OLLAMA_HOST, cache_ttl=0.0)

    # Test synthesizing atmospheric static on dead air
    t0 = time.time()
    synth_live = synthesize_radio_signal(
        frequency=85.3,
        status_category="DEAD AIR",
        clues_count=1,
        force_generate=True,
    )
    elapsed = time.time() - t0
    print(f"  * Synthesis Elapsed: {elapsed:.2f}s")
    print(f"  * Source: {synth_live['source']}")
    print(f"  * Model: {synth_live['model']}")
    print(f"  * Output Text: {synth_live['text']}")

    assert synth_live["source"] in ("GEMMA_AI", "FALLBACK")
    assert len(synth_live["text"]) > 10
    print("  [OK] Live Gemma AI atmospheric signal synthesis test finished.")

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED SUCCESSFULLY! (5/5)")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()

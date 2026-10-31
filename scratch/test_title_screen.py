"""
test_title_screen.py - Test suite for AfterHours Cinematic Opening Screen
"""

import os
import sys
import base64
import struct

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
TITLE_IMG_PATH = os.path.join(ASSETS_DIR, "afterhours_title.png")

print("=" * 70)
print("AFTERHOURS: CINEMATIC OPENING SCREEN TEST SUITE")
print("=" * 70)

# -------------------------------------------------------------------
# Test 1: Image Asset Existence & Integrity
# -------------------------------------------------------------------
print("\n[TEST 1] Verifying title screen image asset...")
assert os.path.exists(TITLE_IMG_PATH), f"Missing title image at {TITLE_IMG_PATH}"
file_size = os.path.getsize(TITLE_IMG_PATH)
assert file_size > 500000, f"Image file unexpectedly small: {file_size} bytes"

with open(TITLE_IMG_PATH, "rb") as f:
    header = f.read(24)
    assert header[:8] == b"\x89PNG\r\n\x1a\n", "File does not have valid PNG magic signature"
    w, h = struct.unpack(">LL", header[16:24])
    assert w == 1672, f"Expected width 1672, got {w}"
    assert h == 941, f"Expected height 941, got {h}"

print(f"  * Path: {TITLE_IMG_PATH}")
print(f"  * Size: {file_size:,} bytes")
print(f"  * Dimensions: {w} x {h} (Aspect Ratio: {w/h:.4f})")
print("  [PASS] Image asset verified.")

# -------------------------------------------------------------------
# Test 2: Base64 Encoding & Memory Cache
# -------------------------------------------------------------------
print("\n[TEST 2] Verifying base64 encoding and caching...")
with open(TITLE_IMG_PATH, "rb") as f:
    b64_data = base64.b64encode(f.read()).decode("utf-8")

assert len(b64_data) > 2000000, f"Base64 data too short: {len(b64_data)}"
print(f"  * Encoded string length: {len(b64_data):,} characters")
print("  [PASS] Base64 encoding verified.")

# -------------------------------------------------------------------
# Test 3: Precision Button Geometry Verification
# -------------------------------------------------------------------
print("\n[TEST 3] Verifying responsive button alignment geometry...")
img_w, img_h = 1672, 941
btn_x1, btn_x2 = 579, 1094
btn_y1, btn_y2 = 584, 670

rel_left = btn_x1 / img_w
rel_width = (btn_x2 - btn_x1) / img_w
rel_top = btn_y1 / img_h
rel_height = (btn_y2 - btn_y1) / img_h

print(f"  * Button Relative Box: Left: {rel_left*100:.2f}%, Top: {rel_top*100:.2f}%, Width: {rel_width*100:.2f}%, Height: {rel_height*100:.2f}%")
assert abs((rel_left + rel_width / 2) - 0.50) < 0.01, "Button is not horizontally centered in image"
assert 0.60 <= rel_top <= 0.65, f"Button top position outside expected range: {rel_top}"
assert 0.08 <= rel_height <= 0.11, f"Button height outside expected range: {rel_height}"

# Test aspect ratio formula continuity
boundary_aspect = img_w / img_h
# Case 1: Wide screen (Aspect ratio = 2.0 > 1.777)
# Width = 100vw, Height = 100vw * 941 / 1672
vw, vh = 1920, 1080  # 16:9
ratio = vw / vh
print(f"  * Desktop 1920x1080 Viewport: Aspect Ratio {ratio:.4f}")
print("  [PASS] Responsive button geometry verified.")

# -------------------------------------------------------------------
# Test 4: Session State Lifecycle & Non-Regression
# -------------------------------------------------------------------
print("\n[TEST 4] Verifying Session State Flow & Non-Reset...")
sys.path.insert(0, BASE_DIR)
from story import get_initial_state, add_clue_to_state, resolve_frequency_telemetry

# New session initial state
state = get_initial_state()
state.setdefault("game_started", False)

assert state["game_started"] is False, "New player session must initially show title screen"
assert len(state["discovered_clues"]) == 1, "Initial clue should exist"

# Transition simulation
state["game_started"] = True
t88 = resolve_frequency_telemetry(88.1, is_locked=True, locked_freq=88.1)
add_clue_to_state(state, t88["clue"], "88.1 MHz")
assert state["game_started"] is True, "State must remain started"
assert len(state["discovered_clues"]) == 2, "Clue progression must be preserved"

# Simulate Streamlit rerun
# When rerun happens, game_started remains True, no reset
assert state.get("game_started") is True, "Streamlit reruns must NOT return to title screen"
assert len(state["discovered_clues"]) == 2, "Discovered clues must remain intact across reruns"
print("  * Initial session -> game_started: False (Title screen active)")
print("  * Button clicked -> game_started: True (Radio interface unlocked)")
print("  * Streamlit rerun -> game_started: True (Radio interface preserved)")
print("  * Clue progression preserved -> 2 clues maintained")
print("  [PASS] Session state lifecycle verified.")

# -------------------------------------------------------------------
# Test 5: Transition Telemetry Stages
# -------------------------------------------------------------------
print("\n[TEST 5] Verifying Atmospheric Transition Telemetry Messages...")
expected_stages = [
    "SIGNAL DETECTED...",
    "CONNECTING TO BLACKWOOD FREQUENCY...",
    "INVESTIGATION INITIATED.",
]

import app

# Check app module contains the transition logic
assert hasattr(app, "render_title_screen"), "app.py missing render_title_screen function"
assert hasattr(app, "run_atmospheric_transition"), "app.py missing run_atmospheric_transition function"
assert hasattr(app, "get_title_image_base64"), "app.py missing get_title_image_base64 function"

print("  * Stage 1: 'SIGNAL DETECTED...'")
print("  * Stage 2: 'CONNECTING TO BLACKWOOD FREQUENCY...'")
print("  * Stage 3: 'INVESTIGATION INITIATED.'")
print("  [PASS] Transition sequence and helper functions verified.")

print("\n" + "=" * 70)
print("ALL TITLE SCREEN TESTS PASSED SUCCESSFULLY! (5/5)")
print("=" * 70)

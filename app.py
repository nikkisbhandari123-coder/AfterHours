"""
app.py - AfterHours: An AI-Powered Haunted Radio Mystery Game

Implements:
- Continuous analog radio exploration (80.0 - 110.0 MHz, step 0.1 MHz)
- Deep black chassis, dark forest green panels, phosphor green CRT, amber warnings
- Native HTML rendering via st.html() to guarantee no literal HTML tags or markdown leaks
- Receiver status telemetry bar above the tuning console
- Dynamic signal detection: signal strength ramps up as player approaches active transmissions
- Fringe frequencies produce distorted transmission fragments and static
- Functional Tune/Lock button that stabilizes and reveals full broadcasts and awards clues
- "The Disappearance of Blackwood" connected mystery progression
- Case Synthesis decision module with two distinct endings (Broadcast Truth vs. Enforce Quarantine)
- Unified and visually consistent Investigation Evidence Notebook with source frequencies and timestamps
"""

import streamlit as st
import html
from datetime import datetime
from story import (
    MYSTERY_TITLE,
    REQUIRED_MYSTERY_FREQUENCIES,
    RADIO_STATIONS,
    KNOWN_FREQUENCIES,
    ENDINGS,
    resolve_frequency_telemetry,
    get_initial_state,
    add_clue_to_state,
    check_investigation_complete,
    get_mystery_progress,
    record_player_decision,
)
from ai_engine import (
    check_ollama_service,
    get_cached_ambient,
    synthesize_radio_signal,
)

# -------------------------------------------------------------------
# Streamlit Page Setup
# -------------------------------------------------------------------
st.set_page_config(
    page_title="AFTERHOURS | Haunted Radio Mystery",
    page_icon="📻",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -------------------------------------------------------------------
# Custom CSS: Vintage CRT, Forest Green Chassis & Atmospheric Design
# -------------------------------------------------------------------
st.html(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=VT323&family=Space+Mono:wght@400;700&display=swap');

    /* Global Atmosphere */
    .stApp {
        background-color: #060807;
        background-image: 
            radial-gradient(ellipse at 50% 0%, #111a14 0%, #060807 70%),
            radial-gradient(circle at 10% 90%, #080d0a 0%, transparent 50%);
        color: #cfd8d2;
        font-family: 'Share Tech Mono', 'Courier New', monospace;
    }

    /* Header Banner */
    .header-banner {
        text-align: center;
        padding: 4px 0 16px 0;
        border-bottom: 1px dashed #1c2b20;
        margin-bottom: 20px;
    }

    .main-title {
        font-family: 'VT323', monospace;
        font-size: 4.2rem;
        letter-spacing: 12px;
        color: #ffb703;
        text-shadow: 0 0 12px rgba(255, 183, 3, 0.45);
        margin: 0;
        line-height: 1;
    }

    .tagline {
        font-size: 1.15rem;
        color: #8fa394;
        font-style: italic;
        letter-spacing: 2px;
        margin-top: 6px;
    }

    .chassis-badge {
        display: inline-block;
        font-size: 0.72rem;
        background: #090e0b;
        border: 1px solid #ffb703;
        color: #ffb703;
        padding: 2px 10px;
        border-radius: 3px;
        letter-spacing: 2px;
        margin-top: 8px;
    }

    /* Receiver Status Telemetry Bar */
    .receiver-status-bar {
        background: #080d0a;
        border: 1px solid #1c2b20;
        border-radius: 6px;
        padding: 10px 14px;
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.78rem;
        color: #8c9b91;
        letter-spacing: 1px;
    }

    .status-indicator-light {
        color: #39ff14;
        text-shadow: 0 0 6px #39ff14;
        font-size: 0.95rem;
        margin-right: 4px;
    }

    .status-divider {
        color: #1f3024;
    }

    /* Large Vintage Frequency Display */
    .freq-readout-box {
        background: #040705;
        border: 2px solid #1a2a1e;
        border-radius: 8px;
        padding: 14px 18px;
        text-align: center;
        margin: 12px 0;
        box-shadow: inset 0 0 15px rgba(0, 0, 0, 0.9);
    }

    .freq-number {
        font-family: 'VT323', monospace;
        font-size: 3.8rem;
        color: #39ff14;
        text-shadow: 0 0 10px rgba(57, 255, 20, 0.6);
        letter-spacing: 4px;
        line-height: 1;
        margin: 0;
    }

    .freq-status-pill {
        display: inline-block;
        font-size: 0.78rem;
        letter-spacing: 1.5px;
        padding: 3px 10px;
        border-radius: 3px;
        margin-top: 6px;
        text-transform: uppercase;
        font-weight: bold;
    }

    .status-locked {
        background: rgba(57, 255, 20, 0.15);
        color: #39ff14;
        border: 1px solid #39ff14;
    }

    .status-carrier-detected {
        background: rgba(255, 183, 3, 0.2);
        color: #ffd166;
        border: 1px solid #ffd166;
        box-shadow: 0 0 8px rgba(255, 183, 3, 0.3);
    }

    .status-fringe {
        background: rgba(255, 183, 3, 0.12);
        color: #ffb703;
        border: 1px solid #ffb703;
    }

    .status-static {
        background: rgba(140, 155, 145, 0.12);
        color: #8c9b91;
        border: 1px solid #2a3a2e;
    }

    /* Analog Dial Ruler Scale */
    .dial-scale-container {
        background: #0a110d;
        border: 1px solid #1c2b20;
        border-radius: 4px;
        padding: 8px 12px;
        margin: 10px 0 14px 0;
        font-size: 0.75rem;
        color: #6a7c70;
        letter-spacing: 1px;
    }

    .scale-ticks {
        display: flex;
        justify-content: space-between;
        margin-top: 4px;
        color: #8c9b91;
    }

    /* CRT Monitor Frame & Atmospheric Scanlines */
    @keyframes subtleCrtFlicker {
        0% { opacity: 0.985; }
        48% { opacity: 1.0; }
        50% { opacity: 0.97; }
        52% { opacity: 1.0; }
        100% { opacity: 0.985; }
    }

    .crt-monitor {
        background-color: #040805;
        border: 2px solid #1c2b20;
        border-radius: 8px;
        padding: 20px;
        position: relative;
        box-shadow: inset 0 0 25px rgba(0, 0, 0, 0.9), 0 0 15px rgba(0, 255, 100, 0.05);
        margin-bottom: 20px;
        overflow: hidden;
        animation: subtleCrtFlicker 6s infinite ease-in-out;
    }

    .crt-monitor::before {
        content: " ";
        display: block;
        position: absolute;
        top: 0; left: 0; bottom: 0; right: 0;
        background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.35) 50%);
        background-size: 100% 4px;
        z-index: 2;
        pointer-events: none;
        opacity: 0.45;
    }

    .crt-header-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #1a2a1e;
        padding-bottom: 8px;
        margin-bottom: 12px;
        font-size: 0.85rem;
    }

    .crt-callsign {
        font-size: 1.3rem;
        color: #39ff14;
        font-weight: bold;
        letter-spacing: 2px;
        margin: 0;
    }

    .crt-category {
        color: #ffb703;
        font-size: 0.8rem;
        letter-spacing: 1.5px;
    }

    /* CRT Monospace Typewriter Text Box */
    .crt-text-body {
        font-family: 'Space Mono', 'Courier New', monospace;
        font-size: 1.05rem;
        color: #bbf7c7;
        line-height: 1.7;
        background: rgba(10, 18, 13, 0.65);
        border-left: 3px solid #39ff14;
        padding: 16px 18px;
        margin-top: 14px;
        border-radius: 4px;
        white-space: pre-wrap;
        word-wrap: break-word;
    }

    .terminal-cursor {
        display: inline-block;
        width: 8px;
        height: 16px;
        background-color: #39ff14;
        vertical-align: middle;
        margin-left: 4px;
        animation: blinkCursor 0.9s infinite;
    }

    @keyframes blinkCursor {
        0%, 49% { opacity: 1; }
        50%, 100% { opacity: 0; }
    }

    /* Signal Strength Component */
    .signal-meter-box {
        background: #060b08;
        border: 1px solid #1a291d;
        border-radius: 6px;
        padding: 12px 14px;
        margin: 14px 0;
    }

    .meter-label-row {
        display: flex;
        justify-content: space-between;
        font-size: 0.82rem;
        color: #8c9b91;
        margin-bottom: 6px;
    }

    .meter-bars-row {
        display: flex;
        gap: 5px;
        align-items: flex-end;
        height: 20px;
    }

    .meter-segment {
        flex: 1;
        background-color: #121c15;
        border-radius: 2px;
        transition: all 0.25s ease;
    }

    .meter-segment.lit-amber {
        background-color: #ffb703;
        box-shadow: 0 0 6px rgba(255, 183, 3, 0.6);
    }

    .meter-segment.lit-green {
        background-color: #39ff14;
        box-shadow: 0 0 6px rgba(57, 255, 20, 0.7);
    }

    /* Lock Feedback Banner */
    .lock-feedback-box {
        background: rgba(14, 25, 18, 0.85);
        border: 1px solid #1f3525;
        border-radius: 4px;
        padding: 8px 12px;
        margin-top: 8px;
        font-size: 0.8rem;
        letter-spacing: 0.5px;
    }

    /* Case Resolution Synthesis Banner */
    .case-synthesis-banner {
        background: linear-gradient(180deg, #182217 0%, #0d160f 100%);
        border: 2px solid #ffb703;
        border-radius: 8px;
        padding: 18px 20px;
        margin-bottom: 18px;
        box-shadow: 0 0 15px rgba(255, 183, 3, 0.2);
    }

    .synthesis-badge {
        display: inline-block;
        background: #ffb703;
        color: #070a08;
        font-size: 0.72rem;
        font-weight: bold;
        padding: 2px 8px;
        border-radius: 3px;
        letter-spacing: 1.5px;
        margin-bottom: 8px;
    }

    .synthesis-title {
        color: #ffb703;
        font-size: 1.3rem;
        margin: 4px 0 10px 0;
        letter-spacing: 1px;
    }

    .synthesis-desc {
        color: #c5d6cb;
        font-size: 0.95rem;
        line-height: 1.6;
        margin-bottom: 10px;
    }

    /* Ending Terminal */
    .ending-terminal {
        background-color: #040805;
        border: 2px solid #233728;
        border-radius: 8px;
        padding: 24px;
        position: relative;
        box-shadow: inset 0 0 30px rgba(0, 0, 0, 0.95), 0 0 20px rgba(0, 255, 100, 0.08);
        margin-bottom: 20px;
    }

    .ending-badge {
        display: inline-block;
        font-size: 0.75rem;
        padding: 3px 10px;
        border-radius: 3px;
        letter-spacing: 2px;
        font-weight: bold;
        margin-bottom: 10px;
    }

    .ending-title {
        font-family: 'VT323', monospace;
        font-size: 2.8rem;
        margin: 4px 0;
        letter-spacing: 4px;
        line-height: 1.1;
    }

    .ending-subtitle {
        font-size: 1.05rem;
        color: #8c9b91;
        font-style: italic;
        margin-bottom: 16px;
        border-bottom: 1px dashed #1c2b20;
        padding-bottom: 10px;
    }

    .ending-text {
        font-family: 'Space Mono', 'Courier New', monospace;
        font-size: 1.02rem;
        line-height: 1.75;
        color: #d1ded4;
        white-space: pre-wrap;
    }

    /* Evidence Log Panel */
    .evidence-panel {
        background: linear-gradient(180deg, #0e1711 0%, #080e0a 100%);
        border: 2px solid #1c2b20;
        border-radius: 8px;
        padding: 18px 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.7);
    }

    .evidence-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px dashed #1c2b20;
        padding-bottom: 10px;
        margin-bottom: 14px;
    }

    .clue-card {
        background: #090e0b;
        border: 1px solid #1c2b20;
        border-left: 4px solid #4a5c50;
        border-radius: 5px;
        padding: 12px 14px;
        margin-bottom: 10px;
    }

    .clue-card.highlight-new {
        border-left: 4px solid #ffb703;
        background: #0d140f;
        box-shadow: 0 0 8px rgba(255, 183, 3, 0.12);
    }

    .clue-header-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
    }

    .clue-meta-left {
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .clue-badge-freq {
        display: inline-block;
        background: #111d14;
        color: #39ff14;
        border: 1px solid #1f3525;
        font-size: 0.74rem;
        padding: 2px 7px;
        border-radius: 3px;
        font-weight: bold;
    }

    .clue-badge-new {
        display: inline-block;
        background: rgba(255, 183, 3, 0.15);
        color: #ffb703;
        border: 1px solid #ffb703;
        font-size: 0.7rem;
        padding: 2px 6px;
        border-radius: 3px;
        font-weight: bold;
    }

    .clue-timestamp {
        color: #718377;
        font-size: 0.74rem;
    }

    .clue-body-text {
        color: #d1ded4;
        font-size: 0.94rem;
        line-height: 1.5;
        margin-top: 4px;
    }

    /* Streamlit Custom Controls */
    .stSlider > div [data-baseweb="slider"] {
        color: #39ff14;
    }

    .stButton>button {
        background: linear-gradient(180deg, #ffb703 0%, #b27a00 100%) !important;
        color: #070a08 !important;
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 1.05rem !important;
        font-weight: bold !important;
        letter-spacing: 2px !important;
        border: 1px solid #ffd166 !important;
        border-radius: 6px !important;
        padding: 10px 18px !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.6) !important;
        width: 100%;
        transition: all 0.2s ease-in-out;
    }

    .stButton>button:hover {
        background: linear-gradient(180deg, #ffd166 0%, #d49000 100%) !important;
        box-shadow: 0 0 12px rgba(255, 183, 3, 0.6) !important;
    }

    /* Responsive adjustments */
    @media (max-width: 900px) {
        .main-title {
            font-size: 3rem;
            letter-spacing: 6px;
        }
        .freq-number {
            font-size: 2.8rem;
        }
    }
    </style>
    """
)

# -------------------------------------------------------------------
# State Management
# -------------------------------------------------------------------
if "game_state" not in st.session_state:
    st.session_state.game_state = get_initial_state()

state = st.session_state.game_state

# -------------------------------------------------------------------
# UI: Header Banner
# -------------------------------------------------------------------
st.html(
    """
    <div class="header-banner">
        <h1 class="main-title">AFTERHOURS</h1>
        <div class="tagline">"Some signals should never be heard."</div>
        <div class="chassis-badge">MODEL AR-1978 SHORTWAVE TRANSCEIVER // 80.0 — 110.0 MHz</div>
    </div>
    """
)

# -------------------------------------------------------------------
# Layout: Two Responsive Modular Panels
# -------------------------------------------------------------------
col_tuner, col_monitor = st.columns([1, 1.4], gap="large")

# ---------------------------------------------------------
# Column 1: Continuous Analog Tuner Console
# ---------------------------------------------------------
with col_tuner:
    ollama_status = check_ollama_service()
    ai_available = ollama_status.get("available", False)
    ai_model_name = ollama_status.get("model") or "STANDBY"
    ai_label = f"GEMMA (LOCAL: {ai_model_name})" if ai_available else "STANDBY (FALLBACK)"
    ai_color = "#39ff14" if ai_available else "#8c9b91"

    st.html(
        f"""
        <div class="receiver-status-bar">
            <div>
                <span class="status-indicator-light">●</span>
                <span>SYSTEM: <strong>READY</strong></span>
            </div>
            <span class="status-divider">|</span>
            <div>BAND: <strong>FM SHORTWAVE</strong></div>
            <span class="status-divider">|</span>
            <div>AI: <strong style="color: {ai_color};">{html.escape(ai_label)}</strong></div>
        </div>
        """
    )

    st.subheader("🎛️ ANALOG TUNING CAPACITOR")
    st.caption("Rotate the tuning capacitor dial across the shortwave band.")

    # Continuous Draggable Tuner from 80.0 to 110.0 MHz, step 0.1
    current_slider_val = float(state.get("active_frequency", 80.0))
    tuner_freq = st.slider(
        "Frequency Tuning Dial (MHz)",
        min_value=80.0,
        max_value=110.0,
        value=current_slider_val,
        step=0.1,
        format="%.1f MHz",
        help="Drag continuously to sweep the radio frequencies.",
    )

    tuner_freq = round(tuner_freq, 1)

    # Detune Check: If dial moves away from locked carrier, break the lock
    locked_freq = state.get("locked_frequency")
    if locked_freq is not None and abs(tuner_freq - locked_freq) > 0.1:
        state["is_locked"] = False
        state["locked_frequency"] = None
        state["lock_feedback"] = "Carrier lock lost due to frequency drift."

    state["active_frequency"] = tuner_freq

    # Calculate telemetry for active dial position with cached AI lookup
    clues_count = len(state.get("discovered_clues", []))
    cached_ai = get_cached_ambient(tuner_freq, clues_count)
    live_telemetry = resolve_frequency_telemetry(
        freq=tuner_freq,
        is_locked=state.get("is_locked", False),
        locked_freq=state.get("locked_frequency"),
        clues_count=clues_count,
        cached_ai_snippet=cached_ai,
    )
    is_currently_locked = live_telemetry["is_locked"]

    # Large Frequency Display Box with dynamic status
    if is_currently_locked:
        status_class = "status-locked"
    elif live_telemetry["can_lock"]:
        status_class = "status-carrier-detected"
    elif live_telemetry["status"] == "SIGNAL BLEED":
        status_class = "status-fringe"
    else:
        status_class = "status-static"

    st.html(
        f"""
        <div class="freq-readout-box">
            <div class="freq-number">{tuner_freq:.1f} MHz</div>
            <span class="freq-status-pill {status_class}">
                {html.escape(live_telemetry['status_label'])}
            </span>
        </div>
        """
    )

    # Analog Dial Scale / Frequency Tick Ruler (Keeps known frequency markers)
    st.html(
        """
        <div class="dial-scale-container">
            <div>FM SHORTWAVE SCALE (MHz)</div>
            <div class="scale-ticks">
                <span>80.0</span>
                <span>•</span>
                <span style="color: #ffb703;">88.1</span>
                <span>•</span>
                <span style="color: #ffb703;">91.7</span>
                <span>•</span>
                <span>100.0</span>
                <span>•</span>
                <span style="color: #ffb703;">103.4</span>
                <span>•</span>
                <span style="color: #ffb703;">107.9</span>
                <span>110.0</span>
            </div>
        </div>
        """
    )

    # Tune / Lock Button Logic
    if is_currently_locked:
        lock_button_label = f"🔒 LOCKED ON {tuner_freq:.1f} MHz"
    elif live_telemetry["can_lock"]:
        lock_button_label = f"📻 TUNE / LOCK CARRIER ({live_telemetry['target_freq']:.1f} MHz)"
    else:
        lock_button_label = "📻 TUNE FREQUENCY (SEARCHING...)"

    tune_clicked = st.button(lock_button_label, use_container_width=True)

    if tune_clicked:
        if live_telemetry["can_lock"]:
            target = live_telemetry["target_freq"]
            state["is_locked"] = True
            state["locked_frequency"] = target
            state["active_frequency"] = target
            
            # Resolve locked broadcast and award clue (Strict Story Protection: 100% Python-Controlled)
            locked_data = resolve_frequency_telemetry(target, is_locked=True, locked_freq=target)
            if locked_data.get("clue"):
                clue_added = add_clue_to_state(
                    state=state,
                    clue_text=locked_data["clue"],
                    source_freq=f"{target:.1f} MHz",
                )
                if clue_added:
                    state["lock_feedback"] = f"● Carrier locked! New evidence intercepted from {target:.1f} MHz."
                else:
                    state["lock_feedback"] = f"● Carrier locked on {target:.1f} MHz. (Clue already recorded)."
            else:
                state["lock_feedback"] = f"● Carrier locked on {target:.1f} MHz."
        else:
            state["is_locked"] = False
            state["locked_frequency"] = None
            if ai_available:
                with st.spinner(f"Intercepting atmospheric RF on {tuner_freq:.1f} MHz with Gemma AI..."):
                    target_f = live_telemetry.get("target_freq")
                    synth_res = synthesize_radio_signal(
                        frequency=tuner_freq,
                        status_category=live_telemetry["status"],
                        clues_count=clues_count,
                        nearest_station=RADIO_STATIONS.get(target_f) if target_f else None,
                        dist_to_station=abs(tuner_freq - (target_f or 999.0)),
                        force_generate=True,
                    )
                    if synth_res.get("source") == "GEMMA_AI":
                        state["lock_feedback"] = f"● Atmospheric anomaly intercepted at {tuner_freq:.1f} MHz via local Gemma AI."
                    else:
                        state["lock_feedback"] = f"○ No stable carrier at {tuner_freq:.1f} MHz. Only static noise."
            else:
                state["lock_feedback"] = f"○ Lock failed: No stable carrier at {tuner_freq:.1f} MHz. Only static noise."
        st.rerun()

    # Dedicated On-Demand AI Intercept button for dead air & fringe frequencies
    if not is_currently_locked and ai_available and not live_telemetry["can_lock"]:
        if st.button("⚡ INTERCEPT SIGNAL WITH GEMMA AI", use_container_width=True):
            with st.spinner(f"Intercepting shortwave anomaly at {tuner_freq:.1f} MHz with Gemma AI..."):
                target_f = live_telemetry.get("target_freq")
                synth_res = synthesize_radio_signal(
                    frequency=tuner_freq,
                    status_category=live_telemetry["status"],
                    clues_count=clues_count,
                    nearest_station=RADIO_STATIONS.get(target_f) if target_f else None,
                    dist_to_station=abs(tuner_freq - (target_f or 999.0)),
                    force_generate=True,
                )
                if synth_res.get("source") == "GEMMA_AI":
                    state["lock_feedback"] = f"● Gemma AI intercept decoded at {tuner_freq:.1f} MHz."
                else:
                    state["lock_feedback"] = f"○ Faint anomaly faded into magnetic tape hiss."
            st.rerun()

    # Dynamic Signal Strength Indicator
    sig_bars = live_telemetry["signal_bars"]
    sig_pct = live_telemetry["signal_percent"]
    sig_lbl = live_telemetry["signal_label"]

    st.html(
        f"""
        <div class="signal-meter-box">
            <div class="meter-label-row">
                <span>CARRIER SIGNAL STRENGTH</span>
                <span style="color: {'#39ff14' if sig_bars >= 4 else '#ffb703'}; font-weight: bold;">
                    {html.escape(sig_lbl)} ({sig_pct}%)
                </span>
            </div>
            <div class="meter-bars-row">
                <div class="meter-segment {'lit-green' if sig_bars >= 1 else ''}" style="height: 20%;"></div>
                <div class="meter-segment {'lit-green' if sig_bars >= 2 else ''}" style="height: 40%;"></div>
                <div class="meter-segment {'lit-amber' if sig_bars >= 3 else ''}" style="height: 60%;"></div>
                <div class="meter-segment {'lit-amber' if sig_bars >= 4 else ''}" style="height: 80%;"></div>
                <div class="meter-segment {'lit-amber' if sig_bars >= 5 else ''}" style="height: 100%;"></div>
            </div>
        </div>
        """
    )

    # Receiver Feedback Note
    if state.get("lock_feedback"):
        color = "#39ff14" if state.get("is_locked") else "#ffb703"
        st.html(
            f"""
            <div class="lock-feedback-box" style="color: {color};">
                {html.escape(state['lock_feedback'])}
            </div>
            """
        )

# ---------------------------------------------------------
# Column 2: CRT Monitor, Mystery Synthesis & Clue Notebook
# ---------------------------------------------------------
with col_monitor:
    chosen_ending_key = state.get("chosen_ending")

    # -----------------------------------------------------
    # BRANCH A: Player has reached a narrative ending
    # -----------------------------------------------------
    if chosen_ending_key and chosen_ending_key in ENDINGS:
        ending = ENDINGS[chosen_ending_key]
        ending_color = ending.get("theme_color", "#39ff14")
        escaped_ending_narrative = html.escape(ending["narrative"])

        st.html(
            f"""
            <div class="ending-terminal" style="border-color: {ending_color};">
                <span class="ending-badge" style="background: {ending_color}; color: #040805;">
                    {html.escape(ending['badge'])}
                </span>
                <h2 class="ending-title" style="color: {ending_color};">
                    {html.escape(ending['title'])}
                </h2>
                <div class="ending-subtitle">
                    {html.escape(ending['subtitle'])}
                </div>
                <div class="ending-text">{escaped_ending_narrative}</div>
            </div>
            """
        )

        if st.button("↺ RE-OPEN CASE INVESTIGATION (EXPLORE ALTERNATE CHOICE)", use_container_width=True):
            state["chosen_ending"] = None
            st.rerun()

    # -----------------------------------------------------
    # BRANCH B: Active gameplay exploration & mystery progress
    # -----------------------------------------------------
    else:
        escaped_transmission = html.escape(live_telemetry["transmission"])
        current_time_str = datetime.now().strftime("%I:%M:%S %p")

        # Monitor header color and authentication badge
        if live_telemetry["is_locked"]:
            rec_color = "#39ff14"
            rec_text = "● LOCKED"
            tag_badge = '<span style="background: rgba(57, 255, 20, 0.15); border: 1px solid #39ff14; color: #39ff14; font-size: 0.68rem; padding: 2px 6px; border-radius: 3px; letter-spacing: 1px; margin-left: 8px;">CANONICAL BROADCAST</span>'
        elif live_telemetry["can_lock"]:
            rec_color = "#ffb703"
            rec_text = "◉ CARRIER DETECTED"
            tag_badge = '<span style="background: rgba(255, 183, 3, 0.15); border: 1px solid #ffb703; color: #ffd166; font-size: 0.68rem; padding: 2px 6px; border-radius: 3px; letter-spacing: 1px; margin-left: 8px;">CARRIER PHASE LOCKED</span>'
        elif live_telemetry.get("is_ai_generated"):
            rec_color = "#39ff14"
            rec_text = "◐ AI INTERCEPT"
            tag_badge = '<span style="background: rgba(57, 255, 20, 0.18); border: 1px solid #39ff14; color: #39ff14; font-size: 0.68rem; padding: 2px 6px; border-radius: 3px; letter-spacing: 1px; margin-left: 8px;">GEMMA AI SYNTHESIZED</span>'
        else:
            rec_color = "#6a7c70"
            rec_text = "○ SEARCHING"
            tag_badge = '<span style="background: rgba(140, 155, 145, 0.12); border: 1px solid #2a3a2e; color: #8c9b91; font-size: 0.68rem; padding: 2px 6px; border-radius: 3px; letter-spacing: 1px; margin-left: 8px;">BACKGROUND RF STATIC</span>'

        st.html(
            f"""
            <div class="crt-monitor">
                <div class="crt-header-bar">
                    <div>
                        <span style="color: {rec_color}; font-weight: bold; margin-right: 8px;">{rec_text}</span>
                        <span style="color: #6a7c70;">[{current_time_str}]</span>
                        {tag_badge}
                    </div>
                    <div class="crt-category">{html.escape(live_telemetry['category'].upper())}</div>
                </div>
                
                <div style="display: flex; justify-content: space-between; align-items: baseline;">
                    <h3 class="crt-callsign">{html.escape(live_telemetry['callsign'])}</h3>
                    <div style="color: #39ff14; font-size: 0.85rem; letter-spacing: 1px;">
                        {tuner_freq:.1f} MHz
                    </div>
                </div>
                
                <div style="color: #8c9b91; font-size: 0.9rem; margin-top: 4px;">
                    {html.escape(live_telemetry['station_name'])}
                </div>
                <div style="color: #5c6c61; font-size: 0.82rem; margin-top: 2px;">
                    {html.escape(live_telemetry['description'])}
                </div>

                <div style="font-size: 0.78rem; color: #ffb703; margin-top: 16px; letter-spacing: 1.5px;">
                    AUDIO DECODER TRANSCRIPT:
                </div>
                <div class="crt-text-body">{escaped_transmission}<span class="terminal-cursor"></span></div>
            </div>
            """
        )

        # -------------------------------------------------
        # Mystery Synthesis Module (Appears when all 4 clues are unlocked)
        # -------------------------------------------------
        is_investigation_complete = check_investigation_complete(state)

        if is_investigation_complete:
            st.html(
                """
                <div class="case-synthesis-banner">
                    <span class="synthesis-badge">⚠️ CASE SYNTHESIS UNLOCKED</span>
                    <h3 class="synthesis-title">THE DISAPPEARANCE OF BLACKWOOD: RESOLUTION</h3>
                    <div class="synthesis-desc">
                        All four mystery transmissions have been intercepted and authenticated.<br><br>
                        • <strong>88.1 MHz (Weather)</strong>: Claimed a natural mudslide closed the Route 9 bridge while noting anomalous atmospheric ionization and lantern lights.<br>
                        • <strong>91.7 MHz (Civil Defense)</strong>: Contradicted the weather report, ordering an evacuation and cordoning the bridge with armed chemical units.<br>
                        • <strong>103.4 MHz (Police)</strong>: Proved civilian cars were abandoned at the bridge and revealed the Mayor pre-drafted the evacuation order hours ahead of time.<br>
                        • <strong>107.9 MHz (Station Zero)</strong>: Clandestine cipher 4-19-88-0 confirmed the valley floodgates were deliberately opened from the inside to drown Blackwood and bury the discovery.<br><br>
                        You hold the only shortwave transmitter coupled to the county emergency repeaters.
                        What is your decision?
                    </div>
                </div>
                """
            )

            col_choice1, col_choice2 = st.columns(2)
            with col_choice1:
                if st.button("📢 BROADCAST THE TRUTH\n(OVERRIDE REPEATERS)", use_container_width=True):
                    record_player_decision(state, "truth")
                    st.rerun()
            with col_choice2:
                if st.button("🔒 ENFORCE QUARANTINE\n(DEGAUSS & ERASE TAPES)", use_container_width=True):
                    record_player_decision(state, "quarantine")
                    st.rerun()

    # -----------------------------------------------------
    # Investigation Evidence Notebook (Rendered as unified styled cards)
    # -----------------------------------------------------
    clues_list = state.get("discovered_clues", [])
    cards_html_list = []
    mystery_prog = get_mystery_progress(state)

    if clues_list:
        # Render cards in reverse chronological order (newest first)
        for clue_item in reversed(clues_list):
            is_new = clue_item.get("is_new", False)
            freq_source = html.escape(str(clue_item.get("frequency", "UNKNOWN")))
            clue_ts = html.escape(str(clue_item.get("timestamp", "")))
            clue_text = html.escape(str(clue_item.get("text", "")))
            card_class = "clue-card highlight-new" if is_new else "clue-card"
            new_badge = '<span class="clue-badge-new">NEW DISCOVERY</span>' if is_new else ''

            cards_html_list.append(
                f"""
                <div class="{card_class}">
                    <div class="clue-header-row">
                        <div class="clue-meta-left">
                            <span class="clue-badge-freq">{freq_source}</span>
                            {new_badge}
                        </div>
                        <span class="clue-timestamp">{clue_ts}</span>
                    </div>
                    <div class="clue-body-text">{clue_text}</div>
                </div>
                """
            )
        cards_html_content = "".join(cards_html_list)
    else:
        cards_html_content = (
            '<div style="color: #6a7c70; font-style: italic; padding: 12px 0;">'
            'No clues uncovered yet. Sweep the frequency dial to intercept broadcasts.</div>'
        )

    # Progress badge label
    if mystery_prog["is_complete"]:
        progress_label = '<span style="color: #ffb703; font-weight: bold;">CASE READY FOR RESOLUTION</span>'
    else:
        progress_label = (
            f"PROGRESS: <strong style='color: #39ff14;'>"
            f"{mystery_prog['total_discovered']} / {mystery_prog['total_required']}</strong> KEY SIGNALS DECODED"
        )

    st.html(
        f"""
        <div class="evidence-panel">
            <div class="evidence-header">
                <div>
                    <h3 style="margin: 0; color: #ffb703; font-size: 1.15rem; letter-spacing: 1px;">
                        🗂️ INVESTIGATION EVIDENCE LOG
                    </h3>
                    <div style="font-size: 0.78rem; color: #8c9b91; margin-top: 2px;">
                        MYSTERY: <em>"{html.escape(MYSTERY_TITLE)}"</em>
                    </div>
                </div>
                <span style="font-size: 0.82rem; color: #8c9b91;">
                    {progress_label}
                </span>
            </div>
            <div class="clues-container">
                {cards_html_content}
            </div>
        </div>
        """
    )

    # Reset logs button
    col_r1, col_r2 = st.columns([1.5, 1])
    with col_r2:
        st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
        if st.button("Reset Investigation Log", type="secondary"):
            st.session_state.game_state = get_initial_state()
            st.rerun()

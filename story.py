"""
story.py - Narrative, Signal Telemetry & Story Progression for AfterHours

Manages:
- The 4 connected mystery transmissions for "The Disappearance of Blackwood"
- Proximity-based dynamic signal detection across 80.0 - 110.0 MHz
- Investigation synthesis, contradictions, and mystery completion logic
- Two branching narrative conclusions (Broadcast Truth vs. Enforce Quarantine)
- Persistent clue notebook state with duplicate prevention
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import math
import html

# -------------------------------------------------------------------
# Mystery Metadata
# -------------------------------------------------------------------
MYSTERY_TITLE = "The Disappearance of Blackwood"
REQUIRED_MYSTERY_FREQUENCIES: List[float] = [88.1, 91.7, 103.4, 107.9]

# -------------------------------------------------------------------
# The 4 Connected Radio Stations ("The Disappearance of Blackwood")
# -------------------------------------------------------------------
RADIO_STATIONS: Dict[float, Dict[str, Any]] = {
    88.1: {
        "name": "Blackwood Weather Broadcast (K-MIST Automated)",
        "callsign": "K-MIST 88.1",
        "category": "Weather Alert",
        "station_key": "weather",
        "description": "Continuous automated barometric updates and mountain civil weather warnings.",
        "transmission": (
            "[Synthesized Weather Tone] ...Blackwood Valley automated weather bulletin at 02:40 AM. "
            "Unprecedented barometric plunge detected over Blackwood Ridge, dropping 22 millibars in ten minutes. "
            "Dense freezing fog containing unclassified particulate is engulfing the lowlands. All motorists "
            "are advised that the Route 9 trestle bridge is closed due to localized mudslides. "
            "Do not stop for flickering lantern lights in the tree line..."
        ),
        "distorted_fragment": (
            "...*kzz-hiss*... [CARRIER BLEED FROM K-MIST 88.1] ...'...barometric pressure plunging... "
            "freezing fog engulfing lowlands... Route 9 trestle closed due to mudslides... lantern lights in tree line...'... *static wash*..."
        ),
        "clue": (
            "Weather beacon claims the Route 9 trestle bridge was closed by natural mudslides, "
            "while reporting anomalous barometric drops and strange lantern lights along Blackwood Ridge."
        ),
        "base_strength": 94,
    },
    91.7: {
        "name": "Civil Defense Emergency Transmission",
        "callsign": "CD-ALERT 91.7",
        "category": "Emergency Broadcast",
        "station_key": "defense",
        "description": "Echoing civil alert siren and looping emergency broadcast protocol.",
        "transmission": (
            "[Civil Defense Klaxon Loop] ...Emergency transmission priority one. Evacuation order is mandatory "
            "for sectors four through nine due to unconfirmed water reservoir contamination. Residents are instructed "
            "to extinguish all exterior illumination and seal ventilation ducts. Do not attempt to evacuate via the Route 9 "
            "trestle bridge—the bridge has been cordoned by military personnel in chemical protective gear. "
            "Do not approach the perimeter..."
        ),
        "distorted_fragment": (
            "...*wailing siren bleed*... [CARRIER BLEED FROM CD-ALERT 91.7] ...'...evacuation mandatory for sectors four "
            "through nine... extinguish all lights... Route 9 trestle cordoned by military units in chemical gear...'... *electrical whine*..."
        ),
        "clue": (
            "Civil Defense contradicts the weather service: the Route 9 trestle was cordoned by armed military units "
            "in chemical gear, not closed by a natural mudslide."
        ),
        "base_strength": 90,
    },
    103.4: {
        "name": "Blackwood County Police Transmission",
        "callsign": "SHERIFF-DISP 103.4",
        "category": "Police Dispatch Archive",
        "station_key": "police",
        "description": "Crackling analog police radio repeater playback from the night of October 19, 1984.",
        "transmission": (
            "...*kzzzt*... Dispatch to Unit 6, respond to the Route 9 trestle bridge immediately. "
            "We have multiple 911 calls reporting six civilian vehicles abandoned on the bridge approach with driver "
            "doors standing open and headlights blazing. Checkpoint Bravo has completely gone dark. Dispatch note: "
            "the Mayor's office drafted this evacuation order at 11:00 PM last night—hours before any siren or reservoir "
            "warning sounded. They knew what was coming... *heavy RF burst*..."
        ),
        "distorted_fragment": (
            "...*crackling radio flutter*... [CARRIER BLEED FROM SHERIFF-DISP 103.4] ...'...six civilian vehicles abandoned "
            "with headlights blazing... Checkpoint Bravo is dark... Mayor drafted evacuation hours before sirens sounded...'... *burst of static*..."
        ),
        "clue": (
            "Sheriff dispatch confirms civilian cars were abandoned with headlights on near the bridge, and proves "
            "the Mayor's office drafted the evacuation order hours before any official flood alert was issued."
        ),
        "base_strength": 86,
    },
    107.9: {
        "name": "Mysterious Hidden Transmission (Phantom Station Zero)",
        "callsign": "CARRIER-ZERO 107.9",
        "category": "Clandestine Numbers Station",
        "station_key": "truth",
        "description": "A buried high-frequency shortwave carrier emitting a melodic music box chime and encrypted numbers cipher.",
        "transmission": (
            "...[Music box chime: 4 slow notes]... Cipher sequence: 4-19-88-0 (Four... nineteen... eighty-eight... zero)... "
            "[heavy electromagnetic pulse]... Emergency override authenticated. The valley floodgates were not breached by storm surge. "
            "The manual release valves were engaged from inside the central control room. Blackwood was drowned intentionally to bury "
            "whatever was unearthed beneath Blackwood Ridge. Repeat cipher: 4-19-88-0... [chime fades into abyssal static]..."
        ),
        "distorted_fragment": (
            "...[faint music box chime buried in static]... [CARRIER BLEED FROM CARRIER-ZERO 107.9] ...'...four... "
            "nineteen... eighty-eight... zero... floodgates were opened from inside the control room...'... *pulse tone drops*..."
        ),
        "clue": (
            "Clandestine cipher 4-19-88-0 exposes the ultimate truth: the valley floodgates were deliberately opened "
            "from inside the control room to drown Blackwood and bury whatever was unearthed beneath Blackwood Ridge."
        ),
        "base_strength": 80,
    },
}

KNOWN_FREQUENCIES: List[float] = sorted(list(RADIO_STATIONS.keys()))
SUPPORTED_FREQUENCIES: List[float] = KNOWN_FREQUENCIES

# -------------------------------------------------------------------
# Two Branching Endings
# -------------------------------------------------------------------
ENDINGS: Dict[str, Dict[str, str]] = {
    "truth": {
        "title": "THE TRANSMISSION OF TRUTH",
        "subtitle": "The Silence of Blackwood is Shattered",
        "badge": "ENDING A // THE BROADCAST",
        "theme_color": "#39ff14",
        "narrative": (
            "You route the auxiliary emergency transmitter switch directly into the hilltop repeater tower. "
            "The vacuum tubes flare blinding amber as the full shortwave circuit engages.\n\n"
            "Across the dark mountain valley, the static clears on every radio dial from 80.0 to 110.0 MHz. "
            "The weather contradictions, the sheriff's recordings, and the clandestine control room confession "
            "replay simultaneously across Blackwood County.\n\n"
            "The official forty-year lie of a 'tragic natural flash flood' is shattered forever. The families of the "
            "missing finally know why the doors were locked and why the floodgates opened.\n\n"
            "As the truth loops endlessly into the night sky, your signal meter suddenly pegs at 100%. "
            "An unlisted high-power frequency clicks on: 'We have your antenna coordinates. Stand by your receiver.'"
        ),
    },
    "quarantine": {
        "title": "THE BLACKWOOD QUARANTINE",
        "subtitle": "The Valley Remains Asleep",
        "badge": "ENDING B // THE CONCEALMENT",
        "theme_color": "#ffb703",
        "narrative": (
            "Your finger rests on the emergency broadcast switch... but you hesitate. You look through the cracked "
            "studio window toward Blackwood Ridge. The thick, unnatural fog moves against the wind, dense with unclassified particulate.\n\n"
            "Whatever was unearthed beneath the mountain in 1984 wasn't meant to be discovered. The flooding of the valley "
            "was a desperate quarantine to bury it beneath sixty feet of reservoir water.\n\n"
            "You engage the degaussing circuit. High-voltage magnetic pulses sweep through the tape heads, erasing every recorded "
            "transmission and numbers cipher into permanent white noise.\n\n"
            "The analog needle drops back to 80.0 MHz dead air. The secret of Blackwood remains drowned in silence, protected from "
            "those who might venture into the fog to dig it up again.\n\n"
            "You power down the Allied Shortwave console and walk out into the quiet night."
        ),
    },
}

# Procedural static and eerie interference samples for dead air frequencies
ATMOSPHERIC_STATIC_SAMPLES: List[Dict[str, str]] = [
    {
        "type": "Tape Flutter",
        "text": "...*shhhhhhh*... [faint crackle of magnetic tape spooling] ...*whirrrrr*... *pop*...",
    },
    {
        "type": "Distant Voice",
        "text": "...*kzzzt*... '...is anyone still listening on this band?... please...' ...*heavy static wash*...",
    },
    {
        "type": "Carrier Hum",
        "text": "...[low 60Hz electrical hum vibrating through receiver vacuum tubes]... *intermittent click*...",
    },
    {
        "type": "Distorted Music",
        "text": "...*crackle*... [echoing strains of a 1940s ballroom waltz buried beneath white noise] ...*fade out*...",
    },
    {
        "type": "Morse Pulse",
        "text": "...*bzzzzzt*... [faint Morse code tone: · · · — — — · · · ] ...*static pop*...",
    },
    {
        "type": "Spectral Whisper",
        "text": "...*hsssss*... '...do not look toward the mountain ridge...' ...*electronic screech*...",
    },
]


def resolve_frequency_telemetry(
    freq: float,
    is_locked: bool = False,
    locked_freq: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Evaluate signal detection, carrier proximity, dynamic strength, and decoded transmission.
    """
    freq = round(freq, 1)

    # Find the closest known mystery station
    closest_station_freq = None
    min_dist = 999.0
    for k_freq in KNOWN_FREQUENCIES:
        dist = abs(freq - k_freq)
        if dist < min_dist:
            min_dist = dist
            closest_station_freq = k_freq

    closest_station = RADIO_STATIONS[closest_station_freq]
    is_within_lock_range = (min_dist <= 0.1)

    # 1. Dynamic Signal Strength Calculation
    if min_dist <= 0.1:
        signal_percent = int(closest_station["base_strength"] - (min_dist * 40))
    elif min_dist <= 0.4:
        ratio = (0.4 - min_dist) / 0.3
        signal_percent = int(45 + ratio * 30)
    elif min_dist <= 0.8:
        ratio = (0.8 - min_dist) / 0.4
        signal_percent = int(18 + ratio * 22)
    else:
        seed = int(freq * 10)
        signal_percent = max(5, int(abs(math.sin(seed * 0.7)) * 12))

    # Signal bars
    if signal_percent >= 82:
        signal_bars = 5
        signal_label = "STRONG (CARRIER PEAK)"
    elif signal_percent >= 60:
        signal_bars = 4
        signal_label = "MODERATE (HIGH RF)"
    elif signal_percent >= 38:
        signal_bars = 3
        signal_label = "WEAK (CARRIER BLEED)"
    elif signal_percent >= 18:
        signal_bars = 2
        signal_label = "FAINT (RF FRINGE)"
    else:
        signal_bars = 1
        signal_label = "DEAD AIR (STATIC)"

    # 2. Transmission & Status Logic
    # Case A: Carrier Locked at this frequency
    if is_locked and locked_freq is not None and abs(freq - locked_freq) <= 0.1:
        return {
            "is_locked": True,
            "can_lock": True,
            "target_freq": closest_station_freq,
            "status": "LOCKED",
            "status_label": "● CARRIER LOCKED [DECODED]",
            "station_name": closest_station["name"],
            "callsign": closest_station["callsign"],
            "category": closest_station["category"],
            "signal_percent": signal_percent,
            "signal_bars": signal_bars,
            "signal_label": signal_label,
            "description": closest_station["description"],
            "transmission": closest_station["transmission"],
            "clue": closest_station["clue"],
            "source_freq": f"{closest_station_freq:.1f} MHz",
        }

    # Case B: Close enough to lock, but not locked yet (Within 0.1 MHz)
    elif is_within_lock_range:
        return {
            "is_locked": False,
            "can_lock": True,
            "target_freq": closest_station_freq,
            "status": "CARRIER DETECTED",
            "status_label": "◉ CARRIER DETECTED [TUNE / LOCK TO DECODE]",
            "station_name": f"Carrier Wave at {closest_station_freq:.1f} MHz",
            "callsign": "STABLE CARRIER",
            "category": "Interception Ready",
            "signal_percent": signal_percent,
            "signal_bars": signal_bars,
            "signal_label": signal_label,
            "description": f"Strong RF carrier centered on {closest_station_freq:.1f} MHz. Modulation is scrambled.",
            "transmission": (
                f"...*high-frequency carrier tone*... [STABLE CARRIER IDENTIFIED AT {closest_station_freq:.1f} MHz] ...\n\n"
                f"Audio modulation is phase-locked but unaligned. "
                f"Engage the [TUNE / LOCK FREQUENCY] synthesizer to decode the transmission stream..."
            ),
            "clue": None,
            "source_freq": None,
        }

    # Case C: Nearby frequency (0.1 < min_dist <= 0.4 MHz) - Distorted fragments bleed through
    elif min_dist <= 0.4:
        return {
            "is_locked": False,
            "can_lock": False,
            "target_freq": closest_station_freq,
            "status": "SIGNAL BLEED",
            "status_label": "◐ SIGNAL BLEED / FRINGE",
            "station_name": f"Spillover near {closest_station['callsign']}",
            "callsign": "BLEED OVER",
            "category": "Electromagnetic Spillover",
            "signal_percent": signal_percent,
            "signal_bars": signal_bars,
            "signal_label": signal_label,
            "description": f"RF carrier wave bleeding through from neighboring frequency {closest_station_freq:.1f} MHz.",
            "transmission": closest_station["distorted_fragment"],
            "clue": None,
            "source_freq": None,
        }

    # Case D: Dead air / Unknown frequency (min_dist > 0.4 MHz)
    else:
        seed = int(freq * 10)
        sample = ATMOSPHERIC_STATIC_SAMPLES[seed % len(ATMOSPHERIC_STATIC_SAMPLES)]
        return {
            "is_locked": False,
            "can_lock": False,
            "target_freq": None,
            "status": "DEAD AIR",
            "status_label": "○ NO CARRIER / DEAD AIR",
            "station_name": f"Dead Air ({freq:.1f} MHz)",
            "callsign": "RF NOISE",
            "category": sample["type"],
            "signal_percent": signal_percent,
            "signal_bars": signal_bars,
            "signal_label": signal_label,
            "description": "No recognized commercial or emergency carrier detected. Atmospheric hiss and background RF noise.",
            "transmission": sample["text"],
            "clue": None,
            "source_freq": None,
        }


def get_station_data(frequency: float) -> Dict[str, Any]:
    """Backward compatibility alias for resolve_frequency_telemetry."""
    return resolve_frequency_telemetry(frequency, is_locked=True, locked_freq=frequency)


def get_initial_state() -> Dict[str, Any]:
    """Provide the default state for a new exploration session."""
    initial_time = datetime.now().strftime("%I:%M:%S %p")
    default_freq = 80.0

    return {
        "active_frequency": default_freq,
        "locked_frequency": None,
        "is_locked": False,
        "lock_feedback": None,
        "chosen_ending": None,
        "discovered_clues": [
            {
                "id": "init-01",
                "text": "Receiver initialized in abandoned hilltop studio. Shortwave tuner dial is active from 80.0 to 110.0 MHz. Search for active carrier signals.",
                "frequency": "SYSTEM",
                "timestamp": initial_time,
                "is_new": False,
            }
        ],
    }


def add_clue_to_state(state: Dict[str, Any], clue_text: str, source_freq: str) -> bool:
    """
    Add a discovered clue to the notebook if not already present.
    Guarantees no duplicate clues are recorded.
    """
    if not clue_text:
        return False
    
    for existing in state["discovered_clues"]:
        if existing["text"] == clue_text:
            return False

    current_time = datetime.now().strftime("%I:%M:%S %p")
    new_entry = {
        "id": f"clue-{len(state['discovered_clues']) + 1}",
        "text": clue_text,
        "frequency": source_freq,
        "timestamp": current_time,
        "is_new": True,
    }
    
    for c in state["discovered_clues"]:
        c["is_new"] = False

    state["discovered_clues"].append(new_entry)
    return True


def get_discovered_frequencies(state: Dict[str, Any]) -> List[float]:
    """Return a list of mystery frequencies that have been decoded and logged."""
    found = []
    for clue in state.get("discovered_clues", []):
        freq_str = clue.get("frequency", "")
        for target in REQUIRED_MYSTERY_FREQUENCIES:
            if f"{target:.1f}" in freq_str:
                if target not in found:
                    found.append(target)
    return sorted(found)


def check_investigation_complete(state: Dict[str, Any]) -> bool:
    """Check if all 4 mystery frequencies have been unlocked and documented."""
    found = get_discovered_frequencies(state)
    return len(found) >= len(REQUIRED_MYSTERY_FREQUENCIES)


def get_mystery_progress(state: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve narrative progress telemetry for the mystery."""
    found = get_discovered_frequencies(state)
    return {
        "total_required": len(REQUIRED_MYSTERY_FREQUENCIES),
        "total_discovered": len(found),
        "discovered_frequencies": found,
        "is_complete": len(found) >= len(REQUIRED_MYSTERY_FREQUENCIES),
    }


def record_player_decision(state: Dict[str, Any], decision_key: str) -> bool:
    """Record player's final decision for the ending."""
    if decision_key in ENDINGS:
        state["chosen_ending"] = decision_key
        return True
    return False

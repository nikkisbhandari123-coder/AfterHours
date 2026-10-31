"""
story.py - Narrative, Signal Telemetry & Frequency Database for AfterHours

Manages:
- The 4 known mystery radio stations (88.1, 91.7, 103.4, 107.9 MHz)
- Dynamic proximity-based signal strength detection across 80.0 - 110.0 MHz
- Distorted fragment spillover on fringe frequencies
- Clandestine carrier locking rules
- Persistent clue notebook state with duplicate prevention
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import math
import html

# -------------------------------------------------------------------
# Known Radio Stations (80.0 to 110.0 MHz)
# -------------------------------------------------------------------
RADIO_STATIONS: Dict[float, Dict[str, Any]] = {
    88.1: {
        "name": "Blackwood Weather Broadcast (K-MIST Automated)",
        "callsign": "K-MIST 88.1",
        "category": "Weather Alert",
        "description": "Continuous automated barometric updates and mountain civil weather warnings.",
        "transmission": (
            "[Automated Weather Beacon] ...Blackwood valley weather bulletin at 02:40 AM. "
            "Barometric pressure plunging rapidly over the mountain pass. Dense, unclassified freezing fog "
            "is descending into the lower basin. All motorists are advised that Blackwood Ridge roads are impassable. "
            "Do not stop for flickering lantern lights along the tree line..."
        ),
        "distorted_fragment": (
            "...*kzz-hiss*... [CARRIER BLEED FROM K-MIST 88.1] ...'...barometric pressure plunging... "
            "freezing fog descending... do not stop for lantern lights...'... *static wave washes over signal*..."
        ),
        "clue": "Weather alert reports an unnatural barometric plunge and strange lantern lights along Blackwood Ridge.",
        "base_strength": 94,
    },
    91.7: {
        "name": "Civil Defense Emergency Transmission",
        "callsign": "CD-ALERT 91.7",
        "category": "Emergency Broadcast",
        "description": "Echoing civil alert siren and looping emergency broadcast protocol.",
        "transmission": (
            "[Civil Defense Siren Loop] ...Emergency transmission priority one. "
            "Evacuation order remains in effect for sectors four through nine. Municipal water contamination "
            "unconfirmed. Stay indoors, extinguish all exterior illumination, and do not open doors for "
            "unverified emergency personnel wearing gas masks..."
        ),
        "distorted_fragment": (
            "...*wailing siren bleed*... [CARRIER BLEED FROM CD-ALERT 91.7] ...'...emergency transmission... "
            "evacuation order for sectors four through nine... extinguish all exterior lights...'... *heavy electrical whine*..."
        ),
        "clue": "Civil Defense issued a high-priority evacuation order for sectors 4 through 9 with orders to black out all lights.",
        "base_strength": 90,
    },
    103.4: {
        "name": "Blackwood County Police Transmission",
        "callsign": "SHERIFF-DISP 103.4",
        "category": "Police Dispatch Archive",
        "description": "Crackling analog police radio repeater playback from the night of October 19, 1984.",
        "transmission": (
            "...*kzzzt*... Dispatch to Unit 6, respond to the old trestle bridge on Route 9. "
            "We have multiple 911 calls reporting abandoned civilian vehicles with doors standing open and headlights on. "
            "Checkpoint Bravo is not responding to radio hails... repeat, Checkpoint Bravo is completely dark... *heavy static burst*..."
        ),
        "distorted_fragment": (
            "...*crackling radio flutter*... [CARRIER BLEED FROM SHERIFF-DISP 103.4] ...'...Dispatch to Unit 6... "
            "abandoned civilian vehicles near trestle bridge... Checkpoint Bravo is dark...'... *burst of heavy RF static*..."
        ),
        "clue": "Sheriff dispatch confirms abandoned civilian cars with headlights on near the Route 9 trestle bridge.",
        "base_strength": 86,
    },
    107.9: {
        "name": "Mysterious Hidden Transmission (Phantom Station Zero)",
        "callsign": "CARRIER-ZERO 107.9",
        "category": "Clandestine Numbers Station",
        "description": "A buried high-frequency shortwave carrier emitting a melodic music box chime and encrypted numbers cipher.",
        "transmission": (
            "...[Music box chime: 4 slow notes]... Four... nineteen... eighty-eight... zero... "
            "[heavy electromagnetic pulse]... 'The floodgates were opened from inside the control room'... "
            "repeat: Four... nineteen... eighty-eight... zero... [chime fades into abyssal static]..."
        ),
        "distorted_fragment": (
            "...[faint music box chime buried in static]... [CARRIER BLEED FROM CARRIER-ZERO 107.9] ...'...four... "
            "nineteen... eighty-eight... floodgates were opened...'... *pulse tone drops into silence*..."
        ),
        "clue": "Hidden cipher 4-19-88-0 confirms the valley floodgates were deliberately opened from inside the control room.",
        "base_strength": 80,
    },
}

KNOWN_FREQUENCIES: List[float] = sorted(list(RADIO_STATIONS.keys()))
SUPPORTED_FREQUENCIES: List[float] = KNOWN_FREQUENCIES

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
    
    Args:
        freq: Active position of the dial slider (80.0 to 110.0 MHz)
        is_locked: Whether the receiver currently holds a carrier lock
        locked_freq: The frequency that was locked
        
    Returns:
        Dict containing signal telemetry, status label, strength bars/percent,
        transmission content, and clue availability.
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

    # -------------------------------------------------------------
    # 1. Dynamic Signal Strength Calculation
    # -------------------------------------------------------------
    # Strength ramps up smoothly as player approaches an active frequency
    if min_dist <= 0.1:
        # At or right beside the carrier peak: 85% to 94%
        signal_percent = int(closest_station["base_strength"] - (min_dist * 40))
    elif min_dist <= 0.4:
        # Near carrier (distorted bleed zone): 45% to 75%
        ratio = (0.4 - min_dist) / 0.3  # 0.0 to 1.0
        signal_percent = int(45 + ratio * 30)
    elif min_dist <= 0.8:
        # Faint carrier detection zone: 18% to 40%
        ratio = (0.8 - min_dist) / 0.4  # 0.0 to 1.0
        signal_percent = int(18 + ratio * 22)
    else:
        # Dead air / static noise: 5% to 12%
        seed = int(freq * 10)
        signal_percent = max(5, int(abs(math.sin(seed * 0.7)) * 12))

    # Signal bars (0 to 5)
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

    # -------------------------------------------------------------
    # 2. Transmission & Status Logic
    # -------------------------------------------------------------
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
    default_freq = 80.0  # Start at beginning of spectrum for manual exploration

    return {
        "active_frequency": default_freq,
        "locked_frequency": None,
        "is_locked": False,
        "lock_feedback": None,
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
    
    Returns:
        True if a new clue was added, False if it was already known.
    """
    if not clue_text:
        return False
    
    # Check for existing clue text to strictly prevent duplicates
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
    
    # Mark older clues as not new
    for c in state["discovered_clues"]:
        c["is_new"] = False

    state["discovered_clues"].append(new_entry)
    return True

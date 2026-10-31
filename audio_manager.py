"""
audio_manager.py - Atmospheric Radio Audio System for AfterHours

Manages:
- Procedural synthesis of vintage analog shortwave radio sound effects:
  * Atmospheric dead air static, pink noise, and 60Hz vacuum tube mains hum
  * Heterodyne whistles, carrier whine, and increasing RF interference near stations
  * Mechanical relay click and dual-tone carrier lock chime
  * Subtle analog tuning dial friction / capacitor sweep
  * Station-specific procedural radio audio signatures (EAS alarm, weather tone, repeater squelch, music box)
- Optional ElevenLabs AI voice narration for the 4 canonical broadcasts:
  * 88.1 MHz: Weather broadcast (automated meteorological bulletin)
  * 91.7 MHz: Civil Defense emergency broadcast (urgent civil defense alarm)
  * 103.4 MHz: Police dispatch (VHF analog repeater archive)
  * 107.9 MHz: Station Zero (cryptic numbers cipher with music box chime)
- Disk and memory caching of generated audio to prevent redundant API calls
- Graceful offline fallback to procedural radio audio if ElevenLabs is unconfigured or unavailable
- Master mute/unmute, volume scaling, and independent ambience/voice volume controls
"""

import os
import io
import math
import wave
import struct
import random
import json
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional

# Base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_ASSETS_DIR = os.path.join(BASE_DIR, "assets", "audio")
NARRATION_CACHE_DIR = os.path.join(AUDIO_ASSETS_DIR, "narration")

# Audio file paths
STATIC_DEAD_AIR_PATH = os.path.join(AUDIO_ASSETS_DIR, "static_dead_air.wav")
CARRIER_FRINGE_PATH = os.path.join(AUDIO_ASSETS_DIR, "carrier_fringe.wav")
CARRIER_LOCK_PATH = os.path.join(AUDIO_ASSETS_DIR, "carrier_lock.wav")
DIAL_TUNING_PATH = os.path.join(AUDIO_ASSETS_DIR, "dial_tuning.wav")

STATION_TONE_PATHS = {
    88.1: os.path.join(AUDIO_ASSETS_DIR, "station_88_1.wav"),
    91.7: os.path.join(AUDIO_ASSETS_DIR, "station_91_7.wav"),
    103.4: os.path.join(AUDIO_ASSETS_DIR, "station_103_4.wav"),
    107.9: os.path.join(AUDIO_ASSETS_DIR, "station_107_9.wav"),
}

# In-memory cache for procedural WAV bytes (unscaled)
_WAV_CACHE: Dict[str, bytes] = {}

# ElevenLabs voice IDs for the 4 canonical broadcasts (configurable via env vars)
DEFAULT_ELEVENLABS_VOICES = {
    88.1: os.environ.get("ELEVENLABS_VOICE_88_1", "pNInz6obpgDQGcFmaJgB"),   # Adam / Weather Alert
    91.7: os.environ.get("ELEVENLABS_VOICE_91_7", "IdpQG28K9yA2X07vN7j1"),   # Marcus / Civil Defense EAS
    103.4: os.environ.get("ELEVENLABS_VOICE_103_4", "IKne3meq5aSn9XLyUdCD"),  # Charlie / Police Dispatch
    107.9: os.environ.get("ELEVENLABS_VOICE_107_9", "XB0fDUnXU5ikZZmDhAnM"),  # Charlotte / Station Zero Cipher
}


# ===================================================================
# Procedural Audio Synthesis (Pure Python, Zero External Dependencies)
# ===================================================================

def _make_wav_bytes(samples: List[float], sample_rate: int = 22050) -> bytes:
    """Pack a list of float audio samples (-1.0 to 1.0) into 16-bit mono WAV bytes."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        raw_frames = bytearray()
        for s in samples:
            val = max(-32767, min(32767, int(s * 32767)))
            raw_frames.extend(struct.pack("<h", val))
        w.writeframes(raw_frames)
    return buf.getvalue()


def scale_wav_volume(wav_bytes: bytes, volume_factor: float) -> bytes:
    """
    Scale the amplitude of a 16-bit PCM WAV in pure Python.
    volume_factor: 0.0 (silent) to 1.0 (full volume).
    """
    vol = max(0.0, min(1.0, float(volume_factor)))
    in_buf = io.BytesIO(wav_bytes)

    try:
        with wave.open(in_buf, "rb") as r:
            n_frames = r.getnframes()
            rate = r.getframerate()
            n_channels = r.getnchannels()
            width = r.getsampwidth()
            raw_data = r.readframes(n_frames)

        if vol <= 0.001:
            out_buf = io.BytesIO()
            with wave.open(out_buf, "wb") as w:
                w.setnchannels(n_channels)
                w.setsampwidth(width)
                w.setframerate(rate)
                w.writeframes(b"\x00" * (n_frames * n_channels * width))
            return out_buf.getvalue()

        total_samples = n_frames * n_channels
        fmt = f"<{total_samples}h"
        samples = struct.unpack(fmt, raw_data)
        scaled = [max(-32767, min(32767, int(s * vol))) for s in samples]
        scaled_data = struct.pack(fmt, *scaled)

        out_buf = io.BytesIO()
        with wave.open(out_buf, "wb") as w:
            w.setnchannels(n_channels)
            w.setsampwidth(width)
            w.setframerate(rate)
            w.writeframes(scaled_data)
        return out_buf.getvalue()
    except Exception:
        return wav_bytes


def synth_dead_air_static(duration: float = 2.5, sample_rate: int = 22050) -> bytes:
    """
    Synthesize authentic analog radio static:
    Filtered pink noise + 60Hz mains transformer hum + 120Hz harmonic + random tube crackles.
    """
    samples = []
    last_pink = 0.0
    total_samples = int(duration * sample_rate)

    for i in range(total_samples):
        t = i / sample_rate
        # Lowpass filtered pink noise
        white = random.uniform(-1.0, 1.0)
        pink = (last_pink * 0.90) + (white * 0.10)
        last_pink = pink

        # 60Hz mains hum + 120Hz secondary harmonic
        hum60 = math.sin(2 * math.pi * 60.0 * t) * 0.08
        hum120 = math.sin(2 * math.pi * 120.0 * t) * 0.03

        # Intermittent vacuum tube crackle
        crackle = (random.random() < 0.0015) * random.uniform(-0.5, 0.5)

        sample = (pink * 0.40 + hum60 + hum120 + crackle) * 0.55
        samples.append(sample)

    return _make_wav_bytes(samples, sample_rate)


def synth_fringe_interference(duration: float = 2.5, sample_rate: int = 22050) -> bytes:
    """
    Synthesize RF carrier bleed / fringe interference:
    Heterodyne beat whistle (~1100Hz with subtle frequency drift) + amplitude flutter + static.
    """
    samples = []
    total_samples = int(duration * sample_rate)

    for i in range(total_samples):
        t = i / sample_rate
        # Heterodyne whine with frequency drift
        drift_freq = 1150.0 + 120.0 * math.sin(2 * math.pi * 0.7 * t)
        whine = math.sin(2 * math.pi * drift_freq * t) * 0.22

        # Squelch and amplitude warble
        wobble = 0.7 + 0.3 * math.sin(2 * math.pi * 4.0 * t)

        # Background noise
        noise = random.uniform(-0.25, 0.25)

        sample = (whine * wobble + noise) * 0.55
        samples.append(sample)

    return _make_wav_bytes(samples, sample_rate)


def synth_carrier_lock(duration: float = 0.8, sample_rate: int = 22050) -> bytes:
    """
    Synthesize carrier lock confirmation:
    Mechanical relay click impulse followed by a dual-tone resonant chime (587Hz to 880Hz).
    """
    samples = []
    total_samples = int(duration * sample_rate)

    for i in range(total_samples):
        t = i / sample_rate
        env = math.exp(-t * 5.0)

        # Crisp relay click impulse
        click = (random.uniform(-0.6, 0.6) * math.exp(-t * 60.0))

        # Dual tone resonant chime (D5 587.33Hz + A5 880Hz)
        chime1 = math.sin(2 * math.pi * 587.33 * t) * 0.35
        chime2 = math.sin(2 * math.pi * 880.00 * t) * 0.35

        sample = (click + chime1 + chime2) * env * 0.65
        samples.append(sample)

    return _make_wav_bytes(samples, sample_rate)


def synth_dial_tuning(duration: float = 0.3, sample_rate: int = 22050) -> bytes:
    """
    Synthesize subtle analog capacitor tuning dial friction:
    Short bandpass sweep and mechanical ceramic friction scrape.
    """
    samples = []
    total_samples = int(duration * sample_rate)

    for i in range(total_samples):
        t = i / sample_rate
        env = math.sin(math.pi * (t / duration))  # Bell curve envelope
        scrape = random.uniform(-0.4, 0.4)
        sweep = math.sin(2 * math.pi * (800.0 + 1600.0 * (t / duration)) * t) * 0.15
        sample = (scrape + sweep) * env * 0.45
        samples.append(sample)

    return _make_wav_bytes(samples, sample_rate)


def synth_station_tone(station_key: str, duration: float = 3.5, sample_rate: int = 22050) -> bytes:
    """
    Synthesize authentic procedural radio signatures for canonical broadcasts
    when ElevenLabs voice narration is not enabled or offline.
    """
    samples = []
    total_samples = int(duration * sample_rate)

    if station_key == "weather":
        # 88.1 Weather: 1050Hz NOAA alert beeps (0.4s beep, 0.2s pause) + high-frequency telemetry hiss
        for i in range(total_samples):
            t = i / sample_rate
            beep_gate = 1.0 if (t % 0.6) < 0.4 else 0.0
            beep = math.sin(2 * math.pi * 1050.0 * t) * beep_gate * 0.30
            hiss = random.uniform(-0.08, 0.08)
            samples.append((beep + hiss) * 0.6)

    elif station_key == "defense":
        # 91.7 Civil Defense: EAS two-tone alert (853Hz + 960Hz) + wailing klaxon
        for i in range(total_samples):
            t = i / sample_rate
            eas = (math.sin(2 * math.pi * 853.0 * t) * 0.20 + math.sin(2 * math.pi * 960.0 * t) * 0.20)
            siren_freq = 550.0 + 220.0 * math.sin(2 * math.pi * 0.9 * t)
            siren = math.sin(2 * math.pi * siren_freq * t) * 0.18
            samples.append((eas + siren) * 0.6)

    elif station_key == "police":
        # 103.4 Police: VHF repeater squelch tone (1209Hz) + crackling radio dispatch preamble
        for i in range(total_samples):
            t = i / sample_rate
            chirp_env = math.exp(-((t - 0.2) ** 2) / 0.015)
            chirp = math.sin(2 * math.pi * 1209.0 * t) * chirp_env * 0.45
            hiss = random.uniform(-0.15, 0.15) * (0.8 if t < 2.8 else 0.1)
            samples.append((chirp + hiss) * 0.6)

    elif station_key == "truth":
        # 107.9 Station Zero: Eerie 4-note music box sequence (E5, B4, G4, E4) + 38Hz subterranean pulse
        notes = [659.25, 493.88, 392.00, 329.63]
        for i in range(total_samples):
            t = i / sample_rate
            note_idx = int(t / 0.8) % len(notes)
            note_t = t % 0.8
            freq = notes[note_idx]
            env = math.exp(-note_t * 4.0)
            chime = (
                math.sin(2 * math.pi * freq * note_t) * 0.35
                + math.sin(2 * math.pi * freq * 2.0 * note_t) * 0.12
            ) * env
            sub_pulse = math.sin(2 * math.pi * 38.0 * t) * 0.12
            samples.append((chime + sub_pulse) * 0.6)

    else:
        # Generic carrier hum
        for i in range(total_samples):
            t = i / sample_rate
            carrier = math.sin(2 * math.pi * 440.0 * t) * 0.15 + random.uniform(-0.1, 0.1)
            samples.append(carrier * 0.5)

    return _make_wav_bytes(samples, sample_rate)


# ===================================================================
# Audio Asset Storage & Pre-generation
# ===================================================================

def ensure_audio_assets() -> None:
    """
    Ensure all default procedural audio assets exist on disk in assets/audio/
    and load them into the in-memory cache for 0ms lookup latency.
    """
    os.makedirs(AUDIO_ASSETS_DIR, exist_ok=True)
    os.makedirs(NARRATION_CACHE_DIR, exist_ok=True)

    asset_map = [
        ("STATIC", STATIC_DEAD_AIR_PATH, synth_dead_air_static),
        ("FRINGE", CARRIER_FRINGE_PATH, synth_fringe_interference),
        ("LOCK", CARRIER_LOCK_PATH, synth_carrier_lock),
        ("TUNING", DIAL_TUNING_PATH, synth_dial_tuning),
        ("STATION_88_1", STATION_TONE_PATHS[88.1], lambda: synth_station_tone("weather")),
        ("STATION_91_7", STATION_TONE_PATHS[91.7], lambda: synth_station_tone("defense")),
        ("STATION_103_4", STATION_TONE_PATHS[103.4], lambda: synth_station_tone("police")),
        ("STATION_107_9", STATION_TONE_PATHS[107.9], lambda: synth_station_tone("truth")),
    ]

    for key, path, synth_func in asset_map:
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            try:
                data = synth_func()
                with open(path, "wb") as f:
                    f.write(data)
                _WAV_CACHE[key] = data
            except Exception:
                pass
        else:
            if key not in _WAV_CACHE:
                try:
                    with open(path, "rb") as f:
                        _WAV_CACHE[key] = f.read()
                except Exception:
                    pass


def get_cached_sfx(sfx_key: str) -> bytes:
    """Retrieve raw procedural audio bytes by key from memory cache or disk."""
    if sfx_key in _WAV_CACHE:
        return _WAV_CACHE[sfx_key]

    ensure_audio_assets()
    return _WAV_CACHE.get(sfx_key, b"")


# ===================================================================
# ElevenLabs Broadcast Voice Narration Integration
# ===================================================================

def check_elevenlabs_configured() -> bool:
    """Check if an ElevenLabs API key is configured in the environment."""
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    return bool(key)


def get_elevenlabs_status() -> Dict[str, Any]:
    """Return status telemetry for ElevenLabs voice narration."""
    configured = check_elevenlabs_configured()
    cached_stations = []
    for freq in (88.1, 91.7, 103.4, 107.9):
        cache_file = os.path.join(NARRATION_CACHE_DIR, f"station_{int(freq * 10)}.mp3")
        if os.path.exists(cache_file) and os.path.getsize(cache_file) > 0:
            cached_stations.append(freq)

    return {
        "configured": configured,
        "cached_stations": cached_stations,
        "total_cached": len(cached_stations),
    }


def fetch_elevenlabs_narration(
    frequency: float,
    canonical_text: str,
    voice_id: Optional[str] = None,
    api_key: Optional[str] = None,
    timeout: float = 12.0,
) -> Optional[bytes]:
    """
    Fetch voice narration for a canonical station using ElevenLabs API.
    Caches the returned MP3 audio to disk to prevent redundant API credit usage.
    Returns None if ElevenLabs is unconfigured, offline, or returns an error.
    """
    os.makedirs(NARRATION_CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(NARRATION_CACHE_DIR, f"station_{int(frequency * 10)}.mp3")

    # 1. Return from disk cache if already generated
    if os.path.exists(cache_file) and os.path.getsize(cache_file) > 0:
        try:
            with open(cache_file, "rb") as f:
                return f.read()
        except Exception:
            pass

    # 2. Check API key
    key = (api_key or os.environ.get("ELEVENLABS_API_KEY", "")).strip()
    if not key:
        return None

    active_voice = voice_id or DEFAULT_ELEVENLABS_VOICES.get(round(frequency, 1), "pNInz6obpgDQGcFmaJgB")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{active_voice}?output_format=mp3_44100_128"

    payload = {
        "text": canonical_text,
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {
            "stability": 0.55,
            "similarity_boost": 0.75,
            "style": 0.35,
            "use_speaker_boost": True,
        },
    }

    try:
        encoded_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=encoded_data,
            headers={
                "xi-api-key": key,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg",
                "User-Agent": "AfterHours-Radio/1.0",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                audio_bytes = resp.read()
                if audio_bytes and len(audio_bytes) > 200:
                    with open(cache_file, "wb") as f:
                        f.write(audio_bytes)
                    return audio_bytes
    except Exception:
        return None

    return None


def get_station_narration(
    frequency: float,
    station_key: str,
    canonical_text: str,
    force_generate: bool = False,
) -> Dict[str, Any]:
    """
    Retrieve audio for a canonical station:
    1. ElevenLabs voice narration if cached or API key configured.
    2. Fallback to procedural radio audio signature if ElevenLabs is unavailable.
    """
    freq = round(frequency, 1)
    cache_file = os.path.join(NARRATION_CACHE_DIR, f"station_{int(freq * 10)}.mp3")

    # Check cached ElevenLabs narration
    if os.path.exists(cache_file) and os.path.getsize(cache_file) > 0:
        try:
            with open(cache_file, "rb") as f:
                return {
                    "available": True,
                    "audio_bytes": f.read(),
                    "format": "audio/mp3",
                    "source": "ELEVENLABS_CACHE",
                    "label": "ELEVENLABS VOICE NARRATION (CACHED)",
                    "is_ai_voice": True,
                }
        except Exception:
            pass

    # If force generate requested and ElevenLabs configured
    if force_generate and check_elevenlabs_configured():
        ai_bytes = fetch_elevenlabs_narration(freq, canonical_text)
        if ai_bytes:
            return {
                "available": True,
                "audio_bytes": ai_bytes,
                "format": "audio/mp3",
                "source": "ELEVENLABS_API",
                "label": "ELEVENLABS VOICE NARRATION (LIVE)",
                "is_ai_voice": True,
            }

    # Fallback to procedural station radio tone
    sfx_key = f"STATION_{int(freq * 10)}"
    fallback_wav = get_cached_sfx(sfx_key)
    if not fallback_wav:
        fallback_wav = synth_station_tone(station_key)

    return {
        "available": True,
        "audio_bytes": fallback_wav,
        "format": "audio/wav",
        "source": "PROCEDURAL_BEACON",
        "label": "PROCEDURAL RADIO AUDIO SIGNATURE",
        "is_ai_voice": False,
    }


# ===================================================================
# Audio Controller for Streamlit Integration
# ===================================================================

def resolve_radio_audio_track(
    telemetry: Dict[str, Any],
    is_carrier_lock_event: bool = False,
    is_playing_narration: bool = False,
    master_volume: float = 0.70,
    ambience_volume: float = 0.60,
    voice_volume: float = 0.85,
) -> Optional[Dict[str, Any]]:
    """
    Determine the appropriate audio track and scale its volume for the current game state:
    - Carrier lock chime on lock event
    - Voice narration or station tone when locked and requested
    - Low carrier hum when locked and idle
    - Increasing interference on fringe bleed
    - Atmospheric static on dead air
    """
    ensure_audio_assets()
    effective_ambience_vol = master_volume * ambience_volume
    effective_voice_vol = master_volume * voice_volume

    # 1. Carrier Lock Event (plays short 0.8s lock confirmation chime)
    if is_carrier_lock_event:
        raw_lock = get_cached_sfx("LOCK")
        scaled_lock = scale_wav_volume(raw_lock, master_volume * 0.80)
        return {
            "type": "LOCK_CHIME",
            "name": "CARRIER LOCK CONFIRMATION",
            "format": "audio/wav",
            "audio_bytes": scaled_lock,
            "loop": False,
            "label": "[*] CARRIER LOCKED // TONE CONFIRMED",
        }

    # 2. Station Locked
    if telemetry.get("is_locked"):
        freq = telemetry.get("target_freq") or 88.1
        # If user explicitly requested broadcast narration playback
        if is_playing_narration:
            canonical_text = telemetry.get("transmission", "")
            station_key = "weather"
            if freq == 91.7:
                station_key = "defense"
            elif freq == 103.4:
                station_key = "police"
            elif freq == 107.9:
                station_key = "truth"

            narration_info = get_station_narration(freq, station_key, canonical_text)
            audio_bytes = narration_info["audio_bytes"]
            # If WAV, apply volume scaling
            if narration_info["format"] == "audio/wav":
                audio_bytes = scale_wav_volume(audio_bytes, effective_voice_vol)

            return {
                "type": "NARRATION",
                "name": f"BROADCAST NARRATION ({freq:.1f} MHz)",
                "format": narration_info["format"],
                "audio_bytes": audio_bytes,
                "loop": False,
                "label": narration_info["label"],
            }
        else:
            # Low carrier hum when locked but narration not playing
            raw_sfx = get_cached_sfx(f"STATION_{int(freq * 10)}")
            scaled_hum = scale_wav_volume(raw_sfx, effective_ambience_vol * 0.45)
            return {
                "type": "CARRIER_IDLE",
                "name": f"STABLE CARRIER HUM ({freq:.1f} MHz)",
                "format": "audio/wav",
                "audio_bytes": scaled_hum,
                "loop": True,
                "label": "[*] CARRIER PHASE-LOCKED // IDLE",
            }

    # 3. Carrier Bleed / Fringe Frequency
    if telemetry.get("status") in ("SIGNAL BLEED", "CARRIER DETECTED"):
        raw_fringe = get_cached_sfx("FRINGE")
        scaled_fringe = scale_wav_volume(raw_fringe, effective_ambience_vol)
        return {
            "type": "FRINGE",
            "name": "RF HETERODYNE INTERFERENCE",
            "format": "audio/wav",
            "audio_bytes": scaled_fringe,
            "loop": True,
            "label": "[~] CARRIER BLEED // HETERODYNE DRIFT",
        }

    # 4. Dead Air / Unknown Frequency
    raw_static = get_cached_sfx("STATIC")
    scaled_static = scale_wav_volume(raw_static, effective_ambience_vol)
    return {
        "type": "STATIC",
        "name": "ATMOSPHERIC SHORTWAVE STATIC",
        "format": "audio/wav",
        "audio_bytes": scaled_static,
        "loop": True,
        "label": "[o] DEAD AIR STATIC // 60Hz MAINS HUM",
    }

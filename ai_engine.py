"""
ai_engine.py - Local Ollama Gemma AI Integration for AfterHours

Manages:
- Detection and connection to local Ollama API (http://localhost:11434)
- Auto-discovery of installed local Gemma models (e.g., gemma3:4b, gemma4:e2b)
- Configurable model selection via environment variable OLLAMA_MODEL
- Generation of atmospheric radio interference, distorted voice fragments,
  mysterious background transmissions, and contextual ambient whispers
- Strict story protection: canonical story broadcasts, clues, and endings are NEVER overwritten
- Fast caching and reasonable request timeouts to prevent freezing the UI
- Seamless deterministic Python fallback when Ollama is offline or unavailable
"""

import os
import json
import time
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional

# Configuration defaults
DEFAULT_OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
CONFIGURED_MODEL = os.environ.get("OLLAMA_MODEL", None)
DEFAULT_TIMEOUT = float(os.environ.get("OLLAMA_TIMEOUT", "25.0"))

# In-memory cache for generated ambient snippets (keyed by f"{freq:.1f}-{clues_count}")
_SNIPPET_CACHE: Dict[str, str] = {}

# Cached status for Ollama connection to avoid pinging API on every render
_STATUS_CACHE: Dict[str, Any] = {
    "checked_at": 0.0,
    "available": False,
    "model": None,
    "all_models": [],
}


def check_ollama_service(host: str = DEFAULT_OLLAMA_HOST, cache_ttl: float = 10.0) -> Dict[str, Any]:
    """
    Check if the local Ollama daemon is running and identify available Gemma models.
    Caches availability status for `cache_ttl` seconds to maintain UI responsiveness.
    """
    now = time.time()
    if now - _STATUS_CACHE["checked_at"] < cache_ttl and _STATUS_CACHE["model"] is not None:
        return _STATUS_CACHE

    _STATUS_CACHE["checked_at"] = now
    url = f"{host.rstrip('/')}/api/tags"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AfterHours-Radio/1.0"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                models = [m.get("name", "") for m in data.get("models", [])]
                _STATUS_CACHE["all_models"] = models

                # Identify Gemma model:
                # 1. Configured via environment variable if present in installed models
                # 2. Prefer gemma3:4b (fastest local gemma)
                # 3. Any model with "gemma" in its name
                chosen_model = None
                if CONFIGURED_MODEL:
                    for m in models:
                        if CONFIGURED_MODEL.lower() in m.lower():
                            chosen_model = m
                            break

                if not chosen_model:
                    # Prefer gemma3:4b
                    for m in models:
                        if "gemma3" in m.lower() and "4b" in m.lower():
                            chosen_model = m
                            break

                if not chosen_model:
                    # Any gemma
                    for m in models:
                        if "gemma" in m.lower():
                            chosen_model = m
                            break

                _STATUS_CACHE["available"] = (chosen_model is not None)
                _STATUS_CACHE["model"] = chosen_model
                return _STATUS_CACHE
    except Exception:
        pass

    _STATUS_CACHE["available"] = False
    _STATUS_CACHE["model"] = None
    return _STATUS_CACHE


def get_cached_ambient(frequency: float, clues_count: int = 0) -> Optional[str]:
    """Retrieve a previously generated ambient snippet from memory cache."""
    freq_key = f"{frequency:.1f}-{clues_count}"
    return _SNIPPET_CACHE.get(freq_key)


def cache_ambient(frequency: float, clues_count: int, content: str) -> None:
    """Store an ambient snippet in memory cache."""
    freq_key = f"{frequency:.1f}-{clues_count}"
    _SNIPPET_CACHE[freq_key] = content


def clear_snippet_cache() -> None:
    """Clear the snippet cache (useful for testing)."""
    _SNIPPET_CACHE.clear()


def query_ollama_gemma(
    prompt: str,
    system_instruction: str,
    model_name: Optional[str] = None,
    timeout: float = DEFAULT_TIMEOUT,
    max_tokens: int = 18,
    host: str = DEFAULT_OLLAMA_HOST,
) -> Optional[str]:
    """
    Send a prompt to the local Gemma model with strict limits and timeouts.
    Returns None if Ollama fails, times out, or is offline.
    """
    status = check_ollama_service(host=host)
    if not status["available"]:
        return None

    active_model = model_name or status["model"]
    if not active_model:
        return None

    url = f"{host.rstrip('/')}/api/generate"
    payload = {
        "model": active_model,
        "prompt": prompt,
        "system": system_instruction,
        "stream": False,
        "options": {
            "num_ctx": 512,
            "num_predict": max_tokens,
            "temperature": 0.75,
            "top_k": 40,
            "top_p": 0.9,
            "stop": ["\n\n", "User:", "Assistant:", "Note:", "Human:"],
        },
    }

    try:
        encoded_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=encoded_data,
            headers={"Content-Type": "application/json", "User-Agent": "AfterHours-Radio/1.0"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                res_json = json.loads(resp.read().decode("utf-8"))
                response_text = res_json.get("response", "").strip()
                if response_text:
                    # Clean conversational artifacts and extra quotes
                    cleaned = response_text.replace('"', "").replace("\n", " ").strip()
                    # Strip any repetitive preamble
                    if cleaned.lower().startswith("here is"):
                        parts = cleaned.split(":", 1)
                        if len(parts) > 1:
                            cleaned = parts[1].strip()
                    return cleaned
    except Exception:
        return None

    return None


# -------------------------------------------------------------------
# Specialized Generators for the 4 AI Content Types
# -------------------------------------------------------------------

RADIO_SYSTEM_PROMPT = (
    "You are an analog shortwave radio receiver in 1984 Blackwood Valley. "
    "Output ONLY 1 short sentence of atmospheric radio noise, distorted speech fragments, or tape hiss. "
    "Use vintage radio audio sound cues like ...*kzzzt*..., ...*tape flutter*..., [low hum], or *static wash*. "
    "STRICT RULES: Do NOT say okay, do NOT greet, do NOT explain yourself. "
    "Do NOT invent official clues or solve the mystery. Output raw radio audio only."
)


def generate_atmospheric_interference(
    frequency: float,
    model_name: Optional[str] = None,
    host: str = DEFAULT_OLLAMA_HOST,
) -> Optional[str]:
    """1. Generate atmospheric radio interference messages (static, tape flutter, 60Hz hum)."""
    prompt = (
        f"Generate 1 short atmospheric soundbite of analog radio interference and vacuum tube noise "
        f"on dead frequency {frequency:.1f} MHz. Include audio sound cues like *kzzzt*, [electrical hum], or *tape hiss*."
    )
    return query_ollama_gemma(prompt=prompt, system_instruction=RADIO_SYSTEM_PROMPT, model_name=model_name, host=host)


def generate_distorted_voice_fragment(
    frequency: float,
    nearest_station_name: str,
    model_name: Optional[str] = None,
    host: str = DEFAULT_OLLAMA_HOST,
) -> Optional[str]:
    """2. Generate distorted voice fragments when approaching frequencies (spillover / carrier bleed)."""
    prompt = (
        f"Generate 1 short distorted voice fragment on frequency {frequency:.1f} MHz, "
        f"bleeding over from '{nearest_station_name}'. Words should be half-swallowed by heavy static and frequency drift."
    )
    return query_ollama_gemma(prompt=prompt, system_instruction=RADIO_SYSTEM_PROMPT, model_name=model_name, host=host)


def generate_mysterious_transmission(
    frequency: float,
    clues_count: int = 0,
    model_name: Optional[str] = None,
    host: str = DEFAULT_OLLAMA_HOST,
) -> Optional[str]:
    """3. Generate short mysterious background transmissions (phantom signals, eerie midnight numbers)."""
    prompt = (
        f"Generate 1 short mysterious shortwave transmission on dead frequency {frequency:.1f} MHz. "
        f"It could be an eerie repeating cipher, a phantom callsign, or a distant voice buried in tape flutter."
    )
    return query_ollama_gemma(prompt=prompt, system_instruction=RADIO_SYSTEM_PROMPT, model_name=model_name, host=host)


def generate_contextual_ambient(
    frequency: float,
    clues_count: int,
    model_name: Optional[str] = None,
    host: str = DEFAULT_OLLAMA_HOST,
) -> Optional[str]:
    """4. Generate contextual ambient messages based on tuned frequency and discovered clues."""
    if clues_count == 0:
        context_hint = "Midnight mountain silence, cold autumn fog, lonely valley."
    elif clues_count == 1:
        context_hint = "Rising barometric fog, strange flickering lantern lights reported in the tree line."
    elif clues_count == 2:
        context_hint = "Echoing civil defense sirens in the far distance, military cordons along the perimeter."
    elif clues_count == 3:
        context_hint = "Abandoned civilian cars with headlights on, rumors of pre-planned evacuation orders."
    else:
        context_hint = "The valley floodgates were deliberately opened, waters rising over buried secrets."

    prompt = (
        f"Generate 1 short ambient radio transmission fragment on frequency {frequency:.1f} MHz. "
        f"Context: {context_hint}. Reflect this haunted atmosphere with audio crackle and tape flutter."
    )
    return query_ollama_gemma(prompt=prompt, system_instruction=RADIO_SYSTEM_PROMPT, model_name=model_name, host=host)


# -------------------------------------------------------------------
# Deterministic Python Fallback Content
# -------------------------------------------------------------------

FALLBACK_ATMOSPHERIC_STATIC: List[str] = [
    "...*shhhhhhh*... [faint crackle of magnetic tape spooling] ...*whirrrrr*... *pop*...",
    "...*kzzzt*... '...is anyone still listening on this band?... please...' ...*heavy static wash*...",
    "...[low 60Hz electrical hum vibrating through receiver vacuum tubes]... *intermittent click*...",
    "...*crackle*... [echoing strains of a 1940s ballroom waltz buried beneath white noise] ...*fade out*...",
    "...*bzzzzzt*... [faint Morse code tone: · · · — — — · · · ] ...*static pop*...",
    "...*hsssss*... '...do not look toward the mountain ridge...' ...*electronic screech*...",
    "...*flutter*... [faint synthetic chime loops under deep carrier hum] ...*click*...",
    "...*crackle*... '...water is rising past the marker stones...' ...*carrier fade*...",
]


def get_fallback_ambient(
    frequency: float,
    nearest_station: Optional[Dict[str, Any]] = None,
    dist_to_station: float = 999.0,
) -> str:
    """Return an instant, atmospheric deterministic audio fragment when Ollama is offline or uncached."""
    if dist_to_station <= 0.4 and nearest_station and "distorted_fragment" in nearest_station:
        return nearest_station["distorted_fragment"]

    seed = int(frequency * 10)
    return FALLBACK_ATMOSPHERIC_STATIC[seed % len(FALLBACK_ATMOSPHERIC_STATIC)]


# -------------------------------------------------------------------
# Unified Synthesizer Interface
# -------------------------------------------------------------------

def synthesize_radio_signal(
    frequency: float,
    status_category: str,
    clues_count: int = 0,
    nearest_station: Optional[Dict[str, Any]] = None,
    dist_to_station: float = 999.0,
    force_generate: bool = False,
    model_name: Optional[str] = None,
    host: str = DEFAULT_OLLAMA_HOST,
) -> Dict[str, Any]:
    """
    Unified entry point for atmospheric ambient shortwave synthesis.

    Parameters:
    - frequency: currently tuned frequency
    - status_category: "DEAD AIR", "SIGNAL BLEED", etc.
    - clues_count: number of discovered clues for narrative context
    - nearest_station: station dict if within fringe distance
    - dist_to_station: distance in MHz to closest station
    - force_generate: If True, invokes Ollama Gemma synchronously.
                     If False, checks cache and falls back to deterministic audio
                     to guarantee 0ms slider dragging.
    - model_name: optional override for model name
    - host: optional override for Ollama API endpoint

    Returns:
    {
        "text": formatted audio snippet,
        "source": "GEMMA_AI" | "CACHE" | "FALLBACK",
        "model": model name or None,
    }
    """
    freq_key = f"{frequency:.1f}-{clues_count}"

    # 1. Check in-memory cache for instant return (0ms)
    if freq_key in _SNIPPET_CACHE:
        return {
            "text": _SNIPPET_CACHE[freq_key],
            "source": "CACHE",
            "model": check_ollama_service(host=host).get("model"),
        }

    # 2. If not forcing generation (e.g. continuous slider movement), return instant fallback
    if not force_generate:
        return {
            "text": get_fallback_ambient(frequency, nearest_station, dist_to_station),
            "source": "FALLBACK",
            "model": None,
        }

    # 3. Force generate requested: check if Ollama is available
    status = check_ollama_service(host=host)
    if not status["available"]:
        fallback_text = get_fallback_ambient(frequency, nearest_station, dist_to_station)
        return {
            "text": fallback_text,
            "source": "FALLBACK",
            "model": None,
        }

    active_model = model_name or status["model"]

    # Select appropriate prompt based on RF context and clues
    ai_result = None
    if dist_to_station <= 0.4 and nearest_station:
        # Distorted voice fragment approaching a station
        station_name = nearest_station.get("name", "Emergency Carrier")
        ai_result = generate_distorted_voice_fragment(
            frequency=frequency,
            nearest_station_name=station_name,
            model_name=active_model,
            host=host,
        )
    elif clues_count > 0 and (int(frequency * 10) % 2 == 0):
        # Contextual ambient message reflecting discovered clues
        ai_result = generate_contextual_ambient(
            frequency=frequency,
            clues_count=clues_count,
            model_name=active_model,
            host=host,
        )
    elif int(frequency * 10) % 3 == 0:
        # Mysterious background transmission
        ai_result = generate_mysterious_transmission(
            frequency=frequency,
            clues_count=clues_count,
            model_name=active_model,
            host=host,
        )
    else:
        # Atmospheric radio interference
        ai_result = generate_atmospheric_interference(
            frequency=frequency,
            model_name=active_model,
            host=host,
        )

    if ai_result:
        formatted = f"[GEMMA AI INTERCEPT] {ai_result}"
        _SNIPPET_CACHE[freq_key] = formatted
        return {
            "text": formatted,
            "source": "GEMMA_AI",
            "model": active_model,
        }

    # If Ollama timed out or errored, return fallback
    fallback_text = get_fallback_ambient(frequency, nearest_station, dist_to_station)
    return {
        "text": fallback_text,
        "source": "FALLBACK",
        "model": None,
    }

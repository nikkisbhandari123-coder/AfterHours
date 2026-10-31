# 📻 AfterHours

**AfterHours** is an open-source, AI-powered haunted radio mystery game built with Python and Streamlit.

Tune an analog shortwave receiver across the 80.0 to 110.0 MHz spectrum late into the night. Explore eerie frequencies, encounter electromagnetic interference and phantom carrier waves, piece together clues about the abandoned mountain town of Blackwood, and intercept transmissions from the dark.

---

## 📂 Project Structure & File Guide

```
AfterHours/
├── app.py            # Streamlit web interface, CRT monitor & analog tuner console
├── story.py          # Narrative logic, frequency spectrum telemetry, lore & clues
├── ai_engine.py      # AI persona engine & radio transmission generator
├── audio_manager.py  # Atmospheric radio audio synthesizer & ElevenLabs voice narration
├── assets/           # Audio sound effects, cached narration & title screen artwork
│   └── afterhours_title.png  # Cinematic opening screen backdrop
├── requirements.txt  # Project dependencies (streamlit, python-dotenv)
├── README.md         # Documentation & guide
└── .gitignore        # Git ignore rules for Python & Streamlit
```

### 📄 Detailed File Descriptions

1. **[app.py](file:///c:/Users/nikki/AfterHours/app.py) (Main Application)**:
   - Fullscreen **Cinematic Opening Screen** featuring custom backdrop artwork (`assets/afterhours_title.png`), pixel-perfect responsive `START INVESTIGATION` button alignment, and sequential atmospheric telemetry transition (`SIGNAL DETECTED...` -> `CONNECTING TO BLACKWOOD FREQUENCY...` -> `INVESTIGATION INITIATED.`).
   - Streamlit frontend featuring an abandoned radio station aesthetic (deep black chassis, dark forest green panels, phosphor green text, and vintage amber warnings).
   - Continuous analog dial slider sweeping **80.0 to 110.0 MHz** (precision 0.1 MHz) with large digital readout.
   - Dedicated **Tune / Lock Signal** mechanism with manual dial sweeping for true station discovery.
   - Live receiver telemetry status bar (Power, Band, Tube filaments).
   - Dynamic 5-segment LED signal strength meter reflecting proximity to station carrier waves.
   - Vintage CRT monitor with scanlines, timestamp telemetry, and escaping to ensure clean text display without literal HTML leaks.
   - Investigation evidence notebook recording discovered clues, source frequencies, timestamps, and highlighting new entries.
   - Integrated Receiver Acoustic Monitor & Mixer with master mute switch, volume attenuation, and broadcast narration controls.

2. **[story.py](file:///c:/Users/nikki/AfterHours/story.py) (Narrative & Frequency Telemetry)**:
   - Houses known radio stations:
     - **88.1 MHz**: *Blackwood Weather Broadcast (K-MIST Automated)*
     - **91.7 MHz**: *Civil Defense Emergency Transmission*
     - **103.4 MHz**: *Blackwood County Police Transmission*
     - **107.9 MHz**: *Mysterious Hidden Transmission (Phantom Station Zero)*
   - Dynamic frequency resolution (`resolve_frequency_telemetry`): calculates distance falloff, signal bleeding/interference near known channels, and procedural static/voice fragments on dead air.
   - Clue state management with persistent tracking, timestamping, and source frequency attribution.

3. **[ai_engine.py](file:///c:/Users/nikki/AfterHours/ai_engine.py) (Local Gemma AI Radio Engine)**:
   - Integrates local **Gemma** models using **Ollama**'s HTTP API (`http://localhost:11434`).
   - Automatically detects installed local Gemma models (e.g., `gemma3:4b`).
   - Generates four types of atmospheric content:
     1. Atmospheric radio static and vacuum tube interference.
     2. Distorted voice fragments bleeding over near active stations.
     3. Short mysterious phantom background transmissions.
     4. Contextual ambient messages based on tuned frequency and discovered clues.
   - **Strict Story Protection**: All 4 canonical mystery broadcasts, clues, frequency locks, and branching endings are 100% Python-controlled and can never be altered or overwritten by AI.
   - **Zero-Freeze Caching**: Slider sweeping remains instant (0ms) using in-memory response caching and instant deterministic Python audio fallbacks if Ollama is offline or times out.

4. **[audio_manager.py](file:///c:/Users/nikki/AfterHours/audio_manager.py) (Atmospheric Radio Audio System)**:
   - Zero-dependency audio synthesis using standard library `wave` and `struct` producing 16-bit 22,050Hz mono audio.
   - Procedural sound generation for dead air white noise, 60Hz transformer hum, heterodyne fringe interference, short carrier-lock confirmation chimes, and dial-sweep clicks.
   - Procedural radio station signatures for all 4 canonical stations (NOAA alert tone, EAS dual-tone siren, police repeater squelch bursts, and phantom music box chimes).
   - Optional ElevenLabs Voice Narration integration using `ELEVENLABS_API_KEY` with local disk caching (`assets/audio/narration/`).
   - Pure Python PCM volume attenuation scaling supporting Master, RF Static, and Narration levels without audio clipping.

5. **[requirements.txt](file:///c:/Users/nikki/AfterHours/requirements.txt)**:
   - Defines dependencies (`streamlit`, `python-dotenv`). No external heavyweight ML or audio libraries required.

6. **[.gitignore](file:///c:/Users/nikki/AfterHours/.gitignore)**:
   - Excludes Python bytecode, virtual environments, audio cache artifacts, and scratch tests from Git.

---

## 🤖 Local Gemma AI (Ollama Integration)

AfterHours integrates local Gemma AI via Ollama to synthesize eerie radio interference and contextual shortwave whispers without transmitting any data over the cloud.

### 1. Requirements & Setup
1. Ensure [Ollama](https://ollama.ai) is installed and running on your system:
   ```bash
   ollama list
   ```
2. Verify an installed Gemma model (e.g. `gemma3:4b`):
   ```bash
   ollama run gemma3:4b "echo"
   ```
3. Start the game — AfterHours will automatically detect the running Ollama daemon and the active Gemma model!

### 2. Configuration Options (Environment Variables)
You can configure the AI engine using environment variables in PowerShell or your `.env` file:
```bash
# Model selection (defaults to auto-detected local gemma3:4b)
$env:OLLAMA_MODEL = "gemma3:4b"

# Host address (defaults to http://localhost:11434)
$env:OLLAMA_HOST = "http://localhost:11434"

# Timeout in seconds before falling back to Python static (defaults to 25.0s)
$env:OLLAMA_TIMEOUT = "25.0"
```

### 3. Graceful Offline Fallback
If Ollama is not running or if a generation request times out, the game **continues to work seamlessly** using its built-in procedural Python radio audio synthesizer without freezing the interface. The receiver status bar displays `AI: STANDBY (FALLBACK)` and all canonical broadcasts remain 100% playable.

---

## 🔊 Atmospheric Radio Audio System

AfterHours includes a dedicated, hardware-inspired acoustic subsystem modeled after vintage vacuum-tube shortwave receivers.

### 1. Procedural Radio Sound Effects
- **Dead Air Static**: Authentic white noise with subtle 60Hz/120Hz alternating-current power transformer hum on unallocated frequencies.
- **Heterodyne Fringe Interference**: Dynamic beat frequencies, carrier drift, and squelch flutter that intensify as you approach an active station.
- **Carrier Lock Confirmation**: A resonant dual-tone carrier acknowledgment ping (0.8s) when successfully locking an authentic broadcast.
- **Analog Dial Sweeps**: Subtle tuning clicks and tube reactance when turning the dial across the dial face.
- **Station Audio Signatures**: Custom vintage procedural beacons for all four stations when locked:
  - `88.1 MHz`: Automated NOAA Weather alert tone (1050 Hz) and robotic teletype pulse.
  - `91.7 MHz`: Civil Defense dual-tone EAS siren (853 Hz + 960 Hz emergency alert).
  - `103.4 MHz`: Sheriff repeater roger beep and squelch burst.
  - `107.9 MHz`: Phantom carrier wave with eerie, resonant music box chimes.

### 2. Broadcast Voice Narration (ElevenLabs TTS Integration)
Players can listen to spoken broadcasts for all four canonical transmissions:
- **88.1 MHz**: *K-MIST Automated Weather Broadcast*
- **91.7 MHz**: *Civil Defense Evacuation Advisory*
- **103.4 MHz**: *Blackwood Sheriff Dispatch Transmit*
- **107.9 MHz**: *Phantom Station Zero Numbers Transmission*

#### Setup & API Configuration:
Voice narration uses **ElevenLabs** only when an API key is provided via environment variables or a `.env` file:
```bash
# In your .env file or terminal:
$env:ELEVENLABS_API_KEY = "your-elevenlabs-api-key"

# (Optional) Custom Voice ID Overrides:
$env:ELEVENLABS_VOICE_88_1 = "21m00Tcm4TlvDq8ikWAM"   # Rachel (Weather)
$env:ELEVENLABS_VOICE_91_7 = "ErXwobaYiN019PkySvjV"   # Antoni (Civil Defense)
$env:ELEVENLABS_VOICE_103_4 = "VR6AewLTigWG4xSOukaG"  # Arnold (Police Dispatch)
$env:ELEVENLABS_VOICE_107_9 = "AZnzlk1XvdvUeBnXmlld"  # Domi (Station Zero)
```

#### Privacy & Resilience:
- **No Hardcoded Keys**: API keys are strictly read from environment variables; keys are never logged, printed, or exposed in client bundles.
- **Local Disk Cache**: Audio is automatically cached to `assets/audio/narration/station_{freq}.mp3` upon first fetch, eliminating redundant network calls and quota waste.
- **Graceful Standby Fallback**: If `ELEVENLABS_API_KEY` is not set or network is offline, the game automatically falls back to procedural station audio signatures and pure text without interrupting gameplay.
- **Independent & Optional**: Voice narration is completely optional and can be triggered on demand using the CRT monitor's narration button.

### 3. Receiver Acoustic Console & Volume Controls
Located directly in the tuning console:
- **Speaker Power Switch**: Master toggle (`SPEAKER POWER (AUDIO ON)` / `MUTED`). Defaults to muted to respect modern browser autoplay policies.
- **Master Volume Slider**: Global output scaling from 0% to 100%.
- **RF Static & Ambience Slider**: Independent level control for background atmospheric noise and heterodynes.
- **Voice Narration Slider**: Dedicated volume control for speech and station alert tones.
- **Analog Detune Protection**: Turning the dial or losing carrier lock immediately mutes active voice narration, simulating realistic receiver behavior.

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.9 or higher installed.

### 2. Set Up Virtual Environment (Optional but Recommended)

```bash
python -m venv venv

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# macOS / Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Game

```bash
# On Windows PowerShell:
python -m streamlit run app.py

# Or standard CLI:
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

---

## 🔮 Mystery: "The Disappearance of Blackwood"

Explore four interconnected frequencies that gradually unravel what truly happened the night the valley town of Blackwood was submerged:

| Frequency | Callsign | Narrative Role & Contradictions | Evidence Intercepted |
|---|---|---|---|
| **88.1 MHz** | K-MIST 88.1 | **The Cover Story**: Claims Route 9 trestle is closed due to a natural mudslide, but notes an unnatural 22mb pressure plunge and moving lantern lights in the trees. | Anomaly on Blackwood Ridge & initial bridge closure claim |
| **91.7 MHz** | CD-ALERT 91.7 | **The Contradiction**: Civil Defense declares a mandatory evacuation for sectors 4–9, but reveals the Route 9 trestle was cordoned by armed units in chemical gear—not closed by mudslides. | Contradiction: Armed military cordon at the bridge |
| **103.4 MHz** | SHERIFF-DISP 103.4 | **The Cover-Up**: Police find civilian cars abandoned with headlights blazing; dispatch admits the Mayor's office pre-drafted the evacuation hours before any dam or flood warning was sounded. | Authorities pre-planned the evacuation hours in advance |
| **107.9 MHz** | CARRIER-ZERO 107.9 | **The Truth**: Encrypted cipher `4-19-88-0` reveals that the valley floodgates were deliberately opened from inside the control room to drown Blackwood and bury the anomaly. | Valley floodgates were intentionally breached |

### ⚖️ The Final Decision & Branching Endings
Once all four key broadcasts are authenticated, the **Case Synthesis** module activates, offering two distinct endings:
- **Ending A: "The Transmission of Truth"** — Broadcast the recordings across all county repeaters, dismantling the 40-year lie, while drawing the attention of an unlisted monitoring frequency.
- **Ending B: "The Blackwood Quarantine"** — Degauss and erase the tapes, deciding that whatever was awakened on Blackwood Ridge is safer left drowned beneath sixty feet of reservoir water.
---

## 🤝 Contributing & License
Contributions are welcome! Licensed under MIT.

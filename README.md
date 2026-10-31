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
├── requirements.txt  # Project dependencies (streamlit, python-dotenv)
├── README.md         # Documentation & guide
└── .gitignore        # Git ignore rules for Python & Streamlit
```

### 📄 Detailed File Descriptions

1. **[app.py](file:///c:/Users/nikki/AfterHours/app.py) (Main Application)**:
   - Streamlit frontend featuring an abandoned radio station aesthetic (deep black chassis, dark forest green panels, phosphor green text, and vintage amber warnings).
   - Continuous analog dial slider sweeping **80.0 to 110.0 MHz** (precision 0.1 MHz) with large digital readout.
   - Dedicated **Tune / Lock Signal** mechanism with manual dial sweeping for true station discovery.
   - Live receiver telemetry status bar (Power, Band, Tube filaments).
   - Dynamic 5-segment LED signal strength meter reflecting proximity to station carrier waves.
   - Vintage CRT monitor with scanlines, timestamp telemetry, and escaping to ensure clean text display without literal HTML leaks.
   - Investigation evidence notebook recording discovered clues, source frequencies, timestamps, and highlighting new entries.

2. **[story.py](file:///c:/Users/nikki/AfterHours/story.py) (Narrative & Frequency Telemetry)**:
   - Houses known radio stations:
     - **88.1 MHz**: *Blackwood Weather Broadcast (K-MIST Automated)*
     - **91.7 MHz**: *Civil Defense Emergency Transmission*
     - **103.4 MHz**: *Blackwood County Police Transmission*
     - **107.9 MHz**: *Mysterious Hidden Transmission (Phantom Station Zero)*
   - Dynamic frequency resolution (`resolve_frequency_telemetry`): calculates distance falloff, signal bleeding/interference near known channels, and procedural static/voice fragments on dead air.
   - Clue state management with persistent tracking, timestamping, and source frequency attribution.

3. **[ai_engine.py](file:///c:/Users/nikki/AfterHours/ai_engine.py) (AI Transmission Engine)**:
   - Modular engine designed to handle conversational personas and dynamic responses.
   - Ready for plug-and-play connection to LLM APIs (e.g., Google Gemini, OpenAI, Claude).

4. **[requirements.txt](file:///c:/Users/nikki/AfterHours/requirements.txt)**:
   - Defines dependencies (`streamlit`, `python-dotenv`).

5. **[.gitignore](file:///c:/Users/nikki/AfterHours/.gitignore)**:
   - Excludes Python bytecode, virtual environments, and secrets from Git.

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

## 🔮 Known Frequencies & Mystery Clues

| Frequency | Callsign | Description | Clue Uncovered |
|---|---|---|---|
| **88.1 MHz** | K-MIST 88.1 | Automated mountain weather bulletin | Unnatural barometric plunge & lantern lights |
| **91.7 MHz** | CD-ALERT 91.7 | Civil defense evacuation siren | Sector 4-9 evacuation & blackout orders |
| **103.4 MHz** | SHERIFF-DISP 103.4 | Police dispatch from October 1984 | Abandoned cars on Route 9 trestle bridge |
| **107.9 MHz** | CARRIER-ZERO 107.9 | Hidden clandestine numbers station | Cipher 4-19-88-0 & intentional floodgate breach |

---

## 🤝 Contributing & License
Contributions are welcome! Licensed under MIT.

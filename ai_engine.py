"""
ai_engine.py - AI Personality & Transmission Engine for AfterHours

NOTE: Real LLM integration is intentionally deferred for the initial prototype.
This module currently provides mock responses mimicking dynamic radio hosts and
paranormal broadcasts, while establishing the exact interface to be connected
to an LLM provider (e.g., Google Gemini, OpenAI, Claude, or Ollama).
"""

from typing import List, Dict, Any
import random


class RadioAIEngine:
    """
    Manages the conversational radio host persona and dynamic paranormal responses.
    
    In future iterations, this class will:
    1. Read API keys from environment variables or Streamlit secrets.
    2. Maintain system prompts customized per radio station/frequency.
    3. Generate responses using an LLM.
    """

    def __init__(self, api_key: str = None, model_name: str = "mock-afterhours-v1"):
        self.api_key = api_key
        self.model_name = model_name

    def generate_response(
        self,
        frequency: float,
        player_message: str,
        conversation_history: List[Dict[str, str]] = None,
        station_info: Dict[str, Any] = None,
    ) -> str:
        """
        Generate a radio host or transmission response based on the active frequency.
        Currently produces curated mock atmospheric dialogues.
        """
        station_name = station_info.get("name", "Unknown Frequency") if station_info else "Static"

        # Mock responses tailored to the frequency/station
        if frequency == 104.7:
            responses = [
                f"The microphone clicks. 'Ah, an incoming caller on the line! You're speaking about \"{player_message}\"? The night is deep, friend, and so are the secrets of Blackwood.'",
                f"'Did anyone else hear that static pop just now?' the host murmurs. 'Caller, you ask: \"{player_message}\". Let me tell you about what happened under the old bridge in '84...'",
                f"'Hold the line, caller! The signal meters are dancing like fireflies. What did you say about \"{player_message}\"?'",
                f"'Listen closely, listener. You're not the only one listening to this frequency tonight. Stay by your receiver.'",
            ]
            return random.choice(responses)

        elif frequency == 91.3:
            return (
                f"[Automated Weather Tone] ...Emergency advisory updated. In response to query \"{player_message}\": "
                f"Citizens are advised to remain indoors with windows shuttered until sunrise."
            )

        elif frequency == 107.9:
            numbers = " ".join([str(random.randint(10, 99)) for _ in range(5)])
            return f"...[Musical Chime]... Reciting sequence: {numbers} ... Repeat: {numbers} ... [Chime fades]"

        else:
            static_sounds = [
                "...*kzzzzzt*... [a faint voice whispers unintelligibly beneath heavy static] ...",
                "...*whirrrr*... [high-pitched electronic squeal followed by silence] ...",
                "...*crackle*... [distant organ music bleeding through from another frequency] ...",
            ]
            return random.choice(static_sounds)


# Global default instance for easy import
engine = RadioAIEngine()


def get_radio_response(
    frequency: float,
    player_message: str,
    conversation_history: List[Dict[str, str]] = None,
    station_info: Dict[str, Any] = None,
) -> str:
    """Convenience helper function to query the radio AI engine."""
    return engine.generate_response(
        frequency=frequency,
        player_message=player_message,
        conversation_history=conversation_history,
        station_info=station_info,
    )

# To install the required library: pip install elevenlabs
import os
from elevenlabs.client import ElevenLabs
from elevenlabs import play

# --- Configuration ---
# IMPORTANT: Replace "YOUR_API_KEY" with your actual ElevenLabs API key.
# For better security, consider using environment variables.
ELEVENLABS_API_KEY = "YOUR_API_KEY"

# You can find Voice IDs on the ElevenLabs website in the "Voice Lab".
# "Bella" is a popular and expressive pre-made voice.
DEFAULT_VOICE_ID = "EXAVITQu4vr4xnSDxMaL"

# Initialize the ElevenLabs client
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

def speak(text, voice_id=DEFAULT_VOICE_ID):
    """
    Converts a string of text into speech using the ElevenLabs API and plays it.

    Args:
        text (str): The text you want to convert to speech.
        voice_id (str, optional): The ID of the voice to use. Defaults to DEFAULT_VOICE_ID.
    """
    if not ELEVENLABS_API_KEY or ELEVENLABS_API_KEY == "YOUR_API_KEY":
        print("⚠️ ElevenLabs API key is not set. Please add it to `elevenlabs_api.py`.")
        return

    print(f"🗣️ AI Speaking: '{text}'")
    try:
        # Generate the audio from the text
        audio = client.generate(
            text=text,
            voice=voice_id,
            model="eleven_multilingual_v2" # A versatile and high-quality model
        )

        # Play the generated audio
        play(audio)

    except Exception as e:
        print(f"❌ An error occurred with the ElevenLabs API: {e}")

# --- Example of how to use this file ---
if __name__ == "__main__":
    # This is a test run to demonstrate the 'speak' function.
    print("--- Testing ElevenLabs API ---")
    speak("Hello! This is a test of the text-to-speech API.")
    speak("You can integrate this function into your main AI script to give it a voice.")
import pyttsx3
import whisper
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import tempfile
import threading
import os



# Set your actual FFmpeg path here:
ffmpeg_path = r"C:\Users\HCES\Documents\ffmpeg-7.1.1-essentials_build\bin"
os.environ["PATH"] += os.pathsep + ffmpeg_path


# TTS engine (initialized once)
_tts_engine = pyttsx3.init()

# Whisper model (loaded once)
_whisper_model = whisper.load_model("base")


def speak_text_async(text):
    def speak():
        _tts_engine.say(text)
        _tts_engine.runAndWait()
    threading.Thread(target=speak, daemon=True).start()


def record_and_transcribe(duration=5, samplerate=16000):
    try:
        audio = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=1, dtype='int16')
        sd.wait()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            wav.write(f.name, samplerate, audio)
            result = _whisper_model.transcribe(f.name)
            return result["text"].strip()
    except Exception as e:
        return f"[Speech Error]: {e}"

# main.py
import os
import sys
import customtkinter as ctk
from dotenv import load_dotenv
import pygame

# Import your custom modules
from jarvis_core import JarvisCore
from voice_io import VoiceIO
from gui import App
from logger import log_info, log_error

def main():
    """Main entry point for the JARVIS AI Assistant application."""
    load_dotenv()
    log_info("Application starting...")

    # Initialize Pygame
    pygame.init()

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Check for API keys
    google_api_key = os.getenv("GOOGLE_API_KEY")
    eleven_api_key = os.getenv("ELEVEN_API_KEY")

    if not google_api_key:
        log_error("CRITICAL: GOOGLE_API_KEY not found.")
    if not eleven_api_key:
        log_error("CRITICAL: ELEVEN_API_KEY not found. Voice IO will not work.")
    
    try:
        # Initialize VoiceIO first
        voice_interface = VoiceIO(api_key=eleven_api_key)
        # Pass the voice_interface to JarvisCore
        jarvis_brain = JarvisCore(voice_io=voice_interface)
    except Exception as e:
        log_error(f"Failed to initialize core components: {e}")
        pygame.quit()
        sys.exit(1)

    # Launch the GUI
    app = App(jarvis=jarvis_brain, voice_io=voice_interface)
    app.mainloop()
    
    # Clean up
    pygame.quit()
    log_info("Application shutting down.")

if __name__ == "__main__":
    if not os.path.exists("mic_icon.png"):
        print("Warning: 'mic_icon.png' not found. The mic button will not have an icon.")
    
    main()
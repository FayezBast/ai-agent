# gui.py
import customtkinter as ctk
from PIL import Image

class App(ctk.CTk):
    def __init__(self, jarvis, voice_io):
        super().__init__()

        self.jarvis = jarvis
        self.voice_io = voice_io

        self.title("JARVIS AI Assistant")
        self.geometry("800x600")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.textbox = ctk.CTkTextbox(self.main_frame, state="disabled", wrap="word", font=("Arial", 14))
        self.textbox.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.entry = ctk.CTkEntry(self.main_frame, placeholder_text="Type your command or press the mic...", font=("Arial", 14))
        self.entry.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.entry.bind("<Return>", self.handle_send_event)

        try:
            mic_icon = ctk.CTkImage(Image.open("mic_icon.png"), size=(24, 24))
        except FileNotFoundError:
            mic_icon = None # Handle case where icon is missing

        self.mic_button = ctk.CTkButton(self.main_frame, image=mic_icon, text="" if mic_icon else "Mic", width=40, command=self.handle_mic_event)
        self.mic_button.grid(row=1, column=1, padx=(0, 10), pady=(0, 10), sticky="w")
        
        self.display_message("JARVIS: Hello! How can I assist you today?", "green")

    def display_message(self, message: str, color: str = "white"):
        """Displays a message in the chatbox."""
        self.textbox.configure(state="normal")
        self.textbox.insert("end", f"{message}\n\n")
        self.textbox.configure(state="disabled")
        self.textbox.see("end")

    def handle_send_event(self, event=None):
        """Handles sending a typed command."""
        user_input = self.entry.get()
        if not user_input:
            return
        
        self.voice_io.stop_audio() # Interrupt previous speech
        self.display_message(f"You: {user_input}", "cyan")
        self.entry.delete(0, "end")
        self.after(50, lambda: self.process_and_respond(user_input))

    def handle_mic_event(self):
        """Handles the microphone button click."""
        self.voice_io.stop_audio() # Interrupt previous speech
        self.display_message("JARVIS: Listening...", "yellow")
        self.update_idletasks()
        
        command = self.voice_io.listen()
        if command:
            self.display_message(f"You (voice): {command}", "cyan")
            self.after(50, lambda: self.process_and_respond(command))
        else:
            self.display_message("JARVIS: I didn't catch that. Please try again.", "orange")

    def process_and_respond(self, command: str):
        """
        Sends command to JARVIS core, which now handles speaking.
        This method just displays the final text response.
        """
        response = self.jarvis.process_command(command)
        self.display_message(f"JARVIS: {response}", "green")
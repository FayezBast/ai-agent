# clipboard_controller.py
import pyperclip
from logger import log_info, log_error

class ClipboardController:
    def read_clipboard(self) -> str:
        """Reads the current content of the system clipboard."""
        try:
            content = pyperclip.paste()
            if content:
                log_info("Read content from clipboard.")
                return f"The clipboard contains: {content}"
            else:
                return "The clipboard is currently empty."
        except Exception as e:
            log_error(f"Clipboard read error: {e}")
            return "Sorry, I couldn't read the clipboard."

    def write_to_clipboard(self, text: str) -> str:
        """Writes text to the system clipboard."""
        if not text:
            return "Please provide some text to copy."
        try:
            pyperclip.copy(text)
            log_info(f"Wrote '{text}' to clipboard.")
            return f"I have copied '{text}' to your clipboard."
        except Exception as e:
            log_error(f"Clipboard write error: {e}")
            return "Sorry, I couldn't write to the clipboard."
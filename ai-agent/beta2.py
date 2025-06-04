from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import sys

# ✅ FIXED local path
model_path = "C:/Users/HCES/Documents/speech/trained-voice-llm"

# ✅ Load locally
tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
model = AutoModelForCausalLM.from_pretrained(model_path, local_files_only=True)

def get_model_response(prompt):
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=100, do_sample=True, top_p=0.9, temperature=0.7)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Voice Assistant Chat")
        self.setMinimumSize(500, 400)

        layout = QVBoxLayout()
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        self.input_field = QLineEdit()
        layout.addWidget(self.input_field)

        self.send_button = QPushButton("Send")
        layout.addWidget(self.send_button)
        self.setLayout(layout)

        self.send_button.clicked.connect(self.handle_input)
        self.input_field.returnPressed.connect(self.handle_input)

    def handle_input(self):
        user_text = self.input_field.text().strip()
        if not user_text:
            return

        self.chat_display.append(f"User: {user_text}")
        self.input_field.clear()

        prompt = f"User: {user_text}\nAssistant:"
        response = get_model_response(prompt)
        response_lines = response.split("Assistant:")
        if len(response_lines) > 1:
            assistant_reply = response_lines[-1].strip()
        else:
            assistant_reply = response.strip()

        self.chat_display.append(f"Assistant: {assistant_reply}\n")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())

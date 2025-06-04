import model

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor
from speech2 import speak_text_async, record_and_transcribe
from model import get_ai_response


class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(" AI Chat Assistant")
        self.setGeometry(100, 100, 600, 600)

        self.layout = QVBoxLayout()

        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("font: 14pt;")

        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Type your message...")
        self.input_line.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)

        self.voice_button = QPushButton("🎤 Voice Input")
        self.voice_button.clicked.connect(self.voice_input)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.send_button)
        input_layout.addWidget(self.voice_button)

        self.layout.addWidget(QLabel("💬 Chat with Ollama"))
        self.layout.addWidget(self.chat_area)
        self.layout.addLayout(input_layout)

        self.setLayout(self.layout)

    def send_message(self):
        user_text = self.input_line.text().strip()
        if user_text:
            self.display_user_message(user_text)
            response = get_ai_response(user_text)
            self.display_ai_message(response)
            speak_text_async(response)
            self.input_line.clear()

    def voice_input(self):
        self.chat_area.append("🎙️ Listening (5 seconds)...")
        self.repaint()

        user_text = record_and_transcribe()
        if user_text:
            self.input_line.setText(user_text)
            self.send_message()
        else:
            self.chat_area.append("🤷 Whisper didn't catch anything.\n")

    def display_user_message(self, text):
        self.chat_area.append(f"🧑 You: {text}")

    def display_ai_message(self, text):
        self.chat_area.append(f"🤖 AI: {text}\n")
        self.chat_area.moveCursor(QTextCursor.MoveOperation.End)

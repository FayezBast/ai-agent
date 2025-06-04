import sys
import os
import time
import random
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QTextEdit, QLineEdit, QPushButton, 
                           QLabel, QScrollArea, QFrame, QSplitter, QComboBox,
                           QStackedWidget, QGridLayout, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QThread, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon, QFont, QColor, QPalette, QTextCursor

# Simulated AI response thread - in production, connect to your actual AI API
class AIChatThread(QThread):
    update_signal = pyqtSignal(str)
    typing_signal = pyqtSignal(bool)
    
    def __init__(self, message):
        super().__init__()
        self.message = message
        
    def run(self):
        # Simulate AI "thinking"
        self.typing_signal.emit(True)
        time.sleep(1)  # Simulated thinking time
        
        # Simple response logic - replace with your AI model integration
        message = self.message.lower()
        
        if "hello" in message or "hi" in message:
            response = "Hello! How can I assist you today?"
        elif "how are you" in message:
            response = "I'm functioning well, thank you for asking! How about you?"
        elif "help" in message:
            response = "I'm here to help. Could you provide more details about what you need assistance with?"
        elif "thank" in message:
            response = "You're welcome! Feel free to ask if you need anything else."
        elif "bye" in message:
            response = "Goodbye! Feel free to return if you have more questions."
        elif "weather" in message:
            response = "I don't have access to real-time weather data, but I can help you understand weather concepts or direct you to reliable sources."
        elif "code" in message or "python" in message:
            response = "I'd be happy to help with coding! I can explain concepts, debug code, or generate examples. What specifically do you need help with?"
        else:
            responses = [
                f"I understand you said: '{self.message}'. Could you elaborate on what you're looking for?",
                f"Thanks for your message about '{self.message}'. How can I assist you with this topic?",
                f"I see you're interested in '{self.message}'. What would you like to know about this?"
            ]
            response = random.choice(responses)
        
        # Character-by-character typing effect
        display_text = ""
        for char in response:
            display_text += char
            self.update_signal.emit(display_text)
            time.sleep(0.01)  # Adjust typing speed
            
        self.typing_signal.emit(False)


class MessageWidget(QFrame):
    def __init__(self, message, is_user=True, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.init_ui(message)
        
    def init_ui(self, message):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Message header with time
        header_layout = QHBoxLayout()
        
        # Set sender name and style
        if self.is_user:
            sender_name = "You"
            self.setStyleSheet("""
                QFrame {
                    background-color: #eff6ff;
                    border-radius: 10px;
                    margin-left: 100px;
                    padding: 10px;
                }
            """)
        else:
            sender_name = "AI Assistant"
            self.setStyleSheet("""
                QFrame {
                    background-color: #f3f4f6;
                    border-radius: 10px;
                    margin-right: 100px;
                    padding: 10px;
                }
            """)
            
        # Avatar or icon placeholder
        avatar_label = QLabel()
        if self.is_user:
            avatar_label.setText("👤")  # User icon
        else:
            avatar_label.setText("🤖")  # AI icon
        avatar_label.setFont(QFont("Arial", 16))
        
        # Sender name and timestamp
        current_time = datetime.now().strftime('%H:%M')
        header_text = QLabel(f"{sender_name} • {current_time}")
        header_text.setStyleSheet("color: #757575; font-size: 11px;")
        
        header_layout.addWidget(avatar_label)
        header_layout.addWidget(header_text)
        header_layout.addStretch()
        
        # Message content
        message_text = QTextEdit()
        message_text.setPlainText(message)
        message_text.setReadOnly(True)
        message_text.setFrameStyle(QFrame.Shape.NoFrame)
        message_text.setStyleSheet("background-color: transparent;")
        
        # Automatically adjust height based on content
        doc_height = message_text.document().size().height()
        message_text.setFixedHeight(min(150, max(30, doc_height + 10)))
        
        layout.addLayout(header_layout)
        layout.addWidget(message_text)


class WelcomeWidget(QWidget):
    example_clicked = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Welcome icon
        icon_label = QLabel("🤖")
        icon_label.setFont(QFont("Arial", 48))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Welcome title
        title_label = QLabel("Welcome to AI Assistant")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Welcome subtitle
        subtitle_label = QLabel("I'm here to help with information, creative tasks, coding, and more. How can I assist you today?")
        subtitle_label.setWordWrap(True)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #4b5563; margin-bottom: 20px;")
        
        # Example queries section title
        examples_title = QLabel("Try asking me:")
        examples_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        examples_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Grid for example queries
        examples_grid = QGridLayout()
        
        example_queries = [
            ("Explain machine learning", "Understanding the basics of AI", 
             "Can you explain how machine learning works?"),
            ("Write a creative story", "Get help with creative writing", 
             "Write a short story about a robot discovering emotions."),
            ("Debug code", "Get help with programming", 
             "Help me debug this Python code: for i in range(10): print(i))"),
            ("Productivity advice", "Get practical life tips", 
             "What are some tips for effective time management?")
        ]
        
        # Create example buttons
        row, col = 0, 0
        for title, subtitle, query in example_queries:
            example_frame = QFrame()
            example_frame.setStyleSheet("""
                QFrame {
                    background-color: #f3f4f6;
                    border-radius: 8px;
                    padding: 10px;
                }
                QFrame:hover {
                    background-color: #e5e7eb;
                }
            """)
            
            example_layout = QVBoxLayout(example_frame)
            
            title_label = QLabel(f"<b>{title}</b>")
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet("color: #6b7280; font-size: 11px;")
            
            example_layout.addWidget(title_label)
            example_layout.addWidget(subtitle_label)
            
            # Store the query as a property
            example_frame.setProperty("query", query)
            
            # Make the frame clickable
            example_frame.mousePressEvent = lambda event, q=query: self.example_clicked.emit(q)
            
            examples_grid.addWidget(example_frame, row, col)
            
            # Update grid position
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        # Add widgets to layout
        layout.addStretch(1)
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addSpacing(20)
        layout.addWidget(examples_title)
        layout.addSpacing(10)
        layout.addLayout(examples_grid)
        layout.addStretch(1)


class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern AI Chat Interface")
        self.setMinimumSize(900, 600)
        self.ai_thinking = False
        self.is_dark_mode = False
        self.init_ui()
        
    def init_ui(self):
        # Set central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left sidebar for chat history/settings
        self.sidebar = QWidget()
        sidebar_layout = QVBoxLayout(self.sidebar)
        
        # Sidebar title - Recent Conversations
        recent_label = QLabel("RECENT CONVERSATIONS")
        recent_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #6b7280; letter-spacing: 0.05em;")
        sidebar_layout.addWidget(recent_label)
        
        # Sample conversation history items
        sample_chats = [
            ("New Conversation", True),
            ("Python Help", False),
            ("Web Design Ideas", False),
            ("Project Planning", False)
        ]
        
        for chat_name, is_active in sample_chats:
            chat_btn = QPushButton(chat_name)
            if is_active:
                chat_btn.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding: 10px;
                        border: none;
                        border-radius: 5px;
                        background-color: #e5e7eb;
                        font-weight: 500;
                    }
                """)
            else:
                chat_btn.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding: 10px;
                        border: none;
                        border-radius: 5px;
                        background-color: transparent;
                        color: #4b5563;
                    }
                    QPushButton:hover {
                        background-color: #f3f4f6;
                    }
                """)
            sidebar_layout.addWidget(chat_btn)
        
        sidebar_layout.addStretch()
        
        # Settings section
        settings_label = QLabel("SETTINGS")
        settings_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #6b7280; letter-spacing: 0.05em;")
        sidebar_layout.addWidget(settings_label)
        
        # Model selection dropdown
        model_layout = QVBoxLayout()
        model_label = QLabel("AI Model")
        model_label.setStyleSheet("font-size: 12px; color: #4b5563;")
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(["GPT-4 Turbo", "Claude 3", "Llama 3", "Custom Model"])
        self.model_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border-radius: 5px;
                border: 1px solid #e5e7eb;
                background-color: #f9fafb;
            }
        """)
        
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        sidebar_layout.addLayout(model_layout)
        sidebar_layout.addSpacing(10)
        
        # Theme toggle
        theme_btn = QPushButton("Toggle Dark Mode")
        theme_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                border-radius: 5px;
                background-color: #f3f4f6;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #e5e7eb;
            }
        """)
        theme_btn.clicked.connect(self.toggle_theme)
        sidebar_layout.addWidget(theme_btn)
        
        # Export button
        export_btn = QPushButton("Export Chat")
        export_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                border-radius: 5px;
                background-color: #6366f1;
                color: white;
                text-align: center;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #4f46e5;
            }
        """)
        export_btn.clicked.connect(self.export_chat)
        sidebar_layout.addWidget(export_btn)
        
        # Version info
        version_label = QLabel("AI Assistant v1.0")
        version_label.setStyleSheet("font-size: 11px; color: #9ca3af; margin-top: 10px;")
        sidebar_layout.addWidget(version_label)
        
        copyright_label = QLabel("© 2025 AI Company")
        copyright_label.setStyleSheet("font-size: 11px; color: #9ca3af;")
        sidebar_layout.addWidget(copyright_label)
        
        # Right content area (chat interface)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Header with new chat button
        header_layout = QHBoxLayout()
        
        new_chat_btn = QPushButton("+ New Chat")
        new_chat_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 12px;
                border-radius: 5px;
                background-color: #f3f4f6;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #e5e7eb;
            }
        """)
        new_chat_btn.clicked.connect(self.new_chat)
        
        header_layout.addStretch()
        header_layout.addWidget(new_chat_btn)
        content_layout.addLayout(header_layout)
        
        # Stacked widget to switch between welcome and chat
        self.stacked_widget = QStackedWidget()
        
        # Welcome screen
        self.welcome_widget = WelcomeWidget()
        self.welcome_widget.example_clicked.connect(self.handle_example_query)
        
        # Chat message area
        self.chat_widget = QWidget()
        chat_layout = QVBoxLayout(self.chat_widget)
        
        # Scrollable message area
        self.message_scroll = QScrollArea()
        self.message_scroll.setWidgetResizable(True)
        self.message_scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        self.message_area = QWidget()
        self.message_layout = QVBoxLayout(self.message_area)
        self.message_layout.addStretch()
        self.message_scroll.setWidget(self.message_area)
        
        # Typing indicator
        self.typing_indicator = QLabel("AI is thinking...")
        self.typing_indicator.setStyleSheet("""
            color: #6b7280; 
            font-style: italic; 
            padding: 8px; 
            background-color: #f3f4f6;
            border-radius: 10px;
            margin-right: 100px;
        """)
        self.typing_indicator.setVisible(False)
        
        chat_layout.addWidget(self.message_scroll)
        chat_layout.addWidget(self.typing_indicator)
        
        # Add both widgets to stacked widget
        self.stacked_widget.addWidget(self.welcome_widget)
        self.stacked_widget.addWidget(self.chat_widget)
        
        # Show welcome screen initially
        self.stacked_widget.setCurrentIndex(0)
        
        content_layout.addWidget(self.stacked_widget)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Message AI Assistant...")
        self.message_input.setMaximumHeight(80)
        self.message_input.setAcceptRichText(False)
        self.message_input.textChanged.connect(self.check_input)
        self.message_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e5e7eb;
                border-radius: 10px;
                padding: 10px;
                background-color: #f9fafb;
            }
        """)
        
        self.send_button = QPushButton("Send")
        self.send_button.setEnabled(False)
        self.send_button.setFixedSize(60, 40)
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #6366f1;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4f46e5;
            }
            QPushButton:disabled {
                background-color: #d1d5db;
            }
        """)
        
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        
        content_layout.addLayout(input_layout)
        
        # Add sidebar and content to splitter
        splitter.addWidget(self.sidebar)
        splitter.addWidget(content_widget)
        
        # Set sidebar to a fixed width but allow user resizing
        splitter.setSizes([200, 700])
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
        
    def check_input(self):
        # Enable/disable send button based on input
        text = self.message_input.toPlainText().strip()
        self.send_button.setEnabled(len(text) > 0 and not self.ai_thinking)
        
    def handle_example_query(self, query):
        self.message_input.setPlainText(query)
        self.send_message()
        
    def send_message(self):
        message = self.message_input.toPlainText().strip()
        if not message or self.ai_thinking:
            return
            
        # Switch to chat view if on welcome screen
        if self.stacked_widget.currentIndex() == 0:
            self.stacked_widget.setCurrentIndex(1)
            
        # Add user message
        self.add_message(message, True)
        self.message_input.clear()
        
        # Start AI response thread
        self.ai_thinking = True
        self.typing_indicator.setVisible(True)
        self.send_button.setEnabled(False)
        
        self.ai_thread = AIChatThread(message)
        self.ai_thread.update_signal.connect(self.update_ai_response)
        self.ai_thread.typing_signal.connect(self.set_typing_indicator)
        self.ai_thread.start()
        
    def add_message(self, message, is_user):
        message_widget = MessageWidget(message, is_user)
        
        # Remove the stretch at the end
        self.message_layout.removeItem(self.message_layout.itemAt(self.message_layout.count()-1))
        
        # Add the message widget
        self.message_layout.addWidget(message_widget)
        
        # Add stretch back
        self.message_layout.addStretch()
        
        # Store reference if it's an AI message being typed
        if not is_user:
            self.current_ai_message = message_widget
            
        # Scroll to bottom
        self.message_scroll.verticalScrollBar().setValue(
            self.message_scroll.verticalScrollBar().maximum()
        )
            
    def update_ai_response(self, text):
        # Find the text edit in the current AI message and update its content
        if hasattr(self, 'current_ai_message'):
            message_text = self.current_ai_message.findChild(QTextEdit)
            if message_text:
                message_text.setPlainText(text)
                
                # Update height based on new content
                doc_height = message_text.document().size().height()
                message_text.setFixedHeight(min(150, max(30, doc_height + 10)))
        else:
            # First update - create the message widget
            self.add_message(text, False)
        
    def set_typing_indicator(self, is_typing):
        self.ai_thinking = is_typing
        self.typing_indicator.setVisible(is_typing)
        self.check_input()  # Re-check if send button should be enabled
        
    def new_chat(self):
        # Clear the chat area
        while self.message_layout.count() > 1:  # Keep the last stretch
            item = self.message_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Switch back to welcome screen
        self.stacked_widget.setCurrentIndex(0)
        
        # Clear input
        self.message_input.clear()
        self.send_button.setEnabled(False)
        
    def export_chat(self):
        # In a real app, implement file dialog and saving logic
        print("Export chat functionality would save the conversation to a file")
        
    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        
        if self.is_dark_mode:
            # Dark mode styles
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #111827;
                    color: #f9fafb;
                }
                QTextEdit {
                    background-color: #1f2937;
                    color: #f9fafb;
                    border: 1px solid #374151;
                }
                QScrollArea {
                    background-color: #111827;
                }
                QPushButton {
                    background-color: #1f2937;
                    color: #f9fafb;
                }
                QComboBox {
                    background-color: #1f2937;
                    color: #f9fafb;
                    border: 1px solid #374151;
                }
            """)
            
            # Update message widget styles
            for i in range(self.message_layout.count()-1):  # -1 to skip stretch
                item = self.message_layout.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    if isinstance(widget, MessageWidget):
                        if widget.is_user:
                            widget.setStyleSheet("""
                                QFrame {
                                    background-color: #312e81;
                                    border-radius: 10px;
                                    margin-left: 100px;
                                    padding: 10px;
                                }
                            """)
                        else:
                            widget.setStyleSheet("""
                                QFrame {
                                    background-color: #1f2937;
                                    border-radius: 10px;
                                    margin-right: 100px;
                                    padding: 10px;
                                }
                            """)
        else:
            # Light mode (reset styles)
            self.setStyleSheet("")
            
            # Update message widget styles
            for i in range(self.message_layout.count()-1):  # -1 to skip stretch
                item = self.message_layout.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    if isinstance(widget, MessageWidget):
                        if widget.is_user:
                            widget.setStyleSheet("""
                                QFrame {
                                    background-color: #eff6ff;
                                    border-radius: 10px;
                                    margin-left: 100px;
                                    padding: 10px;
                                }
                            """)
                        else:
                            widget.setStyleSheet("""
                                QFrame {
                                    background-color: #f3f4f6;
                                    border-radius: 10px;
                                    margin-right: 100px;
                                    padding: 10px;
                                }
                            """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application-wide font
    font = QFont("Arial", 10)
    app.setFont(font)
    
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())
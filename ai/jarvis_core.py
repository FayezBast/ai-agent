# jarvis_core.py
import os
from ai_core import AI_Core
from file_manager import FileManager
from system_controller import SystemController
from web_controller import WebController
from knowledge_controller import KnowledgeController
from clipboard_controller import ClipboardController
from weather_controller import WeatherController
from logger import log_info, log_error

class JarvisCore:
    """The core logic engine for the JARVIS AI assistant."""

    def __init__(self, voice_io):
        log_info("Initializing JARVIS Core...")
        api_key = os.getenv('GOOGLE_API_KEY')
        self.ai_core = AI_Core(api_key)
        self.file_manager = FileManager()
        self.system_controller = SystemController()
        self.web_controller = WebController()
        self.knowledge_controller = KnowledgeController()
        self.clipboard_controller = ClipboardController()
        self.weather_controller = WeatherController()
        self.voice_io = voice_io
        self.conversation_history = [] # For contextual memory
        log_info("JARVIS Core initialized.")

    def process_command(self, command: str) -> str:
        """
        Analyzes a command, executes the action, and speaks the response.
        """
        log_info(f"Processing command: '{command}'")
        if not command:
            return "How can I help you?"

        try:
            # Pass the command and history to the AI core for analysis
            analysis = self.ai_core.analyze_command(command, self.conversation_history)
            
            response = "" # Initialize response string

            # If AI provided a direct conversational response
            if analysis.get("response"):
                response = analysis["response"]
            # Otherwise, execute the identified task
            else:
                intent = analysis.get("intent", "conversation")
                action = analysis.get("action", "chat")
                params = analysis.get("parameters", {})

                # CLEANED UP: Main logic router for all intents
                if intent == "file_creation":
                    response = self._handle_file_creation(action, params)
                elif intent == "file_management":
                    response = self._handle_file_management(action, params)
                elif intent == "web_browse":
                    response = self.web_controller.search_web(params.get("query", ""))
                elif intent == "knowledge_inquiry":
                    response = self.knowledge_controller.get_wikipedia_summary(params.get("topic", ""))
                elif intent == "weather_inquiry":
                    response = self.weather_controller.get_weather(params.get("city", ""))
                elif intent == "clipboard_management":
                    if action == "read_clipboard":
                        response = self.clipboard_controller.read_clipboard()
                    elif action == "write_clipboard":
                        response = self.clipboard_controller.write_to_clipboard(params.get("text", ""))
                elif intent == "system_control":
                    if action == "take_screenshot":
                        response = self.system_controller.take_screenshot()
                    elif action == "get_system_status":
                        response = self.system_controller.get_system_status(params.get("status_type", ""))
                    elif action == "open_application":
                        response = self.system_controller.open_application(params.get("application_name", ""))
                elif intent == "help":
                    response = self._get_help_text()
                else: # Fallback to conversation
                    response = "I'm not sure how to do that. Try asking in a different way."

            # Update conversation history
            self.conversation_history.append({"role": "user", "content": command})
            self.conversation_history.append({"role": "assistant", "content": response})
            # Keep the history to the last 3 exchanges (6 items)
            self.conversation_history = self.conversation_history[-6:]
            
            # Speak the final response
            self.voice_io.speak(response)
            
            # Return the text for the GUI
            return response

        except Exception as e:
            log_error(f"Error processing command '{command}': {e}", exc_info=True)
            error_message = "I'm sorry, an unexpected error occurred."
            self.voice_io.speak(error_message)
            return error_message
    
    # --- Helper methods (_handle_file_creation, etc.) are unchanged ---
    def _handle_file_creation(self, action: str, params: dict) -> str:
        topic = params.get("content_topic")
        if not topic:
            return "Please specify a topic for the file content."
        file_type_map = {'create_word': 'docx', 'create_excel': 'xlsx', 'create_pdf': 'pdf', 'create_python': 'py', 'create_text': 'txt'}
        file_type = file_type_map.get(action, 'txt')
        filename = f"{topic.replace(' ', '_').replace('.', '')[:30]}.{file_type}"
        content = self.ai_core.generate_file_content(topic, file_type)
        return self.file_manager.create_file(filename, content, file_type)

    def _handle_file_management(self, action: str, params: dict) -> str:
        query = params.get("query")
        if action == "list_files":
            files = self.file_manager.list_workspace_files()
            if not files:
                return "Your workspace is empty."
            return "Files in your workspace:\n" + "\n".join([f"- {f['name']}" for f in files])
        if not query:
            return "Please specify a filename or search term."
        if action == "find_file":
            results = self.file_manager.find_files(query)
            if not results:
                return f"No files found matching '{query}'."
            return "Found these files:\n" + "\n".join([f"- {r.name}" for r in results])
        if action == "delete_file":
            results = self.file_manager.find_files(query)
            if not results:
                return f"No file found matching '{query}' to delete."
            return self.file_manager.delete_file(results[0])
        return "Unknown file management action."

    def _get_help_text(self) -> str:
        # NEW: Updated help text with all new commands
        return """
        Here are some things I can do:
        - Create Files: "Create a python script for a timer"
        - Manage Files: "List files" or "Find my_report.docx"
        - Open Apps: "Launch visual studio code"
        - Search Web: "Search for news about AI"
        - Get Info: "Tell me about the Roman Empire"
        - Weather: "What is the weather like in New York?"
        - System: "What is my CPU usage?" or "Take a screenshot"
        - Clipboard: "Read my clipboard" or "Copy 'Important Note' to clipboard"
        """
import os
import sys
import json
import subprocess
import platform
import webbrowser
import speech_recognition as sr
import pyttsx3
from pathlib import Path
from datetime import datetime
import requests # For fetching image from URL if you implement vision model
import openai
import google.generativeai as genai # Import the Gemini library
from google.api_core.exceptions import GoogleAPIError # For specific Gemini errors
from openai import OpenAI # Specific import for OpenAI client
from dotenv import load_dotenv # For loading environment variables from a .env file
import shutil # For robust app opening on Linux

class JarvisAI:
    def __init__(self):
        # Load environment variables from .env file (if it exists)
        # This line should be at the very beginning of your script or main() function
        # before any API clients are initialized.
        load_dotenv()

        self.system = platform.system().lower()
        self.workspace_dir = Path.home() / "JARVIS_Workspace"
        self.workspace_dir.mkdir(exist_ok=True)

        # Initialize speech
        self.tts_engine = pyttsx3.init()
        self.speech_recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # AI Model configurations
        self.openai_client = None
        self.gemini_client = None # New attribute for Gemini client
        # Removed local_gen_model and nlp_classifier as per request

        # Command categories and their associated actions
        self.command_categories = {
            'file_creation': ['create', 'make', 'new', 'write', 'generate'],
            'file_management': ['open', 'show', 'list', 'find', 'search', 'delete', 'move'],
            'web_Browse': ['browse', 'search web', 'google', 'website', 'url', 'open'],
            'system_control': ['calculator', 'notepad', 'settings', 'shutdown', 'restart', 'launch', 'open'],
            'information': ['what', 'how', 'when', 'where', 'why', 'tell me', 'explain'],
            'conversation': ['hello', 'hi', 'how are you', 'thank you', 'goodbye']
        }

        self.setup_ai_models()
        print(f"🤖 JARVIS AI Assistant initialized")
        print(f"💻 System: {platform.system()}")
        print(f"🏠 Workspace: {self.workspace_dir}")

    def setup_ai_models(self):
        """Initialize AI models for NLP processing"""
        print("🔧 Setting up AI models...")
        
        # Setup OpenAI if API key available
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            try:
                self.openai_client = OpenAI(api_key=openai_key)
                # Test connection (optional, but good for early feedback)
                self.openai_client.models.list() 
                print("✅ OpenAI API connected")
            except openai.APIError as e:
                print(f"⚠️ OpenAI API connection error: {e}")
                self.openai_client = None # Ensure client is None if connection fails
        else:
            print("⚠️ OPENAI_API_KEY not found. OpenAI API will not be used.")

        # Setup Gemini if API key available
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key:
            try:
                genai.configure(api_key=gemini_key)
                # Using 'gemini-1.5-flash' as requested
                self.gemini_client = genai.GenerativeModel('gemini-1.5-flash') 
                # Test connection (optional)
                # A small generate_content call helps verify the key and model exist
                self.gemini_client.generate_content("ping", stream=True)
                print("✅ Gemini API connected using gemini-1.5-flash")
            except GoogleAPIError as e:
                print(f"⚠️ Gemini API connection error: {e}")
                self.gemini_client = None # Ensure client is None if connection fails
        else:
            print("⚠️ GEMINI_API_KEY not found. Gemini API will not be used.")

        # Removed Hugging Face model loading (nlp_classifier and local_gen_model)

        if not self.gemini_client and not self.openai_client:
            print("📝 No external AI models connected. JARVIS will use rule-based processing only.")

    def speak(self, text):
        """Convert text to speech"""
        try:
            print(f"🤖 JARVIS: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"❌ Speech error: {e}")

    def listen(self):
        """Listen for voice commands"""
        try:
            with self.microphone as source:
                print("🎤 Listening...")
                self.speech_recognizer.adjust_for_ambient_noise(source, duration=1) # Adjust duration
                audio = self.speech_recognizer.listen(source, timeout=5, phrase_time_limit=5) # Shorter phrase limit

            command = self.speech_recognizer.recognize_google(audio)
            print(f"🗣️ You said: {command}")
            return command.lower()

        except sr.WaitTimeoutError:
            return None # No speech detected within timeout
        except sr.UnknownValueError:
            self.speak("I didn't catch that. Could you repeat?")
            return None
        except sr.RequestError as e:
            self.speak("Could not request results from the speech recognition service. Please check your internet connection.")
            print(f"❌ Speech recognition service error: {e}")
            return None
        except Exception as e:
            print(f"❌ General speech recognition error: {e}")
            return None

    def analyze_command_with_ai(self, command):
        """Use AI to understand the command intent and extract parameters."""
        # Prioritize Gemini if available for robust intent analysis
        try:
            if self.gemini_client:
                return self._analyze_with_gemini(command)
            elif self.openai_client:
                return self._analyze_with_openai(command)
            else:
                # Fallback to rule-based if no external APIs are configured
                return self._analyze_with_rules(command)
        except Exception as e:
            print(f"❌ AI analysis error: {e}")
            # Fallback to rules if AI analysis fails for any reason
            return self._analyze_with_rules(command)

    def _analyze_with_gemini(self, command):
        """Analyze command using Gemini API for intent and parameters."""
        prompt = f"""
        Analyze this command and return a JSON object with the detected intent, a specific action, and any relevant parameters.
        The response MUST be valid JSON, containing only the JSON object, and nothing else.

        Command: "{command}"

        Possible intents: file_creation, file_management, web_Browse, system_control, information, conversation

        Possible actions for each intent:
        - file_creation: create_website, create_code (e.g., python), create_text
        - file_management: list_files, open_file, delete_file, find_file
        - web_Browse: web_search, open_url
        - system_control: open_calculator, open_notepad, shutdown_system, restart_system, open_app
        - information: general_query
        - conversation: greet, ask_status, thank, goodbye, chat

        Parameters to extract (use "null" if not applicable):
        - filename: name of the file to create/manage (e.g., "my_document.txt")
        - content: specific content for file creation (e.g., "hello world")
        - search_query: query for web searches (e.g., "latest news")
        - application: name of the application to open (e.g., "Google Chrome", "Spotify", "settings")
        - url: specific URL to open (e.g., "https://www.google.com")
        - message: general conversational or informational message (e.g., "how are you?")

        Example JSON format:
        {{
            "intent": "web_Browse",
            "action": "web_search",
            "parameters": {{
                "search_query": "weather in Paris",
                "filename": null,
                "content": null,
                "application": null,
                "url": null,
                "message": null
            }},
            "confidence": 0.98
        }}

        Example Command: "create a new python script called my_tool"
        Expected JSON:
        {{
            "intent": "file_creation",
            "action": "create_code",
            "parameters": {{
                "filename": "my_tool.py",
                "content": null,
                "search_query": null,
                "application": null,
                "url": null,
                "message": null
            }},
            "confidence": 0.95
        }}

        Example Command: "what is the capital of France"
        Expected JSON:
        {{
            "intent": "information",
            "action": "general_query",
            "parameters": {{
                "message": "what is the capital of France",
                "filename": null,
                "content": null,
                "search_query": null,
                "application": null,
                "url": null
            }},
            "confidence": 0.99
        }}

        Example Command: "open Google Chrome"
        Expected JSON:
        {{
            "intent": "system_control",
            "action": "open_app",
            "parameters": {{
                "application": "Google Chrome",
                "filename": null,
                "content": null,
                "search_query": null,
                "url": null,
                "message": null
            }},
            "confidence": 0.97
        }}
        
        Now, analyze the following command: "{command}"
        """
        try:
            response = self.gemini_client.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.2, # Lower temperature for more factual parsing
                    max_output_tokens=300
                ),
                safety_settings={ # Reduce strictness for general content responses
                    "HARASSMENT": "BLOCK_NONE",
                    "HATE_SPEECH": "BLOCK_NONE",
                    "SEXUALLY_EXPLICIT": "BLOCK_NONE",
                    "DANGEROUS_CONTENT": "BLOCK_NONE",
                }
            )
            result = json.loads(response.text)
            if isinstance(result.get("confidence"), (int, str)):
                result["confidence"] = float(result["confidence"])
            return result
        except GoogleAPIError as e:
            print(f"Gemini API error during analysis: {e}")
            return self._analyze_with_rules(command)
        except json.JSONDecodeError as e:
            print(f"JSON decoding error from Gemini response: {e}")
            print(f"Raw Gemini response (if available): {response.text}") # Print raw response to debug
            return self._analyze_with_rules(command)
        except Exception as e:
            print(f"Unexpected error in Gemini analysis: {e}")
            return self._analyze_with_rules(command)

    def _analyze_with_openai(self, command):
        """Analyze command using OpenAI."""
        prompt = f"""
        Analyze this command and return a JSON object with the detected intent, a specific action, and any relevant parameters.
        The response MUST be valid JSON, containing only the JSON object, and nothing else.

        Command: "{command}"

        Possible intents: file_creation, file_management, web_Browse, system_control, information, conversation

        Possible actions for each intent:
        - file_creation: create_website, create_code (e.g., python), create_text
        - file_management: list_files, open_file, delete_file, find_file
        - web_Browse: web_search, open_url
        - system_control: open_calculator, open_notepad, shutdown_system, restart_system, open_app
        - information: general_query
        - conversation: greet, ask_status, thank, goodbye, chat

        Parameters to extract (use "null" if not applicable):
        - filename: name of the file to create/manage
        - content: specific content for file creation
        - search_query: query for web searches
        - application: name of the application to open
        - url: specific URL to open
        - message: general conversational or informational message

        Example JSON format:
        {{
            "intent": "web_Browse",
            "action": "web_search",
            "parameters": {{
                "search_query": "weather in Paris",
                "filename": null,
                "content": null,
                "application": null,
                "url": null,
                "message": null
            }},
            "confidence": 0.98
        }}

        Example Command: "open Google Chrome"
        Expected JSON:
        {{
            "intent": "system_control",
            "action": "open_app",
            "parameters": {{
                "application": "Google Chrome",
                "filename": null,
                "content": null,
                "search_query": null,
                "url": null,
                "message": null
            }},
            "confidence": 0.97
        }}

        Now, analyze the following command: "{command}"
        """
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo-0125", # Use a recent, stable model
                messages=[
                    {"role": "system", "content": "You are a helpful assistant designed to extract intent and parameters from user commands and return them as a JSON object. Ensure the JSON is always valid and contains only the object."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}, # Instruct OpenAI to return JSON
                temperature=0.2, # Lower temperature for more factual parsing
                max_tokens=300 # Limit output length
            )
            result = json.loads(response.choices[0].message.content)
            if isinstance(result.get("confidence"), (int, str)):
                result["confidence"] = float(result["confidence"])
            return result
        except openai.APIError as e:
            print(f"OpenAI API error during analysis: {e}")
            return self._analyze_with_rules(command)
        except json.JSONDecodeError as e:
            print(f"JSON decoding error from OpenAI response: {e}")
            print(f"Raw OpenAI response (if available): {response.choices[0].message.content}")
            return self._analyze_with_rules(command)
        except Exception as e:
            print(f"Unexpected error in OpenAI analysis: {e}")
            return self._analyze_with_rules(command)
            
    def _analyze_with_rules(self, command):
        """Fallback rule-based analysis for basic commands."""
        command_lower = command.lower()

        # File creation patterns
        if any(word in command_lower for word in ['create', 'make', 'new', 'write', 'generate']):
            if 'website' in command_lower or 'html' in command_lower:
                return {
                    "intent": "file_creation",
                    "action": "create_website",
                    "parameters": {"type": "website", "filename": "jarvis_website.html", "content": None, "search_query": None, "application": None, "url": None, "message": None},
                    "confidence": 0.8
                }
            elif 'code' in command_lower or 'python' in command_lower:
                return {
                    "intent": "file_creation",
                    "action": "create_code",
                    "parameters": {"type": "python", "filename": "jarvis_script.py", "content": None, "search_query": None, "application": None, "url": None, "message": None},
                    "confidence": 0.8
                }
            elif 'text' in command_lower or 'note' in command_lower:
                return {
                    "intent": "file_creation",
                    "action": "create_text",
                    "parameters": {"type": "text", "filename": "jarvis_note.txt", "content": None, "search_query": None, "application": None, "url": None, "message": None},
                    "confidence": 0.8
                }

        # System control patterns
        elif any(word in command_lower for word in ['open', 'launch', 'start']):
            if 'calculator' in command_lower:
                return {
                    "intent": "system_control",
                    "action": "open_calculator",
                    "parameters": {"application": "calculator", "filename": None, "content": None, "search_query": None, "url": None, "message": None},
                    "confidence": 0.9
                }
            elif 'notepad' in command_lower or 'text editor' in command_lower:
                return {
                    "intent": "system_control",
                    "action": "open_notepad",
                    "parameters": {"application": "notepad", "filename": None, "content": None, "search_query": None, "url": None, "message": None},
                    "confidence": 0.9
                }
            elif 'settings' in command_lower:
                 return {
                    "intent": "system_control",
                    "action": "open_app",
                    "parameters": {"application": "settings", "filename": None, "content": None, "search_query": None, "url": None, "message": None},
                    "confidence": 0.7
                }
            elif 'chrome' in command_lower or 'google chrome' in command_lower:
                return {
                    "intent": "system_control",
                    "action": "open_app",
                    "parameters": {"application": "Google Chrome", "filename": None, "content": None, "search_query": None, "url": None, "message": None},
                    "confidence": 0.8
                }
            elif 'opera' in command_lower:
                return {
                    "intent": "system_control",
                    "action": "open_app",
                    "parameters": {"application": "Opera", "filename": None, "content": None, "search_query": None, "url": None, "message": None},
                    "confidence": 0.8
                }
            # Add more specific applications here if needed for rule-based fallback
            
        elif 'shutdown' in command_lower:
            return {
                "intent": "system_control",
                "action": "shutdown_system",
                "parameters": {"filename": None, "content": None, "search_query": None, "application": None, "url": None, "message": None},
                "confidence": 0.95
            }
        elif 'restart' in command_lower:
            return {
                "intent": "system_control",
                "action": "restart_system",
                "parameters": {"filename": None, "content": None, "search_query": None, "application": None, "url": None, "message": None},
                "confidence": 0.95
            }

        # Web Browse patterns
        elif any(word in command_lower for word in ['search', 'google', 'browse', 'go to website', 'find on web']):
            query_part = command_lower
            for phrase in ['search for', 'google', 'browse', 'go to website', 'find on web', 'search']:
                if phrase in query_part:
                    query_part = query_part.split(phrase, 1)[-1].strip()
            
            # Remove any trailing "in google" or "on the web"
            if query_part.endswith("in google"):
                query_part = query_part.replace("in google", "").strip()
            if query_part.endswith("on the web"):
                query_part = query_part.replace("on the web", "").strip()

            search_query = query_part if query_part and query_part != 'the' else None
            return {
                "intent": "web_Browse",
                "action": "web_search",
                "parameters": {"search_query": search_query, "filename": None, "content": None, "application": None, "url": None, "message": None},
                "confidence": 0.7
            }
        elif 'open' in command_lower and 'website' in command_lower:
            # Very basic URL extraction, would need regex for robust parsing
            url_part = command_lower.replace('open website', '').strip()
            if "." in url_part: # Simple check for domain
                return {
                    "intent": "web_Browse",
                    "action": "open_url",
                    "parameters": {"url": url_part, "filename": None, "content": None, "search_query": None, "application": None, "message": None},
                    "confidence": 0.8
                }
        
        # File management patterns
        elif 'list files' in command_lower or 'show files' in command_lower:
            return {
                "intent": "file_management",
                "action": "list_files",
                "parameters": {"filename": None, "content": None, "search_query": None, "application": None, "url": None, "message": None},
                "confidence": 0.85
            }
        elif 'open file' in command_lower:
            filename = command_lower.replace('open file', '').strip()
            return {
                "intent": "file_management",
                "action": "open_file",
                "parameters": {"filename": filename if filename else None, "content": None, "search_query": None, "application": None, "url": None, "message": None},
                "confidence": 0.7
            }

        # Information request patterns
        elif any(word in command_lower for word in ['what is', 'how to', 'tell me about', 'explain', 'who is', 'define', 'how is the weather']):
            return {
                "intent": "information",
                "action": "general_query",
                "parameters": {"message": command, "filename": None, "content": None, "search_query": None, "application": None, "url": None},
                "confidence": 0.6
            }

        # Default conversation
        return {
            "intent": "conversation",
            "action": "chat",
            "parameters": {"message": command, "filename": None, "content": None, "search_query": None, "application": None, "url": None},
            "confidence": 0.5
        }

    # Removed _extract_action and _extract_parameters as they are now handled by AI or simpler rules

    def execute_command(self, analysis):
        """Execute the analyzed command."""
        intent = analysis.get("intent")
        action = analysis.get("action")
        params = analysis.get("parameters", {}) # Ensure params is a dict, default to empty

        if not intent or not action:
            return "I couldn't understand that command. Please try again."

        try:
            if intent == "file_creation":
                return self._handle_file_creation(action, params)
            elif intent == "system_control":
                return self._handle_system_control(action, params)
            elif intent == "web_Browse":
                return self._handle_web_Browse(action, params)
            elif intent == "file_management":
                return self._handle_file_management(action, params)
            elif intent == "information":
                return self._handle_information_request(params)
            elif intent == "conversation":
                return self._handle_conversation(params)
            else:
                return "I'm not sure how to help with that specific request."

        except Exception as e:
            return f"Error executing command: {e}"

    def _handle_file_creation(self, action, params):
        """Handle file creation commands."""
        filename = params.get("filename")
        if not filename:
            # Try to infer default filename if not provided by AI
            if action == "create_website": filename = "jarvis_website.html"
            elif action == "create_code": filename = "jarvis_script.py"
            elif action == "create_text": filename = "jarvis_note.txt"
            else: return "Please specify the filename or type for creation."

        # Basic filename sanitization to prevent directory traversal
        filename = Path(filename).name # Takes only the last component of the path

        filepath = self.workspace_dir / filename

        if action == "create_website":
            html_content = """<!DOCTYPE html>
<html><head><title>JARVIS Created Website</title></head>
<body><h1>Website Created by JARVIS</h1>
<p>This website was created by your AI assistant.</p></body></html>"""
            with open(filepath, 'w') as f:
                f.write(html_content)
            webbrowser.open(f"file://{filepath}")
            return f"Website '{filename}' created and opened."

        elif action == "create_code":
            code_content = f'''# Python script created by JARVIS
# Created: {datetime.now()}

def main():
    print("Hello from JARVIS!")
    
if __name__ == "__main__":
    main()
'''
            with open(filepath, 'w') as f:
                f.write(code_content)
            self._open_file_in_editor(filepath)
            return f"Python script '{filename}' created."

        elif action == "create_text":
            text_content = f"Text file created by JARVIS\nDate: {datetime.now()}\n\nYour content here..."
            with open(filepath, 'w') as f:
                f.write(text_content)
            self._open_file_in_editor(filepath)
            return f"Text file '{filename}' created."

        return "File creation completed."

    def _open_file_in_editor(self, filepath):
        """Helper to open files in a default editor based on OS."""
        try:
            if self.system == "windows":
                # Using 'start' command for general file opening
                subprocess.Popen(["start", str(filepath)], shell=True) 
            elif self.system == "linux":
                # Use shutil.which to find common editors
                if shutil.which("xdg-open"):
                    subprocess.Popen(["xdg-open", str(filepath)])
                elif shutil.which("gedit"):
                    subprocess.Popen(["gedit", str(filepath)])
                elif shutil.which("nano"):
                    subprocess.Popen(["nano", str(filepath)])
                else:
                    print(f"Cannot automatically open file on Linux. No suitable editor found.")
            elif self.system == "darwin": # macOS
                subprocess.Popen(["open", str(filepath)])
            else:
                print(f"Cannot automatically open file on {self.system}")
        except Exception as e:
            print(f"Could not open file '{filepath}' in editor: {e}")

    def _handle_system_control(self, action, params):
        """Handle system control commands."""
        app_name = params.get("application", "").lower()

        if action == "open_calculator":
            try:
                if self.system == "windows":
                    subprocess.Popen(["calc"])
                elif self.system == "linux":
                    if shutil.which("gnome-calculator"): subprocess.Popen(["gnome-calculator"])
                    elif shutil.which("kcalc"): subprocess.Popen(["kcalc"])
                    elif shutil.which("xcalc"): subprocess.Popen(["xcalc"])
                    else: return "Could not find a calculator application."
                else: # macOS
                    subprocess.Popen(["open", "-a", "Calculator"])
                return "Calculator opened."
            except Exception as e:
                return f"Could not open calculator: {e}"

        elif action == "open_notepad":
            try:
                if self.system == "windows":
                    subprocess.Popen(["notepad"])
                elif self.system == "linux":
                    if shutil.which("gedit"): subprocess.Popen(["gedit"])
                    elif shutil.which("nano"): subprocess.Popen(["nano"])
                    elif shutil.which("vi"): subprocess.Popen(["vi"])
                    else: return "Could not find a text editor application."
                else: # macOS
                    subprocess.Popen(["open", "-a", "TextEdit"])
                return "Text editor opened."
            except Exception as e:
                return f"Could not open text editor: {e}"
        
        elif action == "open_app":
            if not app_name:
                return "Please specify which application to open."
            try:
                if self.system == "windows":
                    # Use shell=True for common applications like "chrome.exe" or "notepad.exe"
                    subprocess.Popen([app_name], shell=True) 
                elif self.system == "linux":
                    subprocess.Popen([app_name])
                elif self.system == "darwin":
                    subprocess.Popen(["open", "-a", app_name])
                return f"Attempted to open {app_name}."
            except FileNotFoundError:
                return f"Application '{app_name}' not found."
            except Exception as e:
                return f"Could not open {app_name}: {e}"

        elif action == "shutdown_system":
            self.speak("Are you sure you want to shut down the system? This will close all your programs.")
            confirmation = self.listen()
            if confirmation and ("yes" in confirmation or "confirm" in confirmation):
                if self.system == "windows":
                    subprocess.Popen(["shutdown", "/s", "/t", "1"])
                elif self.system == "linux" or self.system == "darwin":
                    subprocess.Popen(["sudo", "shutdown", "-h", "now"])
                return "System is shutting down."
            else:
                return "Shutdown aborted."

        elif action == "restart_system":
            self.speak("Are you sure you want to restart the system? This will close all your programs.")
            confirmation = self.listen()
            if confirmation and ("yes" in confirmation or "confirm" in confirmation):
                if self.system == "windows":
                    subprocess.Popen(["shutdown", "/r", "/t", "1"])
                elif self.system == "linux" or self.system == "darwin":
                    subprocess.Popen(["sudo", "reboot"])
                return "System is restarting."
            else:
                return "Restart aborted."

        return "System command executed."

    def _handle_web_Browse(self, action, params):
        """Handle web Browse commands."""
        search_query = params.get("search_query")
        url_to_open = params.get("url")

        if action == "web_search" and search_query:
            search_url = f"https://www.google.com/search?q={requests.utils.quote(search_query)}" # URL encode query
            webbrowser.open(search_url)
            return f"Searching for: {search_query}."
        elif action == "open_url" and url_to_open:
            # Basic URL validation/prefixing for safety and robustness
            if not (url_to_open.startswith("http://") or url_to_open.startswith("https://")):
                url_to_open = "https://" + url_to_open # Default to HTTPS
            webbrowser.open(url_to_open)
            return f"Opening website: {url_to_open}."
        else:
            webbrowser.open("https://www.google.com")
            return "Opened Google."

    def _handle_file_management(self, action, params):
        """Handle file management commands."""
        filename = params.get("filename")

        if action == "list_files":
            try:
                files = list(self.workspace_dir.iterdir()) # Use iterdir for more efficient listing
                if files:
                    file_list = "\n".join([f"📄 {f.name}" for f in files])
                    return f"Files in workspace:\n{file_list}"
                else:
                    return "Workspace is empty."
            except Exception as e:
                return f"Error listing files: {e}"

        elif action == "open_file" and filename:
            filepath = self.workspace_dir / filename
            if filepath.exists() and filepath.is_file():
                self._open_file_in_editor(filepath)
                return f"Opening file: {filename}."
            else:
                return f"File '{filename}' not found in workspace."
        # Add more file management actions (delete, move, etc.) here
        return "File management command completed."

    def _handle_information_request(self, params):
        """Handle information requests using external AI models."""
        message = params.get("message", "")
        if not message:
            return "I need more information to answer your question."

        try:
            if self.gemini_client:
                # Use Gemini for information requests
                response = self.gemini_client.generate_content(
                    f"Answer the following question concisely and informatively: {message}",
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=300,
                        temperature=0.7 # Allow some creativity for information
                    ),
                    safety_settings={
                        "HARASSMENT": "BLOCK_NONE", "HATE_SPEECH": "BLOCK_NONE",
                        "SEXUALLY_EXPLICIT": "BLOCK_NONE", "DANGEROUS_CONTENT": "BLOCK_NONE",
                    }
                )
                return response.text
            elif self.openai_client:
                # Fallback to OpenAI if Gemini is not available
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo-0125",
                    messages=[{"role": "user", "content": message}],
                    max_tokens=300,
                    temperature=0.7
                )
                return response.choices[0].message.content
            
        except (GoogleAPIError, openai.APIError) as e:
            print(f"API error during information request: {e}")
            return "I'm having trouble connecting to the AI to answer that question. Please check my API key or internet connection."
        except Exception as e:
            print(f"Error handling information request: {e}")
            return "I'm sorry, I couldn't process that information request."

        return "I need an external AI model or internet connection to answer that question."

    def _handle_conversation(self, params):
        """Handle conversational responses."""
        message = params.get("message", "").lower()

        if any(greeting in message for greeting in ["hello", "hi", "hey"]):
            return "Hello! I'm JARVIS, your AI assistant. How can I help you today?"
        elif "how are you" in message:
            return "I'm functioning optimally and ready to assist you!"
        elif any(thanks in message for thanks in ["thank you", "thanks", "appreciate it"]):
            return "You're very welcome! Happy to help."
        elif any(bye in message for bye in ["goodbye", "bye", "see you", "farewell"]):
            return "Goodbye! Feel free to call me anytime."
        else:
            # For general chat, try AI first, then local, then default
            try:
                if self.gemini_client:
                    response = self.gemini_client.generate_content(
                        f"Respond conversationally to: '{message}'",
                        generation_config=genai.types.GenerationConfig(
                            max_output_tokens=100,
                            temperature=0.9 # More creative for conversation
                        ),
                        safety_settings={
                            "HARASSMENT": "BLOCK_NONE", "HATE_SPEECH": "BLOCK_NONE",
                            "SEXUALLY_EXPLICIT": "BLOCK_NONE", "DANGEROUS_CONTENT": "BLOCK_NONE",
                        }
                    )
                    return response.text
                elif self.openai_client:
                    response = self.openai_client.chat.completions.create(
                        model="gpt-3.5-turbo-0125",
                        messages=[{"role": "user", "content": message}],
                        max_tokens=100,
                        temperature=0.9
                    )
                    return response.choices[0].message.content
            except (GoogleAPIError, openai.APIError) as e:
                print(f"API error during conversational response: {e}")
                return "I'm having a little trouble with my external AI connection right now. How else can I help?"
            except Exception as e:
                print(f"Error in conversational AI response: {e}")
                return "I'm not quite sure how to respond to that, but I'm learning!"

        return "I'm here to help. You can ask me to create files, open applications, search the web, or answer questions."

    def run(self):
        """Main execution loop."""
        self.speak("JARVIS AI Assistant activated. How may I assist you?")

        while True:
            try:
                print("\n" + "="*50)
                print("🎤 Say 'hey jarvis' or type your command:")

                command = None
                # Check for voice activation
                voice_command = self.listen()
                if voice_command:
                    if "hey jarvis" in voice_command:
                        command = voice_command.replace("hey jarvis", "").strip()
                        if not command:
                            self.speak("Yes, I'm listening. What would you like me to do?")
                            command = self.listen() # Listen again for the actual command
                    else: # If a voice command was given but didn't contain "hey jarvis"
                        print("Voice command received, but 'hey jarvis' not detected. Treating as direct command.")
                        command = voice_command # Process it as a direct command

                # If no command from voice, fall back to text input
                if not command:
                    command = input("💬 Type command (or 'exit' to quit): ").strip()

                if not command: # If command is still empty after listening/typing
                    continue

                if command.lower() in ['exit', 'quit', 'shutdown jarvis', 'goodbye jarvis']:
                    self.speak("Shutting down JARVIS. Goodbye!")
                    break

                # Analyze and execute command
                print(f"🔍 Analyzing: {command}")
                analysis = self.analyze_command_with_ai(command)
                print(f"📊 Intent: {analysis.get('intent')} | Action: {analysis.get('action')} | Confidence: {analysis.get('confidence'):.2f}")
                print(f"📦 Parameters: {analysis.get('parameters')}")

                result = self.execute_command(analysis)
                self.speak(result)

            except KeyboardInterrupt:
                self.speak("JARVIS shutting down by user request.")
                break
            except Exception as e:
                error_msg = f"An unexpected error occurred: {e}"
                print(f"❌ {error_msg}")
                self.speak("Sorry, I encountered an unexpected error.")


def main():
    """Launch JARVIS AI Assistant."""
    print("🚀 Initializing JARVIS AI Assistant...")
    print("📋 Make sure you have the following packages installed:")
    print("   pip install speechrecognition pyttsx3 openai google-generativeai python-dotenv Pillow requests")
    print("🔑 For enhanced AI features, set environment variables:")
    print("   export OPENAI_API_KEY=\"your_openai_key_here\"")
    print("   export GEMINI_API_KEY=\"your_gemini_key_here\"")
    print("   (Or create a .env file in the same directory: OPENAI_API_KEY=\"...\", GEMINI_API_KEY=\"...\")")

    try:
        # Check for essential packages more robustly
        import speech_recognition
        import pyttsx3
        import openai
        import google.generativeai
        import requests
        import shutil # Check for shutil, important for Linux app opening

        jarvis = JarvisAI()
        jarvis.run()
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install all necessary packages using: pip install speechrecognition pyttsx3 openai google-generativeai python-dotenv Pillow requests")
    except Exception as e:
        print(f"❌ Error starting JARVIS: {e}")

if __name__ == "__main__":
    main()
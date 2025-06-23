"""
JARVIS-Style AI Assistant with Natural Language Processing
Connects to AI models for intelligent command understanding
"""

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
import requests
import openai
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch

class JarvisAI:
    def __init__(self):
        self.system = platform.system().lower()
        self.workspace_dir = Path.home() / "JARVIS_Workspace"
        self.workspace_dir.mkdir(exist_ok=True)
        
        # Initialize speech
        self.tts_engine = pyttsx3.init()
        self.speech_recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # AI Model configurations
        self.openai_client = None
        self.local_model = None
        self.nlp_classifier = None
        
        # Command categories and their associated actions
        self.command_categories = {
            'file_creation': ['create', 'make', 'new', 'write', 'generate'],
            'file_management': ['open', 'show', 'list', 'find', 'search'],
            'web_browsing': ['browse', 'search web', 'google', 'website', 'url'],
            'system_control': ['calculator', 'notepad', 'settings', 'shutdown', 'restart'],
            'information': ['what', 'how', 'when', 'where', 'why', 'tell me', 'explain'],
            'conversation': ['hello', 'hi', 'how are you', 'thank you', 'goodbye']
        }
        
        self.setup_ai_models()
        print(f"🤖 JARVIS AI Assistant initialized")
        print(f"💻 System: {platform.system()}")
        print(f"🏠 Workspace: {self.workspace_dir}")
    
    def setup_ai_models(self):
        """Initialize AI models for NLP processing"""
        try:
            # Try to load local transformers model for command classification
            print("🔧 Loading NLP models...")
            self.nlp_classifier = pipeline(
                "text-classification",
                model="microsoft/DialoGPT-medium",
                return_all_scores=True
            )
            
            # Setup OpenAI if API key available
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key:
                self.openai_client = openai.OpenAI(api_key=openai_key)
                print("✅ OpenAI API connected")
            
            # Try loading local model
            try:
                self.local_model = pipeline(
                    "text-generation",
                    model="microsoft/DialoGPT-small",
                    tokenizer="microsoft/DialoGPT-small"
                )
                print("✅ Local AI model loaded")
            except:
                print("⚠️ Local model not available")
                
        except Exception as e:
            print(f"⚠️ AI models setup error: {e}")
            print("📝 Will use rule-based processing as fallback")
    
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
                self.speech_recognizer.adjust_for_ambient_noise(source)
                audio = self.speech_recognizer.listen(source, timeout=5)
            
            command = self.speech_recognizer.recognize_google(audio)
            print(f"🗣️ You said: {command}")
            return command.lower()
        
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            self.speak("I didn't catch that. Could you repeat?")
            return None
        except Exception as e:
            print(f"❌ Speech recognition error: {e}")
            return None
    
    def analyze_command_with_ai(self, command):
        """Use AI to understand the command intent and extract parameters"""
        try:
            if self.openai_client:
                return self._analyze_with_openai(command)
            elif self.local_model:
                return self._analyze_with_local_model(command)
            else:
                return self._analyze_with_rules(command)
        except Exception as e:
            print(f"❌ AI analysis error: {e}")
            return self._analyze_with_rules(command)
    
    def _analyze_with_openai(self, command):
        """Analyze command using OpenAI"""
        prompt = f"""
        Analyze this command and return a JSON response with the intent and parameters:
        Command: "{command}"
        
        Possible intents: file_creation, file_management, web_browsing, system_control, information, conversation
        
        Return format:
        {{
            "intent": "intent_name",
            "action": "specific_action",
            "parameters": {{
                "filename": "if applicable",
                "content": "if applicable", 
                "search_query": "if applicable",
                "application": "if applicable"
            }},
            "confidence": 0.95
        }}
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            print(f"OpenAI analysis error: {e}")
            return self._analyze_with_rules(command)
    
    def _analyze_with_local_model(self, command):
        """Analyze command using local transformer model"""
        # This is a simplified version - you'd want to fine-tune a model for intent classification
        intent_keywords = {
            'file_creation': ['create', 'make', 'new', 'write', 'generate', 'build'],
            'file_management': ['open', 'show', 'list', 'find', 'delete', 'move'],
            'web_browsing': ['search', 'google', 'browse', 'website', 'internet'],
            'system_control': ['calculator', 'notepad', 'settings', 'volume', 'shutdown'],
            'information': ['what', 'how', 'when', 'where', 'why', 'tell me', 'explain']
        }
        
        # Score each intent
        scores = {}
        for intent, keywords in intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in command.lower())
            scores[intent] = score / len(keywords)
        
        best_intent = max(scores, key=scores.get)
        confidence = scores[best_intent]
        
        return {
            "intent": best_intent,
            "action": self._extract_action(command, best_intent),
            "parameters": self._extract_parameters(command, best_intent),
            "confidence": confidence
        }
    
    def _analyze_with_rules(self, command):
        """Fallback rule-based analysis"""
        command_lower = command.lower()
        
        # File creation patterns
        if any(word in command_lower for word in ['create', 'make', 'new', 'write']):
            if 'website' in command_lower or 'html' in command_lower:
                return {
                    "intent": "file_creation",
                    "action": "create_website",
                    "parameters": {"type": "website"},
                    "confidence": 0.8
                }
            elif 'code' in command_lower or 'python' in command_lower:
                return {
                    "intent": "file_creation", 
                    "action": "create_code",
                    "parameters": {"type": "python"},
                    "confidence": 0.8
                }
            elif 'text' in command_lower or 'note' in command_lower:
                return {
                    "intent": "file_creation",
                    "action": "create_text",
                    "parameters": {"type": "text"},
                    "confidence": 0.8
                }
        
        # System control patterns
        elif any(word in command_lower for word in ['open', 'launch', 'start']):
            if 'calculator' in command_lower:
                return {
                    "intent": "system_control",
                    "action": "open_calculator", 
                    "parameters": {"application": "calculator"},
                    "confidence": 0.9
                }
            elif 'notepad' in command_lower:
                return {
                    "intent": "system_control",
                    "action": "open_notepad",
                    "parameters": {"application": "notepad"},
                    "confidence": 0.9
                }
        
        # Web browsing patterns
        elif any(word in command_lower for word in ['search', 'google', 'browse']):
            return {
                "intent": "web_browsing",
                "action": "web_search",
                "parameters": {"query": command_lower.replace('search', '').replace('google', '').strip()},
                "confidence": 0.7
            }
        
        # Default conversation
        return {
            "intent": "conversation",
            "action": "chat",
            "parameters": {"message": command},
            "confidence": 0.5
        }
    
    def _extract_action(self, command, intent):
        """Extract specific action from command"""
        command_lower = command.lower()
        
        if intent == "file_creation":
            if 'website' in command_lower: return "create_website"
            elif 'code' in command_lower: return "create_code"
            elif 'text' in command_lower: return "create_text"
            else: return "create_file"
        
        elif intent == "system_control":
            if 'calculator' in command_lower: return "open_calculator"
            elif 'notepad' in command_lower: return "open_notepad"
            else: return "system_action"
        
        elif intent == "web_browsing":
            return "web_search"
        
        return "general_action"
    
    def _extract_parameters(self, command, intent):
        """Extract parameters from command"""
        params = {}
        
        if intent == "web_browsing":
            # Extract search query
            query = command.lower()
            for remove_word in ['search', 'google', 'find', 'look up']:
                query = query.replace(remove_word, '')
            params["query"] = query.strip()
        
        return params
    
    def execute_command(self, analysis):
        """Execute the analyzed command"""
        intent = analysis["intent"]
        action = analysis["action"]
        params = analysis["parameters"]
        
        try:
            if intent == "file_creation":
                return self._handle_file_creation(action, params)
            elif intent == "system_control":
                return self._handle_system_control(action, params)
            elif intent == "web_browsing":
                return self._handle_web_browsing(action, params)
            elif intent == "file_management":
                return self._handle_file_management(action, params)
            elif intent == "information":
                return self._handle_information_request(params)
            elif intent == "conversation":
                return self._handle_conversation(params)
            else:
                return "I'm not sure how to help with that."
        
        except Exception as e:
            return f"Error executing command: {e}"
    
    def _handle_file_creation(self, action, params):
        """Handle file creation commands"""
        if action == "create_website":
            html_content = """<!DOCTYPE html>
<html><head><title>JARVIS Created Website</title></head>
<body><h1>Website Created by JARVIS</h1>
<p>This website was created by your AI assistant.</p></body></html>"""
            
            filepath = self.workspace_dir / "jarvis_website.html"
            with open(filepath, 'w') as f:
                f.write(html_content)
            
            webbrowser.open(f"file://{filepath}")
            return f"Website created and opened: {filepath}"
        
        elif action == "create_code":
            code_content = f'''# Python script created by JARVIS
# Created: {datetime.now()}

def main():
    print("Hello from JARVIS!")
    
if __name__ == "__main__":
    main()
'''
            filepath = self.workspace_dir / "jarvis_script.py"
            with open(filepath, 'w') as f:
                f.write(code_content)
            
            # Try to open in code editor
            try:
                if self.system == "windows":
                    subprocess.Popen(["notepad", str(filepath)])
                else:
                    subprocess.Popen(["nano", str(filepath)])
            except:
                pass
            
            return f"Python script created: {filepath}"
        
        elif action == "create_text":
            text_content = f"Text file created by JARVIS\nDate: {datetime.now()}\n\nYour content here..."
            filepath = self.workspace_dir / "jarvis_note.txt"
            with open(filepath, 'w') as f:
                f.write(text_content)
            
            try:
                if self.system == "windows":
                    subprocess.Popen(["notepad", str(filepath)])
                else:
                    subprocess.Popen(["nano", str(filepath)])
            except:
                pass
            
            return f"Text file created: {filepath}"
        
        return "File creation completed"
    
    def _handle_system_control(self, action, params):
        """Handle system control commands"""
        if action == "open_calculator":
            try:
                if self.system == "windows":
                    subprocess.Popen(["calc"])
                elif self.system == "linux":
                    subprocess.Popen(["gnome-calculator"])
                else:
                    subprocess.Popen(["open", "-a", "Calculator"])
                return "Calculator opened"
            except:
                return "Could not open calculator"
        
        elif action == "open_notepad":
            try:
                if self.system == "windows":
                    subprocess.Popen(["notepad"])
                elif self.system == "linux":
                    subprocess.Popen(["gedit"])
                else:
                    subprocess.Popen(["open", "-a", "TextEdit"])
                return "Text editor opened"
            except:
                return "Could not open text editor"
        
        return "System command executed"
    
    def _handle_web_browsing(self, action, params):
        """Handle web browsing commands"""
        if action == "web_search":
            query = params.get("query", "")
            if query:
                search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                webbrowser.open(search_url)
                return f"Searching for: {query}"
            else:
                webbrowser.open("https://www.google.com")
                return "Opened Google"
        
        return "Web browsing completed"
    
    def _handle_file_management(self, action, params):
        """Handle file management commands"""
        files = list(self.workspace_dir.glob("*"))
        if files:
            file_list = "\n".join([f"📄 {f.name}" for f in files])
            return f"Files in workspace:\n{file_list}"
        else:
            return "Workspace is empty"
    
    def _handle_information_request(self, params):
        """Handle information requests"""
        if self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": params.get("message", "")}],
                    max_tokens=150
                )
                return response.choices[0].message.content
            except:
                pass
        
        return "I'd need an internet connection or AI model to answer that question."
    
    def _handle_conversation(self, params):
        """Handle conversational responses"""
        message = params.get("message", "").lower()
        
        if any(greeting in message for greeting in ["hello", "hi", "hey"]):
            return "Hello! I'm JARVIS, your AI assistant. How can I help you today?"
        elif "how are you" in message:
            return "I'm functioning optimally and ready to assist you!"
        elif any(thanks in message for thanks in ["thank you", "thanks"]):
            return "You're welcome! Happy to help."
        elif any(bye in message for bye in ["goodbye", "bye", "see you"]):
            return "Goodbye! Feel free to call me anytime."
        else:
            return "I'm here to help. You can ask me to create files, open applications, search the web, or answer questions."
    
    def run(self):
        """Main execution loop"""
        self.speak("JARVIS AI Assistant activated. How may I assist you?")
        
        while True:
            try:
                print("\n" + "="*50)
                print("🎤 Say 'hey jarvis' or type your command:")
                
                # Check for voice activation
                voice_command = self.listen()
                if voice_command and "hey jarvis" in voice_command:
                    command = voice_command.replace("hey jarvis", "").strip()
                    if not command:
                        self.speak("Yes, I'm listening. What would you like me to do?")
                        command = self.listen()
                else:
                    # Text input fallback
                    command = input("💬 Type command (or 'exit' to quit): ").strip()
                
                if not command:
                    continue
                    
                if command.lower() in ['exit', 'quit', 'shutdown', 'goodbye']:
                    self.speak("Shutting down JARVIS. Goodbye!")
                    break
                
                # Analyze and execute command
                print(f"🔍 Analyzing: {command}")
                analysis = self.analyze_command_with_ai(command)
                print(f"📊 Intent: {analysis['intent']} | Confidence: {analysis['confidence']:.2f}")
                
                result = self.execute_command(analysis)
                self.speak(result)
                
            except KeyboardInterrupt:
                self.speak("JARVIS shutting down")
                break
            except Exception as e:
                error_msg = f"Error occurred: {e}"
                print(f"❌ {error_msg}")
                self.speak("Sorry, I encountered an error.")


def main():
    """Launch JARVIS AI Assistant"""
    print("🚀 Initializing JARVIS AI Assistant...")
    print("📋 Requirements: pip install speechrecognition pyttsx3 transformers torch openai")
    print("🔑 Optional: Set OPENAI_API_KEY environment variable for enhanced AI features")
    
    try:
        jarvis = JarvisAI()
        jarvis.run()
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("📦 Install required packages: pip install speechrecognition pyttsx3 transformers torch openai")
    except Exception as e:
        print(f"❌ Error starting JARVIS: {e}")

if __name__ == "__main__":
    main()
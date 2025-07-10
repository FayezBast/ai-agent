# ai_core.py
import os
import re
import json
from typing import Dict, Any, List

import google.generativeai as genai
from config import Config
from security import SecurityValidator
from logger import log_info, log_error, log_warning

class AI_Core:
    """Handles AI-powered content generation and command analysis."""
    
    def __init__(self, api_key: str):
        self.gemini_client = None
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.gemini_client = genai.GenerativeModel('gemini-1.5-flash-latest')
                log_info("Google Gemini AI initialized successfully.")
            except Exception as e:
                log_error(f"Failed to initialize Gemini AI: {e}")
        else:
            log_warning("Gemini AI not initialized: API key is missing.")

    # Note: LRU cache is removed because the 'history' list is unhashable.
    def analyze_command(self, command: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Analyzes the user command using AI to determine intent, action, and parameters,
        taking into account the conversation history for context.
        """
        if not self.gemini_client:
            log_warning("AI analysis skipped: Gemini client not available.")
            return self._analyze_with_rules(command)

        # Format the history for the prompt
        formatted_history = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in history])

        # NEW: Expanded prompt with all new actions and context memory
        prompt = f"""
        You are the core logic of the JARVIS AI assistant. Analyze the user's command in the context of the conversation history.

        CONVERSATION HISTORY:
        {formatted_history}
        
        LATEST USER COMMAND: "{command}"

        First, determine if the command is a task or a general conversation/question.

        1. If it's a task, identify the 'intent' and 'action'.
           - Valid Intents: {', '.join(Config.VALID_INTENTS)}, knowledge_inquiry, system_status, clipboard_management, weather_inquiry
           - Action mapping examples:
             - "create word doc" -> intent: 'file_creation', action: 'create_word'
             - "list files" -> intent: 'file_management', action: 'list_files'
             - "open chrome" -> intent: 'system_control', action: 'open_application'
             - "search for AI" -> intent: 'web_browse', action: 'web_search'
             - "what is the weather in Paris" -> intent: 'weather_inquiry', action: 'get_weather', parameters: {{"city": "Paris"}}
             - "tell me about Jupiter" -> intent: 'knowledge_inquiry', action: 'get_summary', parameters: {{"topic": "Jupiter"}}
             - "what is my cpu usage" -> intent: 'system_status', action: 'get_system_status', parameters: {{"status_type": "cpu"}}
             - "take a screenshot" -> intent: 'system_control', action: 'take_screenshot'
             - "read my clipboard" -> intent: 'clipboard_management', action: 'read_clipboard'
             - "copy 'hello' to clipboard" -> intent: 'clipboard_management', action: 'write_clipboard', parameters: {{"text": "hello"}}
             - "help" -> intent: 'help', action: 'show_help'
           - Extract all relevant 'parameters'.
           - Set 'response' to null.

        2. If it's a general question, chat, or a follow-up without a clear action:
           - Set 'intent' to 'conversation'.
           - Set 'action' to 'chat'.
           - Generate a helpful answer in the 'response' field, using the history for context.

        **IMPORTANT**: Respond with ONLY a single, valid JSON object and nothing else.
        """
        
        try:
            response = self.gemini_client.generate_content(prompt)
            json_text = re.search(r'\{.*\}', response.text, re.DOTALL).group(0)
            analysis = json.loads(json_text)
            return analysis
        except Exception as e:
            log_error(f"AI command analysis failed: {e}. Falling back to rule-based analysis.")
            return self._analyze_with_rules(command)

    def generate_file_content(self, topic: str, file_type: str) -> str:
        # This method remains the same
        if not self.gemini_client:
            log_warning("AI content generation skipped.")
            return f"This is a placeholder {file_type} file about {topic}."
        # ... (rest of the method is unchanged)
        content_prompts = {
            'json': f"Generate a realistic and useful JSON structure about '{topic}'. The JSON should have 'headers' (a list of strings) and 'rows' (a list of lists). Respond with only the raw JSON content.",
            'code': f"Write a complete, well-documented Python script for: '{topic}'. Include error handling and comments. The script should be functional and stand-alone. Respond with only the raw Python code.",
            'text': f"Write a comprehensive, well-structured document about '{topic}'. Use Markdown for formatting (e.g., # Headings, **bold**, * bullets).",
        }
        prompt = content_prompts.get(file_type, content_prompts['text'])
        try:
            response = self.gemini_client.generate_content(prompt)
            content = response.text.strip()
            if file_type == 'code' and content.startswith('```python'):
                content = content[9:].replace('```', '').strip()
            return SecurityValidator.sanitize_content(content)
        except Exception as e:
            log_error(f"AI content generation failed: {e}")
            return f"This is a placeholder {file_type} file about {topic}."

    def _analyze_with_rules(self, command: str) -> Dict[str, Any]:
        # This method remains the same
        cmd = command.lower().strip()
        if "create" in cmd or "make" in cmd:
            return {"intent": "file_creation", "action": "create_text", "parameters": {"content_topic": cmd.replace("create", "").strip()}, "response": None}
        if "list files" in cmd:
            return {"intent": "file_management", "action": "list_files", "parameters": {}, "response": None}
        if "help" in cmd:
             return {"intent": "help", "action": "show_help", "parameters": {}, "response": None}
        return {"intent": "conversation", "action": "chat", "parameters": {}, "response": "I'm having trouble connecting to my advanced reasoning circuits. Can you please rephrase?"}
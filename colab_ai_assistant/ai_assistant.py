"""
Main AI Assistant class for Google Colab environment
"""

import os
from creators.text_creator import TextCreator
from creators.website_creator import WebsiteCreator
from creators.code_creator import CodeCreator
from creators.json_creator import JsonCreator
from utils.file_manager import FileManager
from utils.display import show_help

class ColabAIAssistant:
    def __init__(self, model_manager):
        self.model_manager = model_manager
        self.workspace_dir = "/content/ai_workspace"
        os.makedirs(self.workspace_dir, exist_ok=True)
        
        # Initialize creators
        self.text_creator = TextCreator(self.workspace_dir)
        self.website_creator = WebsiteCreator(self.workspace_dir)
        self.code_creator = CodeCreator(self.workspace_dir)
        self.json_creator = JsonCreator(self.workspace_dir)
        self.file_manager = FileManager(self.workspace_dir)
        
        print(f"🏠 Workspace created at: {self.workspace_dir}")
    
    def process_command(self, user_input: str):
        """Process user commands and take appropriate actions"""
        user_input = user_input.lower().strip()
        
        # Command mapping for Colab environment
        if "notepad" in user_input or "text file" in user_input:
            return self.text_creator.create_text_file()
        
        elif "website" in user_input or "html" in user_input:
            return self.website_creator.create_website()
        
        elif "code" in user_input or "python" in user_input:
            return self.code_creator.create_code_file()
        
        elif "json" in user_input or "data" in user_input:
            return self.json_creator.create_json_file()
        
        elif "list files" in user_input:
            return self.file_manager.list_files()
        
        elif "help" in user_input:
            return show_help()
        
        else:
            return self.generate_ai_response(user_input)
    
    def generate_ai_response(self, user_input: str):
        """Generate AI response using loaded models"""
        if not self.model_manager.models:
            return "🤖 No AI models loaded. Please load a model first using model_manager.upload_model_complete()"
        
        # Use the first available model
        model_name = list(self.model_manager.models.keys())[0]
        response = self.model_manager.use_model(model_name, user_input)
        
        return response
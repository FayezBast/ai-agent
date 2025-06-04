"""
JSON file creator for the AI Assistant
"""

import os
import json
from datetime import datetime

class JsonCreator:
    def __init__(self, workspace_dir):
        self.workspace_dir = workspace_dir
    
    def create_json_file(self):
        """Create a JSON data file"""
        data_type = input("📊 What type of data? (config/data/api): ") or "data"
        filename = input("📄 Enter filename (default: data.json): ") or "data.json"
        
        if not filename.endswith('.json'):
            filename += '.json'
        
        sample_data = self._generate_sample_data(data_type)
        
        filepath = os.path.join(self.workspace_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(sample_data, f, indent=2)
        
        print(f"✅ JSON file created: {filepath}")
        print("📋 JSON content:")
        print(json.dumps(sample_data, indent=2))
        
        return f"JSON file '{filename}' created successfully!"
    
    def _generate_sample_data(self, data_type):
        """Create sample data based on type"""
        if data_type == "config":
            return {
                "app_name": "My Application",
                "version": "1.0.0",
                "settings": {
                    "debug": True,
                    "max_connections": 100
                },
                "created": datetime.now().isoformat()
            }
        elif data_type == "api":
            return {
                "api_endpoint": "https://api.example.com",
                "auth_token": "your_token_here",
                "timeout": 30,
                "retry_attempts": 3
            }
        else:
            return {
                "id": 1,
                "name": "Sample Data",
                "description": "This is sample data created by AI Assistant",
                "created_at": datetime.now().isoformat(),
                "active": True
            }
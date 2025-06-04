"""
Text file creator for the AI Assistant
"""

import os
from IPython.display import HTML, display

class TextCreator:
    def __init__(self, workspace_dir):
        self.workspace_dir = workspace_dir
    
    def create_text_file(self):
        """Create an interactive text editor interface"""
        text_content = input("📝 Enter the text content (or press Enter for empty file): ")
        filename = input("📄 Enter filename (default: note.txt): ") or "note.txt"
        
        if not filename.endswith('.txt'):
            filename += '.txt'
        
        filepath = os.path.join(self.workspace_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(text_content)
        
        print(f"✅ Text file created: {filepath}")
        
        # Show content in a nice format
        display(HTML(f"""
        <div style="border: 1px solid #ccc; padding: 10px; background: #f9f9f9;">
            <h3>📄 {filename}</h3>
            <pre style="white-space: pre-wrap;">{text_content}</pre>
        </div>
        """))
        
        return f"Text file '{filename}' created successfully!"
"""
Website creator for the AI Assistant
"""

import os
from datetime import datetime
from IPython.display import HTML, display

class WebsiteCreator:
    def __init__(self, workspace_dir):
        self.workspace_dir = workspace_dir
    
    def create_website(self):
        """Create a simple website builder"""
        title = input("🌐 Enter website title: ") or "My Website"
        content = input("📝 Enter website content: ") or "Welcome to my website!"
        
        html_template = self._generate_html_template(title, content)
        
        filename = "website.html"
        filepath = os.path.join(self.workspace_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(html_template)
        
        print(f"✅ Website created: {filepath}")
        
        # Display the website
        display(HTML(html_template))
        
        return f"Website '{filename}' created and displayed!"
    
    def _generate_html_template(self, title, content):
        """Generate HTML template with styling"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }}
                .container {{
                    background: rgba(255,255,255,0.1);
                    padding: 30px;
                    border-radius: 10px;
                    backdrop-filter: blur(10px);
                }}
                h1 {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{title}</h1>
                <p>{content}</p>
                <p><small>Created with AI Assistant on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small></p>
            </div>
        </body>
        </html>
        """
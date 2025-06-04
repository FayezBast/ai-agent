"""
Display utilities for the AI Assistant
"""

from IPython.display import HTML, display

def show_help():
    """Show available commands"""
    help_text = """
🤖 AI Assistant Commands (Colab Version):

📝 Text Commands:
   - "notepad" / "text file" → Create a text file
   - "website" / "html" → Build a simple website
   - "code" / "python" → Create a Python script
   - "json" / "data" → Create a JSON data file

📁 File Management:
   - "list files" → Show workspace files
   - "help" → Show this help message

🧠 AI Features:
   - Any other input → Generate AI response using loaded models

💡 Note: This version works in Google Colab by creating files 
   instead of opening desktop applications.
    """
    
    display(HTML(f"<pre>{help_text}</pre>"))
    return "Help displayed!"

def show_startup_message():
    """Display startup message"""
    startup_message = """
🎉 Colab AI Assistant Ready!
============================

This modular AI Assistant helps you create files and content
in your Google Colab environment.

Features:
✨ Create text files, websites, Python scripts, and JSON data
📁 Manage workspace files
🤖 AI-powered responses using your loaded models

Type commands or ask questions to get started!
    """
    
    display(HTML(f"<pre>{startup_message}</pre>"))

def format_success_message(message, details=None):
    """Format a success message with optional details"""
    html = f"""
    <div style="background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 10px; border-radius: 5px; margin: 10px 0;">
        <strong>✅ {message}</strong>
        {f"<br><small>{details}</small>" if details else ""}
    </div>
    """
    display(HTML(html))

def format_error_message(message, details=None):
    """Format an error message with optional details"""
    html = f"""
    <div style="background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 10px; border-radius: 5px; margin: 10px 0;">
        <strong>❌ {message}</strong>
        {f"<br><small>{details}</small>" if details else ""}
    </div>
    """
    display(HTML(html))
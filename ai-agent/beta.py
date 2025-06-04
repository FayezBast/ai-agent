import subprocess
import os
import re
import webbrowser
import ollama
import sys

class CommandProcessor:
    def __init__(self, model_name="phi"):
        self.model = model_name
        self.command_patterns = [
            # Format: (regex pattern, handler function)
            (r"(?:paint|draw) (?:a |an )?(?P<shape>\w+)", self.draw_shape),
            (r"(?:make|create) (?:a |an )?(?:website|webpage)(?: about | on )?(?P<topic>.*)?", self.create_website),
            (r"(?:open|launch|start) (?P<program>\w+)", self.open_program),
            # Add more command patterns as needed
        ]
    
    def process_command(self, text):
        """Process text to identify and execute commands"""
        for pattern, handler in self.command_patterns:
            match = re.search(pattern, text.lower())
            if match:
                return handler(match)
        
        return None  # No command recognized

    def draw_shape(self, match):
        """Open paint application and notify about drawing the shape"""
        shape = match.group("shape")
        
        # Open paint based on OS
        if os.name == 'nt':  # Windows
            subprocess.Popen('mspaint')
        elif os.name == 'posix':  # macOS/Linux
            if sys.platform == 'darwin':  # macOS
                subprocess.Popen(['open', '-a', 'Preview'])
            else:  # Linux
                try:
                    subprocess.Popen(['gimp'])
                except:
                    return f"Couldn't find a paint program to open."
        
        return f"I've opened a paint program for you to draw a {shape}."

    def create_website(self, match):
        """Create a website using AI-generated code and open in VS Code"""
        topic = match.group("topic").strip() if match.group("topic") else "general purpose"
        
        # Generate website files using the AI model
        html_prompt = f"Create a complete HTML file for a website about {topic}. Include proper HTML5 structure with header, navigation, main content, and footer."
        css_prompt = f"Create CSS styles for a website about {topic}. Include styling for header, navigation, main content, footer, and responsive design."
        js_prompt = f"Create JavaScript code for a website about {topic} with basic interactivity."
        
        # Generate code using the AI model
        html_code = self.generate_code(html_prompt)
        css_code = self.generate_code(css_prompt)
        js_code = self.generate_code(js_prompt)
        
        # Create project directory
        project_dir = f"{topic.replace(' ', '_')}_website"
        os.makedirs(project_dir, exist_ok=True)
        
        # Write files
        with open(f"{project_dir}/index.html", "w") as f:
            f.write(html_code)
        
        with open(f"{project_dir}/styles.css", "w") as f:
            f.write(css_code)
        
        with open(f"{project_dir}/script.js", "w") as f:
            f.write(js_code)
        
        # Open VS Code with the project
        try:
            subprocess.Popen(['code', project_dir])
            return f"Created AI-generated website about '{topic}' and opened it in VS Code."
        except:
            return f"Created AI-generated website about '{topic}' in the '{project_dir}' directory. You can open it manually in your preferred editor."

    def open_program(self, match):
        """Open specified program"""
        program = match.group("program")
        try:
            subprocess.Popen([program])
            return f"Opened {program}."
        except:
            return f"Couldn't open {program}. Make sure it's installed and in your PATH."

    def generate_code(self, prompt):
        """Generate code using the Ollama Phi model"""
        try:
            response = ollama.generate(model=self.model, prompt=prompt)
            # Extract code from response - may need adjustment based on Phi's output format
            code = response['response']
            # Clean up code (remove markdown code blocks if present)
            code = re.sub(r'```(?:html|css|javascript|js)?(.*?)```', r'\1', code, flags=re.DOTALL)
            return code.strip()
        except Exception as e:
            print(f"Error generating code: {e}")
            return f"// Error generating code: {e}"


class ChatBot:
    def __init__(self, model_name="phi"):
        self.model = model_name
        self.command_processor = CommandProcessor(model_name)
    
    def process_input(self, user_input):
        # First check if it's a command
        command_result = self.command_processor.process_command(user_input)
        if command_result:
            return command_result
        
        # If not a command, pass to the LLM for a response
        try:
            response = ollama.generate(model=self.model, prompt=user_input)
            return response['response']
        except Exception as e:
            return f"Error: {e}"
"""
Code file creator for the AI Assistant
"""

import os
from datetime import datetime

class CodeCreator:
    def __init__(self, workspace_dir):
        self.workspace_dir = workspace_dir
    
    def create_code_file(self):
        """Create a Python code file"""
        code_purpose = input("💻 What should this code do? ") or "print('Hello World')"
        filename = input("📄 Enter filename (default: script.py): ") or "script.py"
        
        if not filename.endswith('.py'):
            filename += '.py'
        
        code_template = self._generate_code_template(code_purpose)
        
        filepath = os.path.join(self.workspace_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(code_template)
        
        print(f"✅ Python file created: {filepath}")
        print("📋 Code preview:")
        print("-" * 50)
        print(code_template)
        print("-" * 50)
        
        # Ask if user wants to run it
        run_code = input("🚀 Run the code now? (y/n): ").lower()
        if run_code == 'y':
            self._execute_code(filepath)
        
        return f"Python file '{filename}' created successfully!"
    
    def _generate_code_template(self, purpose):
        """Generate basic code structure"""
        return f'''"""
{purpose}
Created by AI Assistant on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

def main():
    """Main function"""
    # TODO: Implement {purpose}
    print("Code file created successfully!")
    print("Purpose: {purpose}")

if __name__ == "__main__":
    main()
'''
    
    def _execute_code(self, filepath):
        """Execute the created code file"""
        try:
            exec(open(filepath).read())
        except Exception as e:
            print(f"❌ Error executing code: {e}")
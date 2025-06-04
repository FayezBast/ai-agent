"""
File management utilities for the AI Assistant
"""

import os
from datetime import datetime

class FileManager:
    def __init__(self, workspace_dir):
        self.workspace_dir = workspace_dir
    
    def list_files(self):
        """List all files in the workspace"""
        files = os.listdir(self.workspace_dir)
        
        if not files:
            return "📭 Workspace is empty. Create some files first!"
        
        print("📁 Workspace Files:")
        print("=" * 40)
        
        for file in files:
            filepath = os.path.join(self.workspace_dir, file)
            size = os.path.getsize(filepath)
            modified = datetime.fromtimestamp(os.path.getmtime(filepath))
            
            print(f"📄 {file}")
            print(f"   Size: {size} bytes")
            print(f"   Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
            print()
        
        return f"Found {len(files)} files in workspace"
    
    def delete_file(self, filename):
        """Delete a file from workspace"""
        filepath = os.path.join(self.workspace_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return f"✅ File '{filename}' deleted successfully!"
        else:
            return f"❌ File '{filename}' not found!"
    
    def get_file_info(self, filename):
        """Get detailed information about a file"""
        filepath = os.path.join(self.workspace_dir, filename)
        if not os.path.exists(filepath):
            return f"❌ File '{filename}' not found!"
        
        stat = os.stat(filepath)
        return {
            "name": filename,
            "path": filepath,
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_ctime),
            "modified": datetime.fromtimestamp(stat.st_mtime),
            "is_file": os.path.isfile(filepath)
        }
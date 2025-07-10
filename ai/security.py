# security.py
import re
from pathlib import Path
from typing import Union
from config import Config

class SecurityValidator:
    """Security validation utilities"""
    
    @staticmethod
    def validate_filename(filename: str) -> str:
        """Validate filename for security and format."""
        if not filename or len(filename.strip()) == 0:
            raise ValueError("Filename cannot be empty.")
        filename = filename.strip()
        
        # Check for invalid characters
        invalid_chars = '<>:"/\\|?*'
        if any(char in filename for char in invalid_chars):
            raise ValueError(f"Filename contains invalid characters: {invalid_chars}")
        
        # Check for reserved names (Windows)
        reserved = ['CON', 'PRN', 'AUX', 'NUL'] + [f'COM{i}' for i in range(1, 10)] + [f'LPT{i}' for i in range(1, 10)]
        if filename.upper() in reserved:
            raise ValueError(f"'{filename}' is a reserved filename.")
            
        if len(filename) > 255:
            raise ValueError("Filename too long (max 255 characters).")
            
        return filename

    @staticmethod
    def validate_path(path: Union[str, Path]) -> Path:
        """Ensure path is within the allowed workspace directory."""
        resolved_path = Path(path).resolve()
        workspace = Config.WORKSPACE_DIR.resolve()
        
        if workspace not in resolved_path.parents and resolved_path != workspace:
            raise ValueError("Path is outside the allowed JARVIS_Workspace.")
            
        return resolved_path

    @staticmethod
    def sanitize_content(content: str) -> str:
        """Sanitize content for safe processing."""
        if not isinstance(content, str):
            content = str(content)
        
        # Basic sanitization: remove script tags and other potentially harmful patterns
        dangerous_patterns = [r'<script.*?</script>', r'javascript:', r'vbscript:', r'onload=', r'onerror=']
        for pattern in dangerous_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
            
        return content.strip()
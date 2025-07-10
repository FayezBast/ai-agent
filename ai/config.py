# config.py
from pathlib import Path

class Config:
    """Configuration settings for JARVIS AI"""
    # Directories and Files
    WORKSPACE_DIR = Path.home() / "JARVIS_Workspace"
    LOG_FILE = "jarvis.log"
    HISTORY_FILE = "command_history.json"
    
    # AI and Search Settings
    MAX_SEARCH_RESULTS = 10
    MAX_HISTORY_ENTRIES = 100
    
    # Supported file formats for creation
    SUPPORTED_FORMATS = ['docx', 'xlsx', 'pdf', 'txt', 'py', 'json', 'csv']
    
    # Application aliases for the system controller
    APP_ALIASES = {
        "visual studio code": "code",
        "vscode": "code",
        "vs code": "code",
        "word": "winword",
        "excel": "excel",
        "notepad": "notepad",
        "calculator": "calc",
        "chrome": "chrome",
        "firefox": "firefox",
        "browser": "chrome" # Default browser
    }
    
    # Intents for the command analyzer
    VALID_INTENTS = [
        "file_creation",
        "file_management", 
        "system_control",
        "web_browse",
        "conversation",
        "help"
    ]

    # ElevenLabs Voice Settings
    # Find your Voice ID on the ElevenLabs website -> Voices -> My Voices
    ELEVENLABS_VOICE_ID = 'JBFqnCBsd6RMkjVDRZzb' # e.g., '21m00Tcm4TlvDq8ikWAM'
# system_controller.py
import os
import subprocess
import platform
import psutil

from config import Config
from logger import log_info, log_error

class SystemController:
    """Handles system-level operations like opening applications."""

    def __init__(self):
        self.system = platform.system().lower()
        log_info(f"System controller initialized for OS: {self.system}")

    def open_application(self, app_name: str) -> str:
        """Opens an application using its name or alias."""
        app_name_lower = app_name.lower()
        command = Config.APP_ALIASES.get(app_name_lower, app_name_lower)
        
        try:
            log_info(f"Attempting to open '{app_name}' with command '{command}'")
            if self.system == "windows":
                os.startfile(command)
            elif self.system == "darwin": # macOS
                subprocess.run(["open", "-a", command], check=True)
            else: # Linux
                subprocess.Popen([command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            return f"Successfully launched {app_name}."
        except FileNotFoundError:
            log_error(f"Application '{command}' not found.")
            return f"Error: Could not find the application '{app_name}'. Is it installed and in your system's PATH?"
        except Exception as e:
            log_error(f"Failed to open {app_name}: {e}")
            return f"Could not open {app_name}. An error occurred: {e}"
        
        
    def get_system_status(self, status_type: str) -> str:
        """
        Gets a specific system status metric.
        """
        if "cpu" in status_type:
            cpu_percent = psutil.cpu_percent(interval=1)
            return f"Current CPU usage is at {cpu_percent}%."
        elif "memory" in status_type or "ram" in status_type:
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_gb = round(memory.used / (1024**3), 2)
            return f"Current RAM usage is at {memory_percent}%, which is {memory_gb} gigabytes."
        return "I'm not sure which system status you mean. Try 'CPU' or 'RAM'."
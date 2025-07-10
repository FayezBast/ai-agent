# logger.py
import logging
from pathlib import Path
from config import Config

class JarvisLogger:
    """Enhanced logging for JARVIS"""
    _logger = None

    @staticmethod
    def get_logger():
        if JarvisLogger._logger is None:
            JarvisLogger.setup_logging()
            JarvisLogger._logger = logging.getLogger('JARVIS')
        return JarvisLogger._logger

    @staticmethod
    def setup_logging():
        """Setup logging configuration"""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        log_path = Config.WORKSPACE_DIR / Config.LOG_FILE
        log_path.parent.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler()
            ]
        )

# Convenience functions
def log_info(message):
    JarvisLogger.get_logger().info(message)

def log_error(message):
    JarvisLogger.get_logger().error(message)

def log_warning(message):
    JarvisLogger.get_logger().warning(message)
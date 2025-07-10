# web_controller.py
import webbrowser
from logger import log_info, log_error

class WebController:
    """Handles web operations like searching."""

    def search_web(self, query: str) -> str:
        """Opens the default web browser to perform a Google search."""
        if not query:
            return "Please provide a search query."
        
        try:
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            log_info(f"Opened web browser for query: {query}")
            return f"Searching the web for: '{query}'"
        except Exception as e:
            log_error(f"Web search failed: {e}")
            return "An error occurred while trying to open your web browser."
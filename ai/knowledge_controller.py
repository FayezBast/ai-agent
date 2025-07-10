# knowledge_controller.py
import wikipedia
from logger import log_info, log_error

class KnowledgeController:
    def get_wikipedia_summary(self, topic: str) -> str:
        """
        Fetches a summary of a topic from Wikipedia.
        """
        log_info(f"Fetching Wikipedia summary for: {topic}")
        try:
            # Get a summary of the first 2 sentences
            summary = wikipedia.summary(topic, sentences=2)
            return summary
        except wikipedia.exceptions.DisambiguationError as e:
            # Handle cases where the topic is ambiguous
            options = "\n - ".join(e.options[:5])
            return f"That topic could mean several things, like:\n - {options}\nPlease be more specific."
        except wikipedia.exceptions.PageError:
            return f"Sorry, I couldn't find a Wikipedia page for '{topic}'."
        except Exception as e:
            log_error(f"Wikipedia error: {e}")
            return "Sorry, I had trouble connecting to Wikipedia."
import sys
import os
from PyQt6.QtWidgets import QApplication
from gui import ChatWindow
import model

def main():
    """Main entry point for the application."""
    # Parse command line arguments
    model_path = r"C:\Users\HCES\Documents\speech\trained-voice-llm"  # Default model path
    if len(sys.argv) > 1:
        model_path = sys.argv[1]
    
    # Check if model path exists
    if not os.path.exists(model_path):
        print(f"Error: Model path '{model_path}' does not exist.")
        print("Usage: python main.py [path_to_model]")
        sys.exit(1)
    
    # Initialize application
    app = QApplication(sys.argv)
    
    try:
        # Load the model
        if not model.load_model(model_path):
            print("Failed to load the model. Exiting.")
            sys.exit(1)
        
        # Initialize GUI
        chat_window = ChatWindow()
        chat_window.show()
        
        # Set up application cleanup
        app.aboutToQuit.connect(model.unload_model)
        
        # Start the application
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error initializing application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
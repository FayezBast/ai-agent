#!/usr/bin/env python3
"""
Main entry point for the Colab AI Assistant
"""

from ai_assistant import ColabAIAssistant
from utils.display import show_startup_message

def start_ai_assistant():
    """Start the AI assistant interface"""
    if 'model_manager' not in globals():
        print("❌ Model manager not found. Please run the model manager code first.")
        return
    
    assistant = ColabAIAssistant(model_manager)
    
    print("🤖 AI Assistant Started!")
    print("Type 'help' for available commands or start giving instructions!")
    
    while True:
        try:
            user_input = input("\n🗣️ You: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("👋 Goodbye!")
                break
            
            if user_input:
                response = assistant.process_command(user_input)
                print(f"\n🤖 Assistant: {response}")
        
        except KeyboardInterrupt:
            print("\n👋 Assistant stopped by user")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    show_startup_message()
    print("📝 Run start_ai_assistant() to begin!")
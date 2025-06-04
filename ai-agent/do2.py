import os


text_file_path = 'output.text'


try:
    with open(text_file_path, 'r') as file:
        content = file.read().lower()
    
    
    if "open google chrome" in content:
        os.startfile("notepad.exe")
        print("Opening Calculator")
    elif "open google chrome" in content:
        os.startfile("C:/Users/HCES/Desktop/Google Chrome.lnk")
        print("Opening Google Chrome")
    elif "open notepad" in content:
        os.startfile("")
        print("Opening Notepad")
    
    else:
        print("No matching application command found")

except FileNotFoundError:
    print(f"Could not find file: {text_file_path}")
except Exception as e:
    print(f"Error: {e}")
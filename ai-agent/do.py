import os
import subprocess

def open_application(app_path):
    """Opens the specified application."""
    try:
        if os.name == 'nt':  
            os.startfile(app_path)
        elif os.name == 'posix':  
            subprocess.call(['open', app_path])
        print(f"Successfully opened: {app_path}")
    except Exception as e:
        print(f"Error opening application: {e}")


text_file_path = 'output.text'


text_to_app = {
    "open Google Chrome": "C:/Users/HCES/Desktop/Google Chrome.lnk",
    " open notepad": "notepad.exe"
   
}


try:
    with open(text_file_path, 'r') as file:
        file_content = file.read().lower()  


    app_found = False
    for trigger_text, app_path in text_to_app.items():
        if trigger_text.lower() in file_content:
            print(f"Found trigger: '{trigger_text}'")
            open_application(app_path)
            app_found = True
    
    if not app_found:
        print("No matching triggers found in the text file.")

except FileNotFoundError:
    print(f"Error: The file {text_file_path} was not found.")
except Exception as e:
    print(f"An error occurred: {e}")
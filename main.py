import subprocess
import json
import sys
import os

# The PowerShell script is expected to be in the same directory
POWERSHELL_SCRIPT = "apppath.ps1"

def find_app_path(app_name):
    """
    Runs the PowerShell script to find the full path of an application.
    """
    print(f"🤖 Searching for '{app_name}'...")

    if not os.path.exists(POWERSHELL_SCRIPT):
        print(f"⚠️ Error: The script '{POWERSHELL_SCRIPT}' was not found.")
        return None

    try:
        # Command to execute the PowerShell script with the app name as an argument
        ps_command = [
            "powershell.exe",
            "-ExecutionPolicy", "Bypass",
            "-File", POWERSHELL_SCRIPT,
            "-AppName", app_name
        ]

        # We use Popen and communicate to avoid potential deadlocks with stdout/stderr
        process = subprocess.Popen(ps_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()

        # Handle PowerShell errors
        if process.returncode != 0 or "NOT_FOUND" in stdout:
            print(f"😞 Sorry, I couldn't find an application matching '{app_name}'.")
            if stderr:
                print(f"   Error details: {stderr.strip()}")
            return None

        # The PowerShell script should return the path directly
        app_path = stdout.strip()
        if os.path.exists(app_path):
            print(f"✅ Found it! Path is: {app_path}")
            return app_path
        else:
            print(f"🤔 The script returned a path, but it doesn't seem valid: {app_path}")
            return None

    except FileNotFoundError:
        print("❌ Error: 'powershell.exe' is not installed or not in your system's PATH.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def open_application(app_path):
    """
    Opens the application at the given path.
    The .exe is already part of the path returned by the PowerShell script.
    """
    if not app_path:
        return

    print(f"🚀 Opening '{os.path.basename(app_path)}'...")
    try:
        # Use subprocess.Popen for non-blocking execution
        subprocess.Popen([app_path])
        print("✨ Application launched successfully!")
    except Exception as e:
        print(f"❌ Failed to open the application. Error: {e}")

if __name__ == "__main__":
    # Get the application name from the command line arguments
    if len(sys.argv) > 1:
        app_to_find = sys.argv[1]
        path = find_app_path(app_to_find)
        if path:
            open_application(path)
    else:
        print("Please provide an application name to search for.")
        print("Example: python ai4.py chrome")
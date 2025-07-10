import subprocess
import json

CACHE_FILE = "apps_cache.json"

def update_apps_cache():
    try:
        print("⚡ Updating apps list via apppath.ps1...")
        ps_command = [
            "powershell.exe",
            "-ExecutionPolicy", "Bypass",
            "-File", "apppath.ps1"
        ]
        result = subprocess.run(ps_command, capture_output=True, text=True, check=True)
        output = result.stdout.strip()

        if output and output.startswith("["):
            apps = json.loads(output)
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(apps, f, ensure_ascii=False, indent=2)
            print(f"✅ Apps list updated and saved to {CACHE_FILE}.")
            return True
        else:
            print("⚠️ apppath.ps1 did not return valid JSON.")
            return False
    except subprocess.CalledProcessError as e:
        print(f"⚠️ apppath.ps1 failed: {e}")
        return False
    except Exception as e:
        print(f"⚠️ Error running apppath.ps1: {e}")
        return False

if __name__ == "__main__":
    update_apps_cache()

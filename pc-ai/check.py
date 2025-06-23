#!/usr/bin/env python3
"""
JARVIS AI Assistant Setup Script
Automatically installs dependencies and configures the system
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def install_package(package):
    """Install a Python package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_system_dependencies():
    """Check and install system-level dependencies"""
    system = platform.system().lower()
    
    print(f"🔍 Detected system: {platform.system()}")
    
    if system == "linux":
        print("🐧 Linux detected - checking audio dependencies...")
        try:
            # Check if espeak is installed
            subprocess.run(["espeak", "--version"], capture_output=True, check=True)
            print("✅ espeak found")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ espeak not found")
            print("📦 Please run: sudo apt-get install espeak espeak-data libespeak1 libespeak-dev")
            print("📦 Also run: sudo apt-get install portaudio19-dev python3-pyaudio")
            return False
    
    elif system == "darwin":  # macOS
        print("🍎 macOS detected - checking brew dependencies...")
        try:
            subprocess.run(["brew", "--version"], capture_output=True, check=True)
            print("✅ Homebrew found")
            # Install portaudio if needed
            subprocess.run(["brew", "install", "portaudio"], capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Homebrew not found - please install from https://brew.sh")
            print("📦 Then run: brew install portaudio")
            return False
    
    return True

def setup_environment():
    """Setup environment variables and configuration"""
    print("🔧 Setting up environment...")
    
    # Create JARVIS workspace
    workspace = Path.home() / "JARVIS_Workspace"
    workspace.mkdir(exist_ok=True)
    print(f"📁 Workspace created: {workspace}")
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("🔑 OpenAI API key not found in environment variables")
        print("💡 To enable advanced AI features:")
        print("   1. Get API key from https://platform.openai.com/api-keys")
        print("   2. Set environment variable: export OPENAI_API_KEY='your-key-here'")
        print("   3. Or add to ~/.bashrc or ~/.zshrc for permanent setup")
    else:
        print("✅ OpenAI API key found")
    
    return True

def install_python_dependencies():
    """Install required Python packages"""
    packages = [
        "openai>=1.0.0",
        "transformers>=4.21.0", 
        "torch>=1.12.0",
        "speechrecognition>=3.10.0",
        "pyttsx3>=2.90",
        "requests>=2.28.0",
        "psutil>=5.9.0"
    ]
    
    print("📦 Installing Python dependencies...")
    failed_packages = []
    
    for package in packages:
        print(f"📥 Installing {package}...")
        if not install_package(package):
            failed_packages.append(package)
            print(f"❌ Failed to install {package}")
        else:
            print(f"✅ {package} installed")
    
    # Try to install PyAudio (often problematic)
    print("🎤 Installing audio dependencies...")
    if not install_package("pyaudio"):
        print("❌ PyAudio installation failed")
        print("💡 Try manual installation:")
        if platform.system().lower() == "windows":
            print("   pip install pipwin && pipwin install pyaudio")
        elif platform.system().lower() == "linux":
            print("   sudo apt-get install python3-pyaudio")
        else:
            print("   brew install portaudio && pip install pyaudio")
        failed_packages.append("pyaudio")
    
    return len(failed_packages) == 0

def create_launcher_script():
    """Create a convenient launcher script"""
    launcher_content = '''#!/usr/bin/env python3
"""
JARVIS AI Assistant Launcher
"""

import sys
from pathlib import Path

# Add the JARVIS directory to Python path
jarvis_dir = Path(__file__).parent
sys.path.insert(0, str(jarvis_dir))

try:
    from jarvis_ai_assistant import main
    main()
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("📦 Please run setup.py first to install dependencies")
except Exception as e:
    print(f"❌ Error starting JARVIS: {e}")
'''
    
    launcher_path = Path("launch_jarvis.py")
    with open(launcher_path, 'w') as f:
        f.write(launcher_content)
    
    # Make executable on Unix systems
    if platform.system().lower() != "windows":
        os.chmod(launcher_path, 0o755)
    
    print(f"🚀 Launcher created: {launcher_path}")
    return launcher_path

def run_tests():
    """Run basic functionality tests"""
    print("🧪 Running system tests...")
    
    try:
        # Test text-to-speech
        import pyttsx3
        engine = pyttsx3.init()
        print("✅ Text-to-speech working")
    except Exception as e:
        print(f"❌ Text-to-speech error: {e}")
    
    try:
        # Test speech recognition
        import speech_recognition as sr
        r = sr.Recognizer()
        print("✅ Speech recognition loaded")
    except Exception as e:
        print(f"❌ Speech recognition error: {e}")
    
    try:
        # Test transformers
        from transformers import pipeline
        print("✅ Transformers library working")
    except Exception as e:
        print(f"❌ Transformers error: {e}")
    
    print("🧪 Basic tests completed")

def main():
    """Main setup function"""
    print("🤖 JARVIS AI Assistant Setup")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher required")
        print(f"📋 Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Step 1: Check system dependencies
    if not check_system_dependencies():
        print("❌ System dependencies check failed")
        print("📋 Please install required system packages and run setup again")
        return False
    
    # Step 2: Install Python packages
    if not install_python_dependencies():
        print("⚠️ Some Python packages failed to install")
        print("📋 JARVIS may have limited functionality")
    
    # Step 3: Setup environment
    setup_environment()
    
    # Step 4: Create launcher
    launcher = create_launcher_script()
    
    # Step 5: Run tests
    run_tests()
    
    print("\n" + "=" * 40)
    print("🎉 JARVIS AI Assistant Setup Complete!")
    print("\n📋 Quick Start:")
    print(f"   python {launcher}")
    print("   or")
    print("   python jarvis_ai_assistant.py")
    
    print("\n💡 Tips:")
    print("   - Say 'Hey JARVIS' to activate voice mode")
    print("   - Type commands for text mode")
    print("   - Set OPENAI_API_KEY for enhanced AI features")
    print("   - Check workspace folder for created files")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🚀 Setup successful! You can now run JARVIS.")
        else:
            print("\n❌ Setup encountered issues. Check messages above.")
    except KeyboardInterrupt:
        print("\n👋 Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Setup error: {e}")
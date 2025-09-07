#!/usr/bin/env python3
"""
Script to fix Streamlit installation issues
"""
import subprocess
import sys

def run_command(cmd, description):
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} successful")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def fix_streamlit():
    print("🔧 Fixing Streamlit Installation Issues")
    print("=" * 40)
    
    # Method 1: Try installing cmake first
    print("\n📦 Method 1: Installing cmake...")
    if run_command("brew install cmake", "Installing cmake with Homebrew"):
        if run_command("pip install streamlit", "Installing Streamlit after cmake"):
            print("✅ Streamlit installed successfully!")
            return True
    
    # Method 2: Try conda
    print("\n📦 Method 2: Trying conda...")
    if run_command("conda install -c conda-forge streamlit -y", "Installing Streamlit with conda"):
        print("✅ Streamlit installed successfully with conda!")
        return True
    
    # Method 3: Try pre-built wheels
    print("\n📦 Method 3: Using pre-built wheels...")
    if run_command("pip install --only-binary=all streamlit==1.25.0", "Installing pre-built Streamlit"):
        print("✅ Streamlit installed successfully with pre-built wheels!")
        return True
    
    # Method 4: Try without pyarrow
    print("\n📦 Method 4: Installing without pyarrow...")
    commands = [
        "pip install streamlit==1.25.0 --no-deps",
        "pip install altair blinker cachetools click importlib-metadata numpy packaging pandas pillow protobuf rich tenacity toml typing-extensions tzlocal validators gitpython pydeck tornado watchdog"
    ]
    
    success = True
    for cmd in commands:
        if not run_command(cmd, f"Running: {cmd}"):
            success = False
            break
    
    if success:
        print("✅ Streamlit installed successfully without pyarrow!")
        return True
    
    print("❌ All methods failed. Try Docker deployment instead.")
    return False

if __name__ == "__main__":
    if fix_streamlit():
        print("\n🎉 Streamlit installation fixed!")
        print("Now you can run: python deploy.py")
    else:
        print("\n💡 Alternative: Use Docker deployment (no build issues)")
        print("Run: python deploy.py -> Choose option 1")

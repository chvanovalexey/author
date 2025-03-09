#!/usr/bin/env python
"""
Script to reinstall the project dependencies.
This will uninstall any conflicting packages and reinstall from requirements.txt.
"""
import subprocess
import sys

def main():
    print("Uninstalling potentially conflicting packages...")
    subprocess.call([sys.executable, "-m", "pip", "uninstall", "-y", "openai"])
    
    print("Installing dependencies from requirements.txt...")
    subprocess.call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    print("Installation complete.")
    print("Please restart the application with: python run.py")

if __name__ == "__main__":
    main() 
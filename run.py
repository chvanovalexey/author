#!/usr/bin/env python
"""
Script to run the Audio Story Script Generator application.
"""
import os
import subprocess
import sys
import toml

def check_requirements():
    """Check if required packages are installed."""
    try:
        import streamlit
        import openai
        import tiktoken
        import pandas
        return True
    except ImportError as e:
        print(f"Missing required package: {e}")
        return False

def install_requirements():
    """Install required packages from requirements.txt."""
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def check_streamlit_secrets():
    """Check if .streamlit/secrets.toml file exists and contains API key."""
    # Create .streamlit directory if it doesn't exist
    os.makedirs(".streamlit", exist_ok=True)
    
    secrets_file = ".streamlit/secrets.toml"
    
    if not os.path.exists(secrets_file):
        print("Streamlit secrets file not found.")
        api_key = input("Please enter your OpenAI API key: ")
        
        # Create secrets.toml with the API key
        secrets = {
            "openai": {
                "api_key": api_key
            }
        }
        
        with open(secrets_file, "w", encoding="utf-8") as f:
            toml.dump(secrets, f)
            
        print("Secrets file created at: .streamlit/secrets.toml")
    else:
        # Check if API key is in the secrets file
        try:
            with open(secrets_file, "r", encoding="utf-8") as f:
                secrets = toml.load(f)
            
            if "openai" not in secrets or "api_key" not in secrets["openai"]:
                api_key = input("OpenAI API key not found in secrets file. Please enter your key: ")
                
                if "openai" not in secrets:
                    secrets["openai"] = {}
                
                secrets["openai"]["api_key"] = api_key
                
                with open(secrets_file, "w", encoding="utf-8") as f:
                    toml.dump(secrets, f)
                
                print("API key added to secrets file.")
        except Exception as e:
            print(f"Error reading secrets file: {str(e)}")
            api_key = input("Please enter your OpenAI API key: ")
            
            secrets = {
                "openai": {
                    "api_key": api_key
                }
            }
            
            with open(secrets_file, "w", encoding="utf-8") as f:
                toml.dump(secrets, f)

def run_app():
    """Run the Streamlit app."""
    print("Starting Audio Story Script Generator...")
    subprocess.run(["streamlit", "run", "app.py"])

if __name__ == "__main__":
    # Check if requirements are installed
    if not check_requirements():
        install_requirements()
    
    # Check if Streamlit secrets file exists and contains API key
    check_streamlit_secrets()
    
    # Run the app
    run_app() 
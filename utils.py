import os
import json
import tiktoken
import streamlit as st
import requests
import time
from config import (
    MODELS,
    DEFAULT_SYSTEM_PROMPT as SYSTEM_PROMPT,
    OUTPUT_ESTIMATION_FACTOR,
    MIN_OUTPUT_TOKENS,
    DEFAULT_TEMPERATURE
)

# Ensure data directory exists
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def count_tokens(text, model="gpt-4o"):
    """Count the number of tokens in a text string for a given model"""
    try:
        # Try to get the encoding for the specified model
        enc = tiktoken.encoding_for_model(model)
    except KeyError:
        # If the model is not directly supported, use the cl100k_base encoding
        # which is used by newer models like GPT-4 and GPT-4o family
        enc = tiktoken.get_encoding("cl100k_base")
    
    return len(enc.encode(text))

def estimate_cost(input_tokens, estimated_output_tokens, model="gpt-4o"):
    """Estimate the cost of a request based on input and output tokens"""
    input_cost = (input_tokens / 1000000) * MODELS[model]["input_cost"]
    output_cost = (estimated_output_tokens / 1000000) * MODELS[model]["output_cost"]
    return input_cost + output_cost

def estimate_output_tokens(brief_length):
    """Estimate the number of output tokens based on the brief length"""
    return max(brief_length * OUTPUT_ESTIMATION_FACTOR, MIN_OUTPUT_TOKENS)

def generate_script(messages, model="gpt-4o", temperature=DEFAULT_TEMPERATURE):
    """Generate a script using the OpenAI API directly via HTTP"""
    try:
        # Get API key from Streamlit secrets
        api_key = st.secrets["openai"]["api_key"]
        
        # Directly use the requests library to make the API call
        # This avoids any proxy issues that might be in the OpenAI client
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        
        # Make the API call
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        # Check for successful response
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            # Handle API errors
            error_info = response.json() if response.content else {"error": f"Status code: {response.status_code}"}
            st.error(f"API Error: {error_info}")
            raise Exception(f"OpenAI API error: {error_info}")
            
    except Exception as e:
        st.error(f"Error details: {str(e)}")
        import traceback
        st.error(f"Traceback: {traceback.format_exc()}")
        raise Exception(f"Error generating script: {str(e)}")

def load_scripts():
    """Load all scripts from the scripts.json file"""
    scripts_file = os.path.join(DATA_DIR, "scripts.json")
    if os.path.exists(scripts_file):
        with open(scripts_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"scripts": []}

def save_scripts(scripts_data):
    """Save all scripts to the scripts.json file"""
    scripts_file = os.path.join(DATA_DIR, "scripts.json")
    with open(scripts_file, "w", encoding="utf-8") as f:
        json.dump(scripts_data, f, ensure_ascii=False, indent=4)

def load_script_versions(script_id):
    """Load all versions of a specific script"""
    filename = os.path.join(DATA_DIR, f"versions_{script_id}.json")
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_script_versions(script_id, versions):
    """Save all versions of a specific script"""
    filename = os.path.join(DATA_DIR, f"versions_{script_id}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(versions, f, ensure_ascii=False, indent=4)

def create_message_from_context(system_prompt, brief, selected_versions, user_prompt):
    """Create a message list for the OpenAI API from context components"""
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add brief
    brief_text = f"Brief summary of the story: {brief}"
    messages.append({"role": "user", "content": brief_text})
    
    # Add selected previous versions with their actual version numbers
    for version in selected_versions:
        # Get version number from the version object
        version_number = version.get('version_number', 0)
        version_text = f"Previous version {version_number}:\nPrompt: {version.get('prompt', 'No prompt')}\nContent: {version.get('content', 'No content')}"
        messages.append({"role": "user", "content": version_text})
    
    # Add current prompt
    messages.append({"role": "user", "content": user_prompt})
    
    return messages

def get_context_parts(brief, selected_versions, user_prompt):
    """Get a list of context parts for display"""
    context_parts = []
    
    # Add brief
    brief_text = f"Brief summary of the story: {brief}"
    context_parts.append({"type": "Brief Summary", "content": brief_text})
    
    # Add selected previous versions with their actual version numbers
    for version in selected_versions:
        # Get version number from the version object
        version_number = version.get('version_number', 0)
        version_text = f"Previous version {version_number}:\nPrompt: {version.get('prompt', 'No prompt')}\nContent: {version.get('content', 'No content')}"
        context_parts.append({"type": f"Previous Version {version_number}", "content": version_text})
    
    # Add current prompt
    context_parts.append({"type": "Current Request", "content": user_prompt})
    
    return context_parts 
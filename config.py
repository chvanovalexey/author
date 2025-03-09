# App configuration settings

# App description
APP_TITLE = "Audio Story Script Generator"
APP_DESCRIPTION = "Create engaging scripts for audio stories with AI assistance"

# Default system prompt
DEFAULT_SYSTEM_PROMPT = """You are an expert scriptwriter for audio stories. 
Your task is to create detailed, engaging scripts based on brief summaries.
Focus on natural-sounding dialogue, clear narrative structure, and vivid descriptions.
The script should be ready for audio recording, with appropriate pacing and tone.
Include sound effect suggestions and music cues where appropriate.
Format the script for easy reading by voice actors, including character names, dialogue, and narrative directions.
"""

# OpenAI models configuration
MODELS = {
    "gpt-4o": {
        "quality": 100,
        "context_window": 128000,
        "input_cost": 5.0,  # per 1M tokens
        "output_cost": 15.0,  # per 1M tokens
    },
    "gpt-4o-2024-08-06": {
        "quality": 100,
        "context_window": 128000,
        "input_cost": 2.5,  # per 1M tokens
        "output_cost": 10.0,  # per 1M tokens
    },
    "gpt-4o-mini": {
        "quality": 85,
        "context_window": 128000,
        "input_cost": 0.15,  # per 1M tokens
        "output_cost": 0.6,  # per 1M tokens
    }
}

# Rate limits
RATE_LIMITS = {
    "gpt-4o": {
        "TPM": 30000,  # Tokens per minute
        "RPM": 500,    # Requests per minute
        "TPD": 90000,  # Tokens per day
    },
    "gpt-4o-mini": {
        "TPM": 200000,  # Tokens per minute
        "RPM": 500,     # Requests per minute
        "RPD": 10000,   # Requests per day
        "TPD": 2000000, # Tokens per day
    }
}

# Output estimation factor (how many tokens to expect in output compared to brief length)
OUTPUT_ESTIMATION_FACTOR = 5

# Default output token minimum
MIN_OUTPUT_TOKENS = 1000

# Default temperature for generation
DEFAULT_TEMPERATURE = 0.7 
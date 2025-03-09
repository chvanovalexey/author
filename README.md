# Audio Story Script Generator

A Streamlit application that helps writers create and refine audio story scripts using OpenAI's language models (LLM).

## Features

- Create and manage multiple script projects
- Generate detailed scripts from brief summaries
- Refine scripts by providing specific instructions to the AI
- Select previous script versions to use as context for improvements
- Token counting and cost estimation
- Download scripts in text format
- Track script versions and their prompts

## Requirements

- Python 3.8+
- Streamlit
- OpenAI API key

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS or Linux
   source venv/bin/activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up your OpenAI API key:
   - Create a `.streamlit` directory in the project root if it doesn't exist
   - Create a `secrets.toml` file inside the `.streamlit` directory
   - Add your OpenAI API key in the following format:
     ```toml
     [openai]
     api_key = "your-openai-api-key-here"
     ```
   
   Alternatively, you can use the run script which will prompt you for your API key.

## Quick Start

The easiest way to start the application is to use the run script:

```
python run.py
```

This script will:
1. Check if all required packages are installed
2. Install any missing requirements
3. Check if the `.streamlit/secrets.toml` file exists with an API key
4. Prompt for an API key if needed
5. Start the Streamlit application

Alternatively, you can start the application directly with Streamlit:

```
streamlit run app.py
```

## Usage

1. Access the app in your web browser (typically at http://localhost:8501)

2. Create a new script:
   - Click "Create New Script" in the sidebar
   - Enter a title and brief summary of your audio story

3. Generate a script:
   - Select an AI model (GPT-4o, GPT-4o-mini, etc.)
   - Enter a prompt describing what you want in the script
   - Click "Generate Script"

4. Refine your script:
   - View the generated script
   - Select previous versions to include as context (if applicable)
   - Enter a new prompt describing the changes you want
   - Generate a new version

5. Download your final script:
   - Go to the version you want to download
   - Click "Download this version"

## Data Storage

The application stores data locally:
- `data/scripts.json`: Contains metadata for all scripts
- `data/versions_<script_id>.json`: Contains all versions of a specific script

## Models Available

- **gpt-4o**: Highest quality, more expensive
  - Context Window: 128K tokens
  - Input Cost: $5 per 1M tokens
  - Output Cost: $15 per 1M tokens

- **gpt-4o-2024-08-06**: High quality, medium cost
  - Context Window: 128K tokens
  - Input Cost: $2.5 per 1M tokens
  - Output Cost: $10 per 1M tokens

- **gpt-4o-mini**: Good quality, most affordable
  - Context Window: 128K tokens
  - Input Cost: $0.15 per 1M tokens
  - Output Cost: $0.6 per 1M tokens

## Advanced Configuration

You can modify the following files to customize the application:

- `config.py`: Contains model definitions, system prompts, and other settings
- `utils.py`: Contains utility functions for token counting, cost estimation, etc.
- `app.py`: The main Streamlit application
- `.streamlit/secrets.toml`: Contains your OpenAI API key and other secrets

## Troubleshooting

If you encounter any issues:

1. Make sure your OpenAI API key is valid and correctly set in the `.streamlit/secrets.toml` file
2. Check that all required packages are installed
3. Ensure you have sufficient permissions to create and write files in the application directory

## License

[Your License Information] 
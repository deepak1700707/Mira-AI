"""
Configuration management with environment variable support.
Falls back to config.json for backwards compatibility.
"""
import os
import json
from pathlib import Path

# Try to load .env file if dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, skip loading .env
    pass

BASE_DIR = Path(__file__).parent.parent
CONFIG_PATH = BASE_DIR / "data" / "config.json"
MAX_MEMORY_ENTRIES = int(os.getenv("MAX_MEMORY_ENTRIES", "1000"))

def get_config():
    """Load configuration from .env or config.json."""
    config = {}
    
    # Try loading from .env first (preferred)
    config["openweather_api_key"] = os.getenv("OPENWEATHER_API_KEY", "")
    config["tavily_api_key"] = os.getenv("TAVILY_API_KEY", "")
    
    # Fallback to config.json for backwards compatibility
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                json_config = json.load(f)
                # Only use JSON values if .env doesn't have them
                if not config["openweather_api_key"]:
                    config["openweather_api_key"] = json_config.get("openweather_api_key", "")
                if not config["tavily_api_key"]:
                    config["tavily_api_key"] = json_config.get("tavily_api_key", "")
        except Exception as e:
            print(f"⚠️ Warning: Could not load config.json: {e}")
    
    return config

CONFIG = get_config()


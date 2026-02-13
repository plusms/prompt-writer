import json
import os
from typing import Dict, Any

CONFIG_FILE = "sites.json"

def load_sites_config() -> Dict[str, Any]:
    """Loads the WordPress sites configuration from sites.json."""
    # Try Streamlit Secrets first (for Cloud)
    # Try Streamlit Secrets first (for Cloud)
    try:
        import streamlit as st
        # Accessing st.secrets may raise FileNotFoundError or StreamlitSecretNotFoundError if no secrets.toml
        if hasattr(st, "secrets") and "sites_config" in st.secrets:
            return dict(st.secrets["sites_config"])
    except (ImportError, Exception):
        # Fallback to local file if streamlit is not installed or secrets are missing
        pass

    # Fallback to local file
    if not os.path.exists(CONFIG_FILE):
        return {}
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {CONFIG_FILE}: {e}")
        return {}

def get_gemini_api_key() -> str:
    """Retrieves the Gemini API key from environment variables."""
    return os.getenv("GEMINI_API_KEY", "")

def get_sheets_credentials_path() -> str:
    """Retrieves the path to the Google Sheets service account JSON."""
    return os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH", "service_account.json")

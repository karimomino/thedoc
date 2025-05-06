"""Configuration management for TheDoc."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any

DEFAULT_CONFIG = {
    "project_name": "",
    "output_dir": "docs",
    "docs_dir": "",
    "exclude_patterns": [
        "*.pyc",
        "__pycache__",
        ".git",
        "venv",
        "node_modules",
    ],
    "supported_languages": [
        "python",
        "javascript",
        "typescript",
        "java",
        "csharp",
        "go",
        "rust",
    ],
}

def get_config_path() -> Path:
    """Get the path to the configuration file."""
    return Path.cwd() / "thedoc.yaml"

def load_config() -> Dict[str, Any]:
    """Load configuration from file or return defaults."""
    config_path = get_config_path()
    if not config_path.exists():
        return DEFAULT_CONFIG.copy()
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        merged_config = DEFAULT_CONFIG.copy()
        merged_config.update(config)
        return merged_config
    except Exception as e:
        print(f"Error loading config: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    config_path = get_config_path()
    try:
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
    except Exception as e:
        print(f"Error saving config: {e}") 
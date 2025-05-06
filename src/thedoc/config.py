"""Configuration management for TheDoc."""

import os
from pathlib import Path
from typing import Dict, Any

DEFAULT_CONFIG = {
    "project_name": "",
    "output_dir": "docs",
    "mkdocs_dir": "mkdocs",
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
    
    # TODO: Implement YAML config loading
    return DEFAULT_CONFIG.copy()

def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    config_path = get_config_path()
    # TODO: Implement YAML config saving
    pass 
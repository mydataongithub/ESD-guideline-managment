"""
Configuration settings for the MCP server connection.
"""
from typing import Dict, Any, Optional
import os
import json
from pathlib import Path

# Default MCP configuration
DEFAULT_MCP_CONFIG = {
    "server_url": "http://localhost:3000",
    "api_key": "",  # Default empty, should be set in environment or config file
    "timeout_seconds": 60,
    "extract_rules": True,
    "extract_metadata": True,
    "extract_images": True,
    "use_advanced_models": True,
    "confidence_threshold": 0.7  # Minimum confidence score for rule extraction
}

def load_mcp_config() -> Dict[str, Any]:
    """
    Load MCP configuration from environment variables or config file.
    
    Priority:
    1. Environment variables
    2. mcp_config.json file in config directory
    3. Default values
    
    Returns:
        Dictionary with MCP configuration
    """
    config = DEFAULT_MCP_CONFIG.copy()
    
    # Check for config file
    config_path = Path("config/mcp_config.json")
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                file_config = json.load(f)
                config.update(file_config)
        except Exception as e:
            print(f"Error loading MCP config file: {str(e)}")
    
    # Override with environment variables if they exist
    if os.environ.get("MCP_SERVER_URL"):
        config["server_url"] = os.environ.get("MCP_SERVER_URL")
    
    if os.environ.get("MCP_API_KEY"):
        config["api_key"] = os.environ.get("MCP_API_KEY")
        
    if os.environ.get("MCP_TIMEOUT"):
        try:
            config["timeout_seconds"] = int(os.environ.get("MCP_TIMEOUT"))
        except ValueError:
            pass
    
    return config

def save_mcp_config(config: Dict[str, Any]) -> bool:
    """
    Save MCP configuration to config file.
    
    Args:
        config: Configuration dictionary to save
        
    Returns:
        True if successful, False otherwise
    """
    config_dir = Path("config")
    if not config_dir.exists():
        config_dir.mkdir(parents=True, exist_ok=True)
        
    config_path = config_dir / "mcp_config.json"
    
    try:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving MCP config file: {str(e)}")
        return False

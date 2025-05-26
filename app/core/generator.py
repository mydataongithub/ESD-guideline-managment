# app/core/generator.py
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any

# Path configurations
CONFIG_PATH = Path(__file__).parent.parent.parent / "config"
MASTER_TEMPLATE_NAME = "master_template.md"
GUIDELINES_REPO_PATH = Path(__file__).parent.parent.parent / "guidelines_repo"

def load_tech_params(technology_name: str) -> Dict[str, Any]:
    """Load technology-specific parameters from JSON config file."""
    param_file = CONFIG_PATH / f"{technology_name}.json"
    if not param_file.exists():
        raise ValueError(f"Configuration for technology '{technology_name}' not found.")
    
    with open(param_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_guideline_markdown(technology_name: str) -> str:
    """Generate guideline markdown content using Jinja2 template."""
    params = load_tech_params(technology_name)
    
    # Initialize Jinja2 environment
    env = Environment(loader=FileSystemLoader(CONFIG_PATH))
    template = env.get_template(MASTER_TEMPLATE_NAME)
    
    # Render template with parameters
    markdown_content = template.render(**params, technology_name=technology_name)
    return markdown_content

def save_guideline(technology_name: str, markdown_content: str) -> Path:
    """Save generated guideline to file system."""
    tech_dir = GUIDELINES_REPO_PATH / technology_name
    tech_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = tech_dir / "esd_latchup_guidelines.md"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    return file_path

def get_available_technologies() -> list[str]:
    """Get list of available technologies based on config files."""
    tech_files = CONFIG_PATH.glob("*.json")
    # Exclude master_template and MCP-related config files
    excluded_files = ["master_template", "mcp_config", "mcp_server_config"]
    return [f.stem for f in tech_files if f.stem not in excluded_files]

def validate_technology_config(technology_name: str) -> bool:
    """Validate that technology configuration is complete."""
    try:
        params = load_tech_params(technology_name)
        required_keys = ['esd_levels', 'latch_up_rules', 'approved_clamps']
        return all(key in params for key in required_keys)
    except (ValueError, json.JSONDecodeError):
        return False

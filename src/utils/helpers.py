import os
import json
import yaml
from typing import Dict, Any

def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
        
    # Handle .py files by importing as module
    if config_path.endswith('.py'):
        import importlib.util
        spec = importlib.util.spec_from_file_location("config", config_path)
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        return config.SETTINGS
    
    # Handle other formats
    ext = os.path.splitext(config_path)[1].lower()
    with open(config_path, 'r') as f:
        if ext == '.json':
            return json.load(f)
        elif ext in ['.yml', '.yaml']:
            return yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported config format: {ext}")

def export_model_card(card_data: Dict[str, Any], format: str = 'json') -> str:
    """Export model card in specified format."""
    if format == 'yaml':
        return yaml.dump(card_data)
    return json.dumps(card_data, indent=2)
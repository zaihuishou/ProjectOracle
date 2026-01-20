"""Configuration management for ProjectOracle."""

import json
import copy
from pathlib import Path
from typing import Any, Optional

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for Python 3.10


class ConfigManager:
    """Manages configuration loading from multiple sources."""
    
    DEFAULT_CONFIG = {
        "scan": {
            "max_files": 5000,
            "max_depth": 4,
            "max_file_size_kb": 500,
            "scan_timeout_seconds": 300,
            "follow_symlinks": False,
            "workers": 4,
            "custom_ignore_patterns": []
        },
        "analysis": {
            "include_tests": False,
            "detect_fragile_points": True,
            "generate_mermaid": True
        },
        "llm": {
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022",
            "max_input_tokens": 8000,
            "max_cost_usd": 0.50,
            "timeout_seconds": 30,
            "retry_attempts": 1
        },
        "output": {
            "backup_enabled": True,
            "diff_threshold_percent": 20,
            "keep_history": 5,
            "atomic_write": True
        },
        "security": {
            "scan_for_secrets": False
        }
    }
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.config = None
    
    def load(self, cli_overrides: Optional[dict] = None) -> dict[str, Any]:
        """
        Load configuration with priority: CLI > JSON > TOML > defaults.
        
        Args:
            cli_overrides: Configuration overrides from CLI arguments
        
        Returns:
            Merged configuration dictionary
        """
        config = copy.deepcopy(self.DEFAULT_CONFIG)
        
        # Layer 1: Try pyproject.toml
        pyproject_path = self.project_root / "pyproject.toml"
        if pyproject_path.exists():
            toml_config = self._load_from_toml(pyproject_path)
            if toml_config:
                config = self._merge_config(config, toml_config)
        
        # Layer 2: Try .projectoracle.config.json
        json_path = self.project_root / ".projectoracle.config.json"
        if json_path.exists():
            json_config = self._load_from_json(json_path)
            if json_config:
                config = self._merge_config(config, json_config)
        
        # Layer 3: Apply CLI overrides
        if cli_overrides:
            config = self._merge_config(config, cli_overrides)
        
        self.config = config
        return config
    
    def _load_from_toml(self, path: Path) -> Optional[dict]:
        """Load configuration from pyproject.toml [tool.projectoracle] section."""
        try:
            with open(path, "rb") as f:
                data = tomllib.load(f)
            
            tool_config = data.get("tool", {}).get("projectoracle", {})
            if not tool_config:
                return None
            
            # Convert flat structure to nested
            config = {}
            for key, value in tool_config.items():
                if "." in key:
                    section, subkey = key.split(".", 1)
                    if section not in config:
                        config[section] = {}
                    config[section][subkey] = value
                else:
                    config[key] = value
            
            return config
        except Exception as e:
            print(f"Warning: Failed to load config from {path}: {e}")
            return None
    
    def _load_from_json(self, path: Path) -> Optional[dict]:
        """Load configuration from JSON file."""
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load config from {path}: {e}")
            return None
    
    def _merge_config(self, base: dict, override: dict) -> dict:
        """Deep merge two configuration dictionaries."""
        result = copy.deepcopy(base)
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get(self, path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            path: Dot-separated path (e.g., "llm.max_cost_usd")
            default: Default value if path not found
        
        Returns:
            Configuration value or default
        """
        if self.config is None:
            self.load()
        
        parts = path.split(".")
        value = self.config
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        
        return value

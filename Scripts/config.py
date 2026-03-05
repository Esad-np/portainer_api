"""
Configuration Management

Loads and manages application configuration from YAML files and environment variables.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """Raised when configuration loading fails."""
    pass


class ConfigManager:
    """
    Manages application configuration from YAML files.
    
    Supports environment variable substitution in config values.
    """

    def __init__(self, config_dir: Path = None):
        """
        Initialize ConfigManager.
        
        Args:
            config_dir: Path to configuration directory. Defaults to ./config
        """
        if config_dir is None:
            # Find config relative to this file
            config_dir = Path(__file__).parent.parent / "config"
        
        self.config_dir = Path(config_dir)
        self.configs: Dict[str, Any] = {}
        
        if not self.config_dir.exists():
            raise ConfigError(f"Configuration directory not found: {self.config_dir}")

    def load(self, config_name: str) -> Dict[str, Any]:
        """
        Load a YAML configuration file.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            
        Returns:
            Configuration dictionary
            
        Raises:
            ConfigError: If file not found or YAML parsing fails
        """
        if config_name in self.configs:
            return self.configs[config_name]
        
        config_file = self.config_dir / f"{config_name}.yaml"
        
        if not config_file.exists():
            raise ConfigError(f"Configuration file not found: {config_file}")
        
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            # Expand environment variables in config values
            config = self._expand_env_vars(config)
            
            self.configs[config_name] = config
            logger.info(f"Loaded configuration: {config_name}")
            return config
        except yaml.YAMLError as e:
            raise ConfigError(f"Failed to parse {config_file}: {str(e)}")
        except Exception as e:
            raise ConfigError(f"Failed to load {config_file}: {str(e)}")

    def _expand_env_vars(self, obj: Any) -> Any:
        """
        Recursively expand ${VAR_NAME} environment variables in config.
        
        Args:
            obj: Configuration object (dict, list, or scalar)
            
        Returns:
            Configuration object with expanded variables
        """
        if isinstance(obj, dict):
            return {k: self._expand_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._expand_env_vars(item) for item in obj]
        elif isinstance(obj, str):
            return self._expand_string(obj)
        else:
            return obj

    def _expand_string(self, value: str) -> str:
        """
        Expand environment variables in a string value.
        Supports ${VAR_NAME} syntax.
        
        Args:
            value: String that may contain ${VAR_NAME} placeholders
            
        Returns:
            String with environment variables expanded
        """
        import re
        
        def replace_var(match):
            var_name = match.group(1)
            env_value = os.environ.get(var_name)
            if env_value is None:
                logger.warning(f"Environment variable not found: {var_name}")
                return match.group(0)  # Return unexpanded
            
            return env_value
        
        # Replace ${VAR_NAME} with environment variable values
        return re.sub(r'\$\{([^}]+)\}', replace_var, value)

    def get_portainer_config(self) -> Dict[str, Any]:
        """
        Load and return Portainer configuration.
        
        Returns:
            Portainer configuration dictionary
        """
        return self.load("portainer")

    def get(self, config_name: str, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key path.
        
        Supports nested keys with dot notation (e.g., "server.url")
        
        Args:
            config_name: Configuration name
            key: Key path (supports dot notation for nested values)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        config = self.load(config_name)
        
        keys = key.split(".")
        value = config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value


def create_config_manager(config_dir: Path = None) -> ConfigManager:
    """
    Factory function to create a ConfigManager instance.
    
    Args:
        config_dir: Optional config directory path
        
    Returns:
        ConfigManager instance
    """
    return ConfigManager(config_dir)

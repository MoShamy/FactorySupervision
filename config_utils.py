"""
Configuration utility for the Factory Supervision project.
Provides centralized access to paths and settings from config.json.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Configuration manager for the Factory Supervision project."""
    
    def __init__(self, config_file: str = "config.json"):
        """Initialize the configuration manager.
        
        Args:
            config_file: Path to the configuration file relative to project root.
        """
        self.project_root = Path(__file__).parent
        self.config_file = self.project_root / config_file
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    def get_path(self, *path_keys: str) -> Path:
        """Get a path from the configuration.
        
        Args:
            *path_keys: Nested keys to access the path (e.g., 'models', 'model1_local')
        
        Returns:
            Absolute Path object, creating directories if they don't exist.
        """
        current = self._config["paths"]
        for key in path_keys:
            if key not in current:
                raise KeyError(f"Path not found in config: {' -> '.join(path_keys)}")
            current = current[key]
        
        # Convert to absolute path
        path = self.project_root / current
        
        # Create directory if it doesn't exist and it's a directory path
        if not path.suffix:  # No file extension, assume it's a directory
            path.mkdir(parents=True, exist_ok=True)
        else:  # Has file extension, create parent directory
            path.parent.mkdir(parents=True, exist_ok=True)
        
        return path
    
    def get_setting(self, setting_key: str, default: Any = None) -> Any:
        """Get a setting from the configuration.
        
        Args:
            setting_key: The setting key to retrieve.
            default: Default value if setting not found.
        
        Returns:
            The setting value or default.
        """
        return self._config.get("settings", {}).get(setting_key, default)
    
    def get_file_path(self, file_key: str) -> Path:
        """Get a file path from the configuration.
        
        Args:
            file_key: The file key to retrieve.
        
        Returns:
            Absolute Path object, creating parent directories if needed.
        """
        if "files" not in self._config or file_key not in self._config["files"]:
            raise KeyError(f"File path not found in config: {file_key}")
        
        file_path = self.project_root / self._config["files"][file_key]
        file_path.parent.mkdir(parents=True, exist_ok=True)
        return file_path
    
    # Convenience properties for commonly used paths
    @property
    def logs_dir(self) -> Path:
        """Get the logs directory path."""
        return self.get_path("output", "logs")
    
    @property
    def results_dir(self) -> Path:
        """Get the results directory path."""
        return self.get_path("output", "results")
    
    @property
    def processed_videos_dir(self) -> Path:
        """Get the processed videos directory path."""
        return self.get_path("output", "processed_videos")
    
    @property
    def production_log_file(self) -> Path:
        """Get the production log file path."""
        return self.get_file_path("production_log")
    
    @property
    def video_input_dir(self) -> Path:
        """Get the video input directory path."""
        return self.get_path("data", "video_input")
    
    @property
    def image_input_dir(self) -> Path:
        """Get the image input directory path."""
        return self.get_path("data", "image_input")


# Global config instance
config = Config()

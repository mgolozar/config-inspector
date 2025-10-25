"""Base strategy interface for storage backends."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pathlib import Path
from typing import List

class StorageStrategy(ABC):
    """Abstract base class for storage backend implementations."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the storage strategy with configuration.
        
        Args:
            config: Backend-specific configuration dictionary
        """
        self.config = config
    
 
 
    @abstractmethod
    def list_files(self, prefix: str = "") -> list[str]:
        """
        List files in remote storage with optional prefix filter.
        
        Args:
            prefix: Optional prefix to filter results
        
        Returns:
            List of file paths in remote storage
        """
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate that the configuration is complete and valid.
        
        Returns:
            True if config is valid, False otherwise
        
        Raises:
            ValueError: If required configuration is missing
        """
        pass

    @abstractmethod
    def get_yaml_files(root: Path) -> List[Path]:
        """
        Get all YAML files in the remote storage.
        
        Args:
            root: Root directory or path to scan
        
        Returns:
            List of Path objects for discovered YAML files
        """
        pass

    @abstractmethod
    def read_file(self, remote_path: str) -> str:
        """Read file content as string from storage backend"""
        pass
    
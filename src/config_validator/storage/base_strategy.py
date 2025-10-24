"""Base strategy interface for storage backends."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pathlib import Path


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
    def upload(self, local_path: Path, remote_path: str) -> bool:
        """
        Upload a file from local path to remote storage.
        
        Args:
            local_path: Path to local file
            remote_path: Destination path in remote storage
        
        Returns:
            True if upload successful, False otherwise
        """
        pass
    
    @abstractmethod
    def download(self, remote_path: str, local_path: Path) -> bool:
        """
        Download a file from remote storage to local path.
        
        Args:
            remote_path: Source path in remote storage
            local_path: Destination path for local file
        
        Returns:
            True if download successful, False otherwise
        """
        pass
    
    @abstractmethod
    def exists(self, remote_path: str) -> bool:
        """
        Check if a file exists in remote storage.
        
        Args:
            remote_path: Path to check in remote storage
        
        Returns:
            True if file exists, False otherwise
        """
        pass
    
    @abstractmethod
    def delete(self, remote_path: str) -> bool:
        """
        Delete a file from remote storage.
        
        Args:
            remote_path: Path to delete in remote storage
        
        Returns:
            True if deletion successful, False otherwise
        """
        pass
    
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

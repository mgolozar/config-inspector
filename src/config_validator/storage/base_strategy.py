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
    def validate_config(self) -> bool:
 
        pass

    @abstractmethod
    def get_yaml_files(root: Path) -> List[Path]:
 
        pass

    @abstractmethod
    def read_file(self, remote_path: str) -> str:
     
        pass
    
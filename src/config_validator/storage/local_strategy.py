"""Local file system storage strategy implementation."""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .base_strategy import StorageStrategy


logger = logging.getLogger(__name__)


class LocalStrategy(StorageStrategy):
    """Storage strategy for local file system operations."""
    
    # Excluded directories when scanning file system
    EXCLUDED_DIRS = {'.git', 'node_modules', '.idea', '.venv', '__pycache__'}
    # Excluded file extensions
    EXCLUDED_EXTS = {'.zip', '.tar', '.gz', '.rar'}
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize local storage strategy.
        
        Args:
            config: Configuration containing 'base_path' for root directory
        
        Raises:
            ValueError: If base_path is not provided or is invalid
        """
        super().__init__(config)
        self.validate_config()
        self.base_path = Path(self.config.get("base_path", "."))
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"LocalStrategy initialized with base_path: {self.base_path}")
    
    
    def validate_config(self) -> bool:
        """Validate that base_path is configured."""
        base_path = self.config.get("base_path")
        if not base_path:
            raise ValueError("LocalStrategy requires 'base_path' in configuration")
        return True
    
    @staticmethod
    def fast_walk(root: Path) -> Iterable[Path]:
        """Yield all files under root (non-recursive stack, no symlinks)."""
        stack = [root]
        while stack:
            d = stack.pop()
            try:
                with os.scandir(d) as it:
                    for entry in it:
                        if entry.is_dir(follow_symlinks=False):
                            if entry.name in LocalStrategy.EXCLUDED_DIRS:
                                continue
                            stack.append(Path(entry.path))
                        # Files (and only files)
                        elif not entry.is_file(follow_symlinks=False):
                            continue    
                        else:
                            p = Path(entry.path)
                            if p.suffix.lower() in LocalStrategy.EXCLUDED_EXTS:
                                continue
                            yield p
            except (PermissionError, FileNotFoundError):
                continue
    
    @staticmethod
    def get_yaml_files(root: Path) -> Iterable[Path]:
        """Yield only YAML files discovered by fast_walk, as absolute paths."""
        for p in LocalStrategy.fast_walk(root):
            if p.suffix.lower() in {'.yml', '.yaml'}:
                # Return absolute path
                yield p.resolve()
    
    
    def discover_yaml_files(root: Path) -> List[Path]:
        """Discover all YAML files in directory tree."""
        unique = sorted({p for p in LocalStrategy.get_yaml_files(root)})
        return list(unique)  
    def read_file(self, remote_path: str) -> str:
        # remote_path is now always an absolute path from discovery
        file_path = Path(remote_path)
        with file_path.open("r", encoding="utf-8") as f:
            return f.read()

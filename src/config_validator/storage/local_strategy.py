"""Local file system storage strategy implementation."""

import logging
import os
import shutil
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
    
    def upload(self, local_path: Path, remote_path: str) -> bool:
        """Copy file from local path to base_path directory."""
        try:
            local_path = Path(local_path)
            if not local_path.exists():
                logger.error(f"Local file not found: {local_path}")
                return False
            
            dest_path = self.base_path / remote_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            if local_path.is_file():
                shutil.copy2(local_path, dest_path)
            else:
                shutil.copytree(local_path, dest_path, dirs_exist_ok=True)
            
            logger.info(f"Uploaded {local_path} to {dest_path}")
            return True
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return False
    
    def download(self, remote_path: str, local_path: Path) -> bool:
        """Copy file from base_path directory to local path."""
        try:
            source_path = self.base_path / remote_path
            local_path = Path(local_path)
            
            if not source_path.exists():
                logger.error(f"Remote file not found: {source_path}")
                return False
            
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            if source_path.is_file():
                shutil.copy2(source_path, local_path)
            else:
                shutil.copytree(source_path, local_path, dirs_exist_ok=True)
            
            logger.info(f"Downloaded {source_path} to {local_path}")
            return True
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return False
    
    def exists(self, remote_path: str) -> bool:
        """Check if file exists in base_path directory."""
        path = self.base_path / remote_path
        exists = path.exists()
        logger.debug(f"Checking existence of {path}: {exists}")
        return exists
    
    def delete(self, remote_path: str) -> bool:
        """Delete file from base_path directory."""
        try:
            path = self.base_path / remote_path
            
            if not path.exists():
                logger.error(f"Remote file not found: {path}")
                return False
            
            if path.is_file():
                path.unlink()
            else:
                shutil.rmtree(path)
            
            logger.info(f"Deleted {path}")
            return True
        except Exception as e:
            logger.error(f"Deletion failed: {e}")
            return False
    
    def list_files(self, prefix: str = "") -> list[str]:
        """List files in base_path directory with optional prefix filter."""
        try:
            files = []
            search_path = self.base_path
            
            if prefix:
                search_path = self.base_path / prefix
                if not search_path.exists():
                    return []
            
            for item in search_path.rglob("*"):
                if item.is_file():
                    rel_path = item.relative_to(self.base_path)
                    files.append(str(rel_path))
            
            logger.info(f"Listed {len(files)} files with prefix '{prefix}'")
            return sorted(files)
        except Exception as e:
            logger.error(f"List files failed: {e}")
            return []
    
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
        """Yield only YAML files discovered by fast_walk, relative to root."""
        for p in LocalStrategy.fast_walk(root):
            if p.suffix.lower() in {'.yml', '.yaml'}:
                # Return path relative to root
                try:
                    yield p.relative_to(root)
                except ValueError:
                    # If path is not relative to root, use as-is
                    yield p
    
    
    def discover_yaml_files(root: Path) -> List[Path]:
        """Discover all YAML files in directory tree."""
        unique = sorted({p for p in LocalStrategy.get_yaml_files(root)})
        return list(unique)  
    def read_file(self, remote_path: str) -> str:
        file_path = self.base_path / remote_path
        with file_path.open("r", encoding="utf-8") as f:
            return f.read()

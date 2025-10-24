"""Hadoop Distributed File System (HDFS) storage strategy implementation."""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from .base_strategy import StorageStrategy


logger = logging.getLogger(__name__)


class HDFSStrategy(StorageStrategy):
    """Storage strategy for HDFS operations."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize HDFS storage strategy.
        
        Args:
            config: Configuration containing:
                - host: HDFS namenode host (required)
                - port: HDFS namenode port (default: 8020)
                - user: HDFS user name (optional)
                - base_path: Base path in HDFS (default: /)
        
        Raises:
            ValueError: If required configuration is missing
        """
        super().__init__(config)
        self.validate_config()
        
        self.host = self.config.get("host")
        self.port = self.config.get("port", 8020)
        self.user = self.config.get("user", "hadoop")
        self.base_path = self.config.get("base_path", "/")
        
        try:
            from hdfs import InsecureClient
            self.hdfs_client = InsecureClient(
                f"http://{self.host}:{self.port}",
                user=self.user
            )
            logger.info(
                f"HDFSStrategy initialized with host: {self.host}, "
                f"port: {self.port}, user: {self.user}"
            )
        except ImportError:
            logger.error(
                "hdfs3 is not installed. Install it with: pip install hdfs3"
            )
            raise
    
    def _get_hdfs_path(self, remote_path: str) -> str:
        """Get full HDFS path with base_path."""
        base = self.base_path.rstrip("/")
        path = remote_path.lstrip("/")
        return f"{base}/{path}" if base else f"/{path}"
    
    def upload(self, local_path: Path, remote_path: str) -> bool:
        """Upload file to HDFS."""
        try:
            local_path = Path(local_path)
            if not local_path.exists():
                logger.error(f"Local file not found: {local_path}")
                return False
            
            hdfs_path = self._get_hdfs_path(remote_path)
            
            with open(local_path, "rb") as f:
                self.hdfs_client.write(hdfs_path, f, overwrite=True)
            
            logger.info(f"Uploaded {local_path} to hdfs://{self.host}:{self.port}{hdfs_path}")
            return True
        except Exception as e:
            logger.error(f"HDFS upload failed: {e}")
            return False
    
    def download(self, remote_path: str, local_path: Path) -> bool:
        """Download file from HDFS."""
        try:
            hdfs_path = self._get_hdfs_path(remote_path)
            local_path = Path(local_path)
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            with self.hdfs_client.read(hdfs_path) as reader:
                with open(local_path, "wb") as f:
                    f.write(reader.read())
            
            logger.info(f"Downloaded hdfs://{self.host}:{self.port}{hdfs_path} to {local_path}")
            return True
        except Exception as e:
            logger.error(f"HDFS download failed: {e}")
            return False
    
    def exists(self, remote_path: str) -> bool:
        """Check if file exists in HDFS."""
        try:
            hdfs_path = self._get_hdfs_path(remote_path)
            exists = self.hdfs_client.status(hdfs_path) is not None
            logger.debug(f"HDFS path exists: {hdfs_path} -> {exists}")
            return exists
        except FileNotFoundError:
            logger.debug(f"HDFS path not found: {hdfs_path}")
            return False
        except Exception as e:
            logger.error(f"HDFS exists check failed: {e}")
            return False
    
    def delete(self, remote_path: str) -> bool:
        """Delete file from HDFS."""
        try:
            hdfs_path = self._get_hdfs_path(remote_path)
            self.hdfs_client.delete(hdfs_path, recursive=False)
            logger.info(f"Deleted hdfs://{self.host}:{self.port}{hdfs_path}")
            return True
        except Exception as e:
            logger.error(f"HDFS deletion failed: {e}")
            return False
    
    def list_files(self, prefix: str = "") -> list[str]:
        """List files in HDFS with optional prefix filter."""
        try:
            search_path = self._get_hdfs_path(prefix) if prefix else self.base_path
            files = []
            
            if not self.exists(search_path):
                logger.warning(f"HDFS path does not exist: {search_path}")
                return []
            
            # Use walk to recursively list files
            for dirpath, dirnames, filenames in self.hdfs_client.walk(search_path):
                for filename in filenames:
                    full_path = f"{dirpath}/{filename}".replace("//", "/")
                    files.append(full_path)
            
            logger.info(f"Listed {len(files)} HDFS files with prefix '{prefix}'")
            return sorted(files)
        except Exception as e:
            logger.error(f"HDFS list files failed: {e}")
            return []
    
    def validate_config(self) -> bool:
        """Validate required HDFS configuration."""
        host = self.config.get("host")
        
        if not host:
            raise ValueError("HDFSStrategy requires 'host' in configuration")
        
        return True

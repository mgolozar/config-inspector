"""AWS S3 storage strategy implementation."""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from .base_strategy import StorageStrategy


logger = logging.getLogger(__name__)


class S3Strategy(StorageStrategy):
    """Storage strategy for AWS S3 operations."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize S3 storage strategy.
        
        Args:
            config: Configuration containing:
                - bucket_name: S3 bucket name (required)
                - region: AWS region (required)
                - aws_access_key_id: AWS access key (optional)
                - aws_secret_access_key: AWS secret key (optional)
                - prefix: Optional prefix for all objects
        
        Raises:
            ValueError: If required configuration is missing
        """
        super().__init__(config)
        self.validate_config()
        
        self.bucket_name = self.config.get("bucket_name")
        self.region = self.config.get("region")
        self.prefix = self.config.get("prefix", "")
        
        try:
            import boto3
            self.s3_client = boto3.client(
                "s3",
                region_name=self.region,
                aws_access_key_id=self.config.get("aws_access_key_id"),
                aws_secret_access_key=self.config.get("aws_secret_access_key"),
            )
            logger.info(
                f"S3Strategy initialized with bucket: {self.bucket_name}, "
                f"region: {self.region}"
            )
        except ImportError:
            logger.error("boto3 is not installed. Install it with: pip install boto3")
            raise
    
    def _get_s3_key(self, remote_path: str) -> str:
        """Get full S3 key with prefix."""
        if self.prefix:
            return f"{self.prefix.rstrip('/')}/{remote_path.lstrip('/')}"
        return remote_path
    
    def upload(self, local_path: Path, remote_path: str) -> bool:
        """Upload file to S3."""
        try:
            local_path = Path(local_path)
            if not local_path.exists():
                logger.error(f"Local file not found: {local_path}")
                return False
            
            s3_key = self._get_s3_key(remote_path)
            self.s3_client.upload_file(str(local_path), self.bucket_name, s3_key)
            logger.info(f"Uploaded {local_path} to s3://{self.bucket_name}/{s3_key}")
            return True
        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
            return False
    
    def download(self, remote_path: str, local_path: Path) -> bool:
        """Download file from S3."""
        try:
            s3_key = self._get_s3_key(remote_path)
            local_path = Path(local_path)
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.s3_client.download_file(self.bucket_name, s3_key, str(local_path))
            logger.info(f"Downloaded s3://{self.bucket_name}/{s3_key} to {local_path}")
            return True
        except Exception as e:
            logger.error(f"S3 download failed: {e}")
            return False
    
    def exists(self, remote_path: str) -> bool:
        """Check if object exists in S3."""
        try:
            s3_key = self._get_s3_key(remote_path)
            self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            logger.debug(f"S3 object exists: {s3_key}")
            return True
        except self.s3_client.exceptions.NoSuchKey:
            logger.debug(f"S3 object not found: {s3_key}")
            return False
        except Exception as e:
            logger.error(f"S3 exists check failed: {e}")
            return False
    
    def delete(self, remote_path: str) -> bool:
        """Delete object from S3."""
        try:
            s3_key = self._get_s3_key(remote_path)
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            logger.info(f"Deleted s3://{self.bucket_name}/{s3_key}")
            return True
        except Exception as e:
            logger.error(f"S3 deletion failed: {e}")
            return False
    
    def list_files(self, prefix: str = "") -> list[str]:
        """List objects in S3 bucket with optional prefix filter."""
        try:
            list_prefix = self._get_s3_key(prefix) if prefix else self.prefix
            paginator = self.s3_client.get_paginator("list_objects_v2")
            pages = paginator.paginate(
                Bucket=self.bucket_name,
                Prefix=list_prefix.rstrip("/") + "/" if list_prefix else ""
            )
            
            files = []
            for page in pages:
                if "Contents" in page:
                    for obj in page["Contents"]:
                        # Exclude directory markers (objects ending with /)
                        if not obj["Key"].endswith("/"):
                            files.append(obj["Key"])
            
            logger.info(f"Listed {len(files)} S3 objects with prefix '{list_prefix}'")
            return sorted(files)
        except Exception as e:
            logger.error(f"S3 list files failed: {e}")
            return []
    
    def validate_config(self) -> bool:
        """Validate required S3 configuration."""
        bucket_name = self.config.get("bucket_name")
        region = self.config.get("region")
        
        if not bucket_name:
            raise ValueError("S3Strategy requires 'bucket_name' in configuration")
        if not region:
            raise ValueError("S3Strategy requires 'region' in configuration")
        
        return True

# Implementation Guide

How to create and extend the storage backend system.

## Creating a Custom Strategy

### Step 1: Inherit from StorageStrategy

```python
from pathlib import Path
from typing import Any, Dict
from config_validator.storage import StorageStrategy

class MyCustomStrategy(StorageStrategy):
    """My custom storage implementation"""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(config)
        self.validate_config()
        # Initialize your backend
        self.client = self._init_client()
    
    def _init_client(self):
        """Initialize connection to your storage backend"""
        # Your initialization code
        pass
```

### Step 2: Implement Required Methods

```python
class MyCustomStrategy(StorageStrategy):
    
    def upload(self, local_path: Path, remote_path: str) -> bool:
        """Upload file to storage"""
        try:
            local_path = Path(local_path)
            if not local_path.exists():
                logger.error(f"File not found: {local_path}")
                return False
            
            # Your upload logic
            self.client.upload(str(local_path), remote_path)
            logger.info(f"Uploaded {local_path} to {remote_path}")
            return True
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return False
    
    def download(self, remote_path: str, local_path: Path) -> bool:
        """Download file from storage"""
        try:
            local_path = Path(local_path)
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Your download logic
            self.client.download(remote_path, str(local_path))
            logger.info(f"Downloaded {remote_path} to {local_path}")
            return True
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return False
    
    def exists(self, remote_path: str) -> bool:
        """Check if file exists"""
        try:
            # Your exists logic
            return self.client.exists(remote_path)
        except Exception as e:
            logger.error(f"Exists check failed: {e}")
            return False
    
    def delete(self, remote_path: str) -> bool:
        """Delete file from storage"""
        try:
            # Your delete logic
            self.client.delete(remote_path)
            logger.info(f"Deleted {remote_path}")
            return True
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return False
    
    def list_files(self, prefix: str = "") -> list[str]:
        """List files in storage"""
        try:
            # Your list logic
            files = self.client.list(prefix)
            logger.info(f"Listed {len(files)} files with prefix '{prefix}'")
            return files
        except Exception as e:
            logger.error(f"List failed: {e}")
            return []
    
    def validate_config(self) -> bool:
        """Validate configuration"""
        # Check required fields
        if not self.config.get("required_field"):
            raise ValueError("'required_field' is required in configuration")
        return True
```

### Step 3: Register Your Strategy

```python
from config_validator.storage import StorageStrategyFactory

# Register
StorageStrategyFactory.register("mybackend", MyCustomStrategy)

# Use
strategy = StorageStrategyFactory.create("mybackend", {
    "required_field": "value"
})
```

## File Organization

### Directory Structure

```
src/config_validator/storage/
├── __init__.py              # Package exports
├── base_strategy.py         # Abstract base class
├── local_strategy.py        # Local file system
├── s3_strategy.py           # AWS S3
├── hdfs_strategy.py         # Hadoop HDFS
└── strategy_loader.py       # Factory & loader
```

### Adding a New Strategy

1. Create new file: `my_strategy.py`
2. Inherit from `StorageStrategy`
3. Implement all abstract methods
4. Add to `__init__.py` exports
5. Register in `strategy_loader.py` (optional)

### Testing

Add tests in `tests/test_storage.py`:

```python
import pytest
from pathlib import Path

class TestMyStrategy:
    def test_upload(self, tmp_path):
        """Test upload operation"""
        config = {"required_field": "value"}
        strategy = StorageStrategyFactory.create("mybackend", config)
        
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        # Test upload
        result = strategy.upload(test_file, "remote/test.txt")
        assert result is True
    
    def test_download(self, tmp_path):
        """Test download operation"""
        strategy = StorageStrategyFactory.create("mybackend", config)
        
        # Test download
        result = strategy.download("remote/test.txt", tmp_path / "local.txt")
        assert result is True
    
    # ... more tests
```

## Best Practices

### 1. Error Handling

Always return `bool` for success/failure:

```python
def operation(self, path):
    try:
        # Operation code
        return True
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        return False
```

### 2. Logging

Log all important operations:

```python
import logging

logger = logging.getLogger(__name__)

logger.info(f"Operation succeeded: {details}")
logger.error(f"Operation failed: {error}")
logger.debug(f"Debug info: {details}")
```

### 3. Configuration Validation

Always validate configuration:

```python
def validate_config(self) -> bool:
    required_fields = ["field1", "field2"]
    for field in required_fields:
        if not self.config.get(field):
            raise ValueError(f"'{field}' is required")
    return True
```

### 4. Type Hints

Use complete type hints:

```python
from typing import Any, Dict, Optional

def method(self, param: str, optional: Optional[int] = None) -> bool:
    pass
```

### 5. Documentation

Document methods thoroughly:

```python
def upload(self, local_path: Path, remote_path: str) -> bool:
    """
    Upload a file to storage.
    
    Args:
        local_path: Path to local file
        remote_path: Destination path in storage
    
    Returns:
        True if successful, False otherwise
    
    Raises:
        None (all errors logged and return False)
    """
    pass
```

## Configuration Format

Define your configuration requirements:

```python
class MyStrategy(StorageStrategy):
    """
    Configuration format:
    {
        "required_field": "value",
        "optional_field": "default_value"
    }
    """
```

## Examples

### Redis Strategy Example

```python
class RedisStrategy(StorageStrategy):
    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(config)
        self.validate_config()
        
        import redis
        self.client = redis.Redis(
            host=config.get("host"),
            port=config.get("port", 6379)
        )
    
    def upload(self, local_path: Path, remote_path: str) -> bool:
        try:
            with open(local_path, 'rb') as f:
                self.client.set(remote_path, f.read())
            return True
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return False
    
    # ... implement other methods
```

### GCS Strategy Example

```python
class GCSStrategy(StorageStrategy):
    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(config)
        self.validate_config()
        
        from google.cloud import storage
        self.client = storage.Client()
        self.bucket = self.client.bucket(config.get("bucket_name"))
    
    def upload(self, local_path: Path, remote_path: str) -> bool:
        try:
            blob = self.bucket.blob(remote_path)
            blob.upload_from_filename(str(local_path))
            return True
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return False
    
    # ... implement other methods
```

## Integration Checklist

- [ ] Implement all abstract methods from StorageStrategy
- [ ] Add comprehensive error handling
- [ ] Add logging for all operations
- [ ] Validate configuration in __init__
- [ ] Write unit tests (90% coverage)
- [ ] Add documentation
- [ ] Type hint all methods
- [ ] Register with factory
- [ ] Add to __init__.py exports
- [ ] Update docs/CONFIGURATION.md
- [ ] Add configuration example in config/examples/
- [ ] Test with example code

## Testing Your Strategy

### Manual Testing

```python
from config_validator.storage import StorageStrategyFactory

# Create instance
strategy = StorageStrategyFactory.create("mybackend", {
    "required_field": "value"
})

# Test operations
print(strategy.upload(Path("test.txt"), "remote/test.txt"))
print(strategy.exists("remote/test.txt"))
print(strategy.list_files())
print(strategy.download("remote/test.txt", Path("downloaded.txt")))
print(strategy.delete("remote/test.txt"))
```

### Automated Testing

```bash
pytest tests/test_storage.py::TestMyStrategy -v
```

---

For more information, see:
- `QUICK_START.md` - Getting started
- `API_REFERENCE.md` - Complete API
- `ARCHITECTURE.md` - Architecture details

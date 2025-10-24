# API Reference

Complete reference for the storage backend API.

## StorageStrategy Interface

All storage backends implement this interface.

### Methods

#### upload(local_path: Path, remote_path: str) → bool

Upload a file from local path to remote storage.

**Parameters:**
- `local_path` (Path): Local file path
- `remote_path` (str): Destination path in storage

**Returns:** `True` if successful, `False` otherwise

**Example:**
```python
strategy.upload(Path("report.json"), "reports/2025-01-01.json")
```

---

#### download(remote_path: str, local_path: Path) → bool

Download a file from remote storage to local path.

**Parameters:**
- `remote_path` (str): Source path in storage
- `local_path` (Path): Destination local path

**Returns:** `True` if successful, `False` otherwise

**Example:**
```python
strategy.download("reports/2025-01-01.json", Path("report.json"))
```

---

#### exists(remote_path: str) → bool

Check if a file exists in remote storage.

**Parameters:**
- `remote_path` (str): Path to check

**Returns:** `True` if file exists, `False` otherwise

**Example:**
```python
if strategy.exists("reports/2025-01-01.json"):
    print("File exists!")
```

---

#### delete(remote_path: str) → bool

Delete a file from remote storage.

**Parameters:**
- `remote_path` (str): Path to delete

**Returns:** `True` if successful, `False` otherwise

**Example:**
```python
strategy.delete("reports/2025-01-01.json")
```

---

#### list_files(prefix: str = "") → list[str]

List files in storage with optional prefix filter.

**Parameters:**
- `prefix` (str): Optional prefix to filter results (default: "")

**Returns:** List of file paths

**Example:**
```python
files = strategy.list_files("reports/")
for f in files:
    print(f)
```

---

#### validate_config() → bool

Validate that the configuration is complete and valid.

**Returns:** `True` if valid

**Raises:** `ValueError` if configuration is invalid

**Example:**
```python
try:
    strategy.validate_config()
except ValueError as e:
    print(f"Config error: {e}")
```

---

## StorageStrategyFactory

Factory class for creating strategy instances.

### Methods

#### create(strategy_type: str, config: Dict[str, Any]) → StorageStrategy

Create a storage strategy instance.

**Parameters:**
- `strategy_type` (str): Type of strategy ('local', 's3', 'hdfs')
- `config` (dict): Backend-specific configuration

**Returns:** StorageStrategy instance

**Raises:** `ValueError` if strategy type is unknown or config is invalid

**Example:**
```python
strategy = StorageStrategyFactory.create("s3", {
    "bucket_name": "my-bucket",
    "region": "us-east-1"
})
```

---

#### register(name: str, strategy_class: type) → None

Register a custom storage strategy.

**Parameters:**
- `name` (str): Name of the strategy
- `strategy_class` (type): Class implementing StorageStrategy

**Raises:** `ValueError` if strategy_class doesn't inherit from StorageStrategy

**Example:**
```python
class MyStrategy(StorageStrategy):
    # Implementation...
    pass

StorageStrategyFactory.register("mybackend", MyStrategy)
```

---

#### get_available_strategies() → list[str]

Get list of available strategy names.

**Returns:** Sorted list of strategy names

**Example:**
```python
strategies = StorageStrategyFactory.get_available_strategies()
print(strategies)  # ['hdfs', 'local', 's3']
```

---

## Module-Level Functions

#### load_storage_strategy(storage_config: Dict[str, Any]) → StorageStrategy

Load a storage strategy from configuration dictionary.

**Parameters:**
- `storage_config` (dict): Configuration with 'type' and 'config' keys

**Returns:** StorageStrategy instance

**Raises:** `ValueError` if configuration is invalid

**Example:**
```python
config = {
    "type": "s3",
    "config": {
        "bucket_name": "my-bucket",
        "region": "us-east-1"
    }
}
strategy = load_storage_strategy(config)
```

**Configuration Format:**
```python
{
    "type": "s3",              # Required: strategy type
    "config": {                # Required: strategy config
        "bucket_name": "...",  # Backend-specific parameters
        "region": "..."
    }
}
```

---

## Strategy Implementations

### LocalStrategy

Local file system storage.

**Configuration:**
```python
{
    "type": "local",
    "config": {
        "base_path": "./data"  # Required
    }
}
```

**Import:**
```python
from config_validator.storage import LocalStrategy
```

---

### S3Strategy

AWS S3 storage.

**Configuration:**
```python
{
    "type": "s3",
    "config": {
        "bucket_name": "my-bucket",      # Required
        "region": "us-east-1",           # Required
        "aws_access_key_id": "...",      # Optional
        "aws_secret_access_key": "...",  # Optional
        "prefix": "configs/"             # Optional
    }
}
```

**Import:**
```python
from config_validator.storage import S3Strategy
```

**Dependencies:**
```bash
pip install boto3
```

---

### HDFSStrategy

Hadoop HDFS storage.

**Configuration:**
```python
{
    "type": "hdfs",
    "config": {
        "host": "namenode.example.com",  # Required
        "port": 8020,                    # Optional (default: 8020)
        "user": "hadoop",                # Optional (default: hadoop)
        "base_path": "/"                 # Optional (default: /)
    }
}
```

**Import:**
```python
from config_validator.storage import HDFSStrategy
```

**Dependencies:**
```bash
pip install hdfs3
```

---

## Usage Examples

### Basic Usage

```python
from pathlib import Path
from config_validator.storage import load_storage_strategy

# Load strategy
strategy = load_storage_strategy({
    "type": "local",
    "config": {"base_path": "./storage"}
})

# Upload file
strategy.upload(Path("report.json"), "reports/2025-01-01.json")

# Download file
strategy.download("reports/2025-01-01.json", Path("downloaded.json"))

# Check existence
if strategy.exists("reports/2025-01-01.json"):
    print("File found!")

# List files
files = strategy.list_files("reports/")

# Delete file
strategy.delete("reports/2025-01-01.json")
```

### Loading from YAML

```python
import yaml
from config_validator.storage import load_storage_strategy

with open("storage-config.yaml") as f:
    config = yaml.safe_load(f)

strategy = load_storage_strategy(config["storage"])
```

### Custom Strategy

```python
from config_validator.storage import StorageStrategy, StorageStrategyFactory

class RedisStrategy(StorageStrategy):
    def upload(self, local_path, remote_path):
        # Implementation
        pass
    
    # Implement other methods...

StorageStrategyFactory.register("redis", RedisStrategy)
strategy = StorageStrategyFactory.create("redis", {})
```

---

## Error Handling

All methods return `bool` for success/failure. Check logs for details:

```python
import logging

logging.basicConfig(level=logging.DEBUG)

strategy = load_storage_strategy(config)
if not strategy.upload(file, path):
    logger.error("Upload failed - check logs")
```

---

## Configuration Files

See `docs/CONFIGURATION.md` for complete configuration guide.

See `config/examples/` for example configurations.

---

For getting started, see `QUICK_START.md`.
For architecture details, see `ARCHITECTURE.md`.

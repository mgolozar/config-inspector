# Architecture & Design Patterns

## Overview

The storage backend system uses the **Strategy Pattern** to provide a flexible, extensible architecture for multiple storage providers.

## Design Pattern: Strategy

### Concept
- **Base Class**: `StorageStrategy` defines the interface
- **Concrete Strategies**: `LocalStrategy`, `S3Strategy`, `HDFSStrategy` implement specific backends
- **Factory**: `StorageStrategyFactory` creates strategy instances
- **Loader**: `load_storage_strategy()` loads from configuration

### Benefits
✅ Easy to add new backends without modifying existing code
✅ Each backend completely independent
✅ Runtime selection based on configuration
✅ No conditional logic in application code

## Component Diagram

```
┌─────────────────────────────────────────────────┐
│           Your Application                       │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
         ┌──────────────────────────┐
         │  load_storage_strategy() │
         │  (from YAML config)      │
         └────────────┬─────────────┘
                      │
                      ▼
         ┌──────────────────────────┐
         │ StorageStrategyFactory   │
         └────────────┬─────────────┘
                      │
       ┌──────────────┼──────────────┐
       │              │              │
       ▼              ▼              ▼
  LocalStrategy   S3Strategy    HDFSStrategy
       │              │              │
       ▼              ▼              ▼
   Local FS        AWS S3        HDFS
```

## Class Hierarchy

```
StorageStrategy (ABC)
├── upload()
├── download()
├── exists()
├── delete()
├── list_files()
└── validate_config()
    │
    ├── LocalStrategy
    │   - Uses: pathlib, shutil
    │   - Config: base_path
    │
    ├── S3Strategy
    │   - Uses: boto3
    │   - Config: bucket_name, region
    │
    └── HDFSStrategy
        - Uses: hdfs3
        - Config: host, port
```

## Configuration Flow

```
YAML File
    ↓
Config Dict
    ↓
load_storage_strategy()
    ↓
StorageStrategyFactory.create()
    ↓
Validate Config
    ↓
Instantiate Strategy
    ↓
Strategy Ready to Use
```

## Data Flow: Upload Operation

```
User Code
    │
    ├─ upload(local_path, remote_path)
    │
    ├─ Validate inputs
    │
    ├─ Strategy-specific implementation
    │   ├─ LocalStrategy: copy file
    │   ├─ S3Strategy: upload to S3
    │   └─ HDFSStrategy: write to HDFS
    │
    ├─ Log operation
    │
    └─ Return True/False
```

## Implementation Details

### StorageStrategy (Abstract Base)
- Defines interface all strategies must implement
- Provides configuration validation framework
- Located in: `base_strategy.py`

### LocalStrategy
- File system operations using pathlib
- Supports relative and absolute paths
- No external dependencies
- Located in: `local_strategy.py`

### S3Strategy
- AWS S3 operations using boto3
- Supports prefix organization
- Configurable region and credentials
- Handles pagination for large listings
- Located in: `s3_strategy.py`

### HDFSStrategy
- Hadoop operations using hdfs3
- Supports base path configuration
- Recursive file listing
- Located in: `hdfs_strategy.py`

### StorageStrategyFactory
- Registry-based strategy creation
- Case-insensitive type matching
- Extensible registration system
- Located in: `strategy_loader.py`

## Configuration Format

```yaml
storage:
  type: s3              # Strategy type
  config:              # Strategy-specific config
    bucket_name: ...
    region: ...
    prefix: ...
```

## Error Handling

- All operations return `bool` (True/False)
- Detailed errors logged (use logging module)
- Configuration validated before use
- Graceful failure with informative messages

## Extensibility

Add custom storage backend:

```python
from config_validator.storage import StorageStrategy, StorageStrategyFactory

class MyBackend(StorageStrategy):
    def upload(self, local_path, remote_path):
        # Implementation
        pass
    
    # ... implement all methods

# Register
StorageStrategyFactory.register("mybackend", MyBackend)

# Use
strategy = StorageStrategyFactory.create("mybackend", config)
```

## Key Design Principles

1. **Single Responsibility**: Each strategy handles one backend
2. **Open/Closed**: Open for extension, closed for modification
3. **Dependency Inversion**: Depend on abstractions, not implementations
4. **Strategy Pattern**: Encapsulate algorithms
5. **Factory Pattern**: Centralized object creation
6. **Configuration-Driven**: Behavior controlled by config

## Benefits

✅ **Flexibility**: Easy to switch between backends
✅ **Testability**: Mock strategies for testing
✅ **Maintainability**: Each backend is independent
✅ **Extensibility**: Add backends without modifying existing code
✅ **Type Safety**: Full type hints throughout

---

For more information, see:
- `QUICK_START.md` - Getting started
- `CONFIGURATION.md` - Configuration details
- `API_REFERENCE.md` - Complete API

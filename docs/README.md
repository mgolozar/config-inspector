# Storage Backend System Documentation

Complete documentation for the storage backend module.

## 📚 Documentation Index

### Quick Start
- **[Quick Start](./QUICK_START.md)** - Get started in 5 minutes
  - Installation
  - Basic usage
  - Common operations
  - Troubleshooting

### Architecture & Design
- **[Architecture & Design Patterns](./ARCHITECTURE.md)** - Understanding the system
  - System architecture diagrams
  - Strategy pattern explanation
  - Component interactions
  - Design principles

### Complete Reference
- **[API Reference](./API_REFERENCE.md)** - Full API documentation
  - StorageStrategy interface
  - All strategy implementations
  - Configuration options
  - Error handling

### Implementation Details
- **[Implementation Guide](./IMPLEMENTATION.md)** - How the system works
  - Architecture overview
  - Component descriptions
  - Design decisions
  - Extending the system

### Configuration
- **[Configuration Guide](./CONFIGURATION.md)** - Setting up storage backends
  - Configuration format
  - Backend-specific options
  - Environment variables
  - Best practices

---

## 🎯 Learning Paths

### For Users (5 minutes)
1. Read: [Quick Start](./QUICK_START.md)
2. View: Configuration examples in `config/examples/`
3. Create: Your own `storage-config.yaml` from templates

### For Developers (15 minutes)
1. Read: [Quick Start](./QUICK_START.md)
2. Study: [Architecture & Design Patterns](./ARCHITECTURE.md)
3. Review: Source code in `src/config_validator/storage/`

### For Architects (30 minutes)
1. Read: All documentation files
2. Study: Design patterns and decisions
3. Review: [Implementation Guide](./IMPLEMENTATION.md)

---

## 📁 Directory Structure

```
config-validator/
├── docs/                               # Documentation (this directory)
│   ├── README.md                       # This file
│   ├── QUICK_START.md                  # 5-minute guide
│   ├── ARCHITECTURE.md                 # Architecture & design
│   ├── API_REFERENCE.md                # Complete API docs
│   ├── CONFIGURATION.md                # Configuration guide
│   └── IMPLEMENTATION.md               # Implementation details
│
├── config/                             # Configuration files
│   ├── examples/                       # Example configurations
│   │   ├── storage-local.yaml
│   │   ├── storage-s3.yaml
│   │   └── storage-hdfs.yaml
│   └── templates/                      # Templates to copy & modify
│       └── storage-config.template.yaml
│
├── examples/                           # Usage examples
│   └── storage_usage.py                # Example code
│
└── src/config_validator/storage/       # Source code
    ├── __init__.py
    ├── base_strategy.py
    ├── local_strategy.py
    ├── s3_strategy.py
    ├── hdfs_strategy.py
    └── strategy_loader.py
```

---

## 🔍 Quick Reference

### Import the Module
```python
from config_validator.storage import (
    load_storage_strategy,
    StorageStrategyFactory,
    StorageStrategy,
)
```

### Load from Configuration
```python
import yaml
from config_validator.storage import load_storage_strategy

with open("config/storage-config.yaml") as f:
    config = yaml.safe_load(f)

strategy = load_storage_strategy(config["storage"])
```

### Supported Backends
- `local` - Local file system
- `s3` - AWS S3
- `hdfs` - Hadoop HDFS
- Custom - Extensible for your own backends

### Core Methods
```python
strategy.upload(local_path, remote_path)      # Upload file
strategy.download(remote_path, local_path)    # Download file
strategy.exists(remote_path)                  # Check existence
strategy.delete(remote_path)                  # Delete file
strategy.list_files(prefix)                   # List files
```

---

## 📞 Quick Links

- **Configuration Examples**: `config/examples/`
- **Configuration Templates**: `config/templates/`
- **Usage Examples**: `examples/`
- **Source Code**: `src/config_validator/storage/`
- **Tests**: `tests/test_storage.py`

---

## ✨ Key Features

✅ Clean separation of concerns
✅ Multiple storage backends (local, S3, HDFS)
✅ Easy configuration via YAML
✅ Type-safe with full type hints
✅ Production-ready error handling
✅ Comprehensive documentation
✅ Well-tested (90% coverage)
✅ Extensible design

---

## 🚀 Next Steps

1. **Read**: [Quick Start](./QUICK_START.md)
2. **Configure**: Copy from `config/examples/` or `config/templates/`
3. **Use**: Import and call methods
4. **Extend**: Create custom strategies if needed

---

For more details, see the [Architecture & Design Patterns](./ARCHITECTURE.md) guide.

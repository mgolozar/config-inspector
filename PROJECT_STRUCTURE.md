# Config Validator - Project Structure & Architecture

## Overview
Config Validator is a Python-based YAML configuration file validation system that supports multiple storage backends, extensible plugin-based validation rules, and file system watching capabilities.

**Version:** 0.1.0

---

## Project Directory Structure

```
config-validator/
├── src/config_validator/              # Main package source
│   ├── __init__.py                    # Package initialization
│   ├── __main__.py                    # CLI entry point
│   ├── cli.py                         # Command-line interface
│   │
│   ├── core/                          # Core validation logic
│   │   ├── __init__.py
│   │   ├── config.py                  # Configuration management
│   │   ├── validator.py               # Main validator class
│   │   ├── discovery.py               # File discovery
│   │   ├── plugins_loader.py          # Dynamic plugin loading
│   │   ├── report.py                  # Report generation
│   │   └── watcher.py                 # File system watcher
│   │
│   ├── storage/                       # Storage strategy pattern
│   │   ├── __init__.py
│   │   ├── base_strategy.py           # Abstract base class
│   │   ├── local_strategy.py          # Local file system implementation
│   │   ├── s3_strategy.py             # AWS S3 implementation
│   │   ├── hdfs_strategy.py           # HDFS implementation
│   │   └── strategy_loader.py         # Factory & loader
│   │
│   ├── plugins/                       # Validation plugins
│   │   ├── __init__.py
│   │   ├── base_plugin.py             # Abstract plugin interface
│   │   ├── check_env.py               # Environment validation plugin
│   │   ├── check_replica.py           # Replica validation plugin
│   │   └── sample_plugin.py           # Example plugin
│   │
│   └── utils/                         # Utilities
│       ├── __init__.py
│       └── logging_setup.py           # Logging configuration
│
├── tests/                             # Test suite
│   ├── test_validation.py             # Validator tests
│   ├── test_discovery.py              # Discovery tests
│   ├── test_plugins.py                # Plugin tests
│   └── test_storage.py                # Storage tests
│
├── config/                            # Configuration files
│   ├── storage/                       # Storage backend configs
│   │   ├── storage-local.yaml
│   │   ├── storage-s3.yaml
│   │   └── storage-hdfs.yaml
│   └── templates/
│       └── storage-config.template.yaml
│
├── docs/                              # Documentation
│   ├── API_REFERENCE.md
│   ├── ARCHITECTURE.md
│   ├── CONFIGURATION.md
│   ├── IMPLEMENTATION.md
│   ├── QUICK_START.md
│   └── README.md
│
├── examples/                          # Usage examples
│   └── storage_usage.py
│
├── Makefile                           # Build automation
├── pyproject.toml                     # Project metadata
└── validation-config.yaml             # Default validation config

```

---

## Core Classes & Their Behavior

### 1. **Validator Class** (`src/config_validator/core/validator.py`)
**Purpose:** Main validation orchestrator for YAML configuration files

**Type:** Static methods for stateless validation operations

**Methods:**

- `parse_yaml(path) -> dict[str, Any]`
  - Parse YAML file at given path using safe loader
  - Raises `ValueError` on malformed YAML

- `_load_yaml(path: Path) -> dict[str, Any]`
  - Load YAML file and return as dictionary
  - Returns empty dict if file is empty
  - Raises `ValueError` on parse errors

- `_validate_core(data: dict, config: ValidationConfig) -> list[str]`
  - Validate core configuration rules against loaded data
  - Checks required fields, replicas range, image format, environment variables
  - Returns list of error messages (empty if valid)

- `validate_file(path: Path, config: ValidationConfig = None) -> Dict[str, Any]`
  - Main validation endpoint for single YAML file
  - Handles list/dict data structures
  - Loads YAML, validates core rules, runs plugins, extracts registry
  - Returns structured result: `{path, valid, errors, registry, data}`

**Behavior:**
- Does not raise exceptions; returns errors in result structure
- Extracts registry name from image field using regex
- Runs all loaded plugins for comprehensive validation
- Non-critical plugin failures don't crash validation

---

### 2. **ValidationConfig Class** (`src/config_validator/core/config.py`)
**Purpose:** Encapsulates validation rules and configuration

**Type:** Dataclass

**Attributes:**
- `replicas_min: int = 1` - Minimum allowed replicas
- `replicas_max: int = 50` - Maximum allowed replicas
- `image_pattern: str` - Regex pattern for image format validation
- `required_fields: List[str]` - Required YAML fields (default: service, image, replicas)
- `env_key_case: str` - Env var case enforcement (UPPERCASE, lowercase, any)
- `custom_rules: List[ValidationRule]` - Custom validation rules

**Methods:**
- `load_validation_config(config_path) -> ValidationConfig`
  - Load config from YAML file or use defaults
  - Parses custom rules from file

- `save_validation_config(config, config_path) -> None`
  - Persist configuration to YAML file

---

### 3. **ValidationRule Class** (`src/config_validator/core/config.py`)
**Purpose:** Define individual validation rules

**Type:** Dataclass

**Attributes:**
- `field: str` - Field name to validate
- `rule_type: str` - Rule type (range, regex, required, enum, etc.)
- `min_value: Optional[int]` - For range validation
- `max_value: Optional[int]` - For range validation
- `pattern: Optional[str]` - For regex validation
- `allowed_values: Optional[List[str]]` - For enum validation
- `error_message: Optional[str]` - Custom error message

---

### 4. **Discovery Class** (`src/config_validator/core/discovery.py`)
**Purpose:** Discover YAML files using configured storage strategy

**Attributes:**
- `root: Path` - Root directory for discovery
- `_storageStrategy: StorageStrategy` - Storage backend strategy

**Methods:**
- `__init__(root: Path, storageStrategy: StorageStrategy)`
  - Initialize with root path and storage strategy

- `discover_yaml_files(root: Path) -> List[Path]`
  - Use storage strategy to find all YAML files
  - Returns sorted list of Path objects

**Behavior:**
- Delegates file discovery to storage strategy
- Works with any storage backend (local, S3, HDFS)

---

### 5. **StorageStrategy (Abstract Base Class)** (`src/config_validator/storage/base_strategy.py`)
**Purpose:** Define interface for storage backend implementations

**Type:** Abstract Base Class (ABC)

**Abstract Methods:**
- `upload(local_path: Path, remote_path: str) -> bool`
- `download(remote_path: str, local_path: Path) -> bool`
- `exists(remote_path: str) -> bool`
- `delete(remote_path: str) -> bool`
- `list_files(prefix: str = "") -> list[str]`
- `validate_config() -> bool`
- `get_yaml_files(root: Path) -> List[Path]`

**Behavior:**
- Enforces consistent interface across all storage implementations
- Allows pluggable storage backends

---

### 6. **LocalStrategy Class** (`src/config_validator/storage/local_strategy.py`)
**Purpose:** Local file system storage backend implementation

**Type:** Concrete implementation of StorageStrategy

**Class Attributes:**
- `EXCLUDED_DIRS` - Set of excluded directories (.git, node_modules, etc.)
- `EXCLUDED_EXTS` - Set of excluded file extensions (.zip, .tar, .gz, etc.)

**Methods:**

- `__init__(config: Dict[str, Any])`
  - Initialize with base_path configuration
  - Creates base_path directory if not exists

- `upload(local_path: Path, remote_path: str) -> bool`
  - Copy file from local path to base_path directory
  - Creates parent directories as needed

- `download(remote_path: str, local_path: Path) -> bool`
  - Copy file from base_path directory to local path

- `exists(remote_path: str) -> bool`
  - Check if file exists in base_path directory

- `delete(remote_path: str) -> bool`
  - Delete file or directory from base_path

- `list_files(prefix: str = "") -> list[str]`
  - List all files with optional prefix filter

- `validate_config() -> bool`
  - Validate that base_path is configured

- `fast_walk(root: Path) -> Iterable[Path]` (static)
  - Non-recursive stack-based directory traversal
  - Skips excluded directories and file types

- `get_yaml_files(root: Path) -> Iterable[Path]` (static)
  - Yield only YAML files (.yml, .yaml)

- `discover_yaml_files(root: Path) -> List[Path]` (static)
  - Get sorted unique list of all YAML files

**Behavior:**
- Uses `shutil.copy2()` and `shutil.copytree()` for file operations
- Efficient directory scanning using `os.scandir()`
- Logs all operations for debugging

---

### 7. **S3Strategy Class** (`src/config_validator/storage/s3_strategy.py`)
**Purpose:** AWS S3 storage backend implementation

**Type:** Concrete implementation of StorageStrategy

**Configuration:**
- `bucket_name` - S3 bucket name
- `region` - AWS region
- `prefix` - Optional prefix for all objects

**Behavior:**
- Uses boto3 for AWS interactions
- Implements all StorageStrategy methods for S3 operations

---

### 8. **HDFSStrategy Class** (`src/config_validator/storage/hdfs_strategy.py`)
**Purpose:** HDFS (Hadoop Distributed File System) storage backend

**Type:** Concrete implementation of StorageStrategy

**Configuration:**
- `namenode_host` - HDFS namenode hostname
- `namenode_port` - HDFS namenode port
- `base_path` - Base path in HDFS

---

### 9. **StorageStrategyFactory Class** (`src/config_validator/storage/strategy_loader.py`)
**Purpose:** Factory for creating storage strategy instances

**Type:** Factory pattern implementation

**Static Methods:**

- `create(strategy_type: str, config: Dict) -> StorageStrategy`
  - Create strategy instance by type name
  - Supported types: "local", "s3", "hdfs"
  - Raises `ValueError` for unknown types

- `register(name: str, strategy_class: type) -> None`
  - Register new custom storage strategy
  - Validates that class inherits from StorageStrategy

- `get_available_strategies() -> list[str]`
  - Return list of available strategy names

**Utility Function:**

- `load_storage_strategy(storage_config: Dict) -> StorageStrategy`
  - Load strategy from configuration dictionary
  - Expected format: `{type: "local", config: {...}}`

**Behavior:**
- Maintains registry of available strategies
- Enables dynamic strategy selection at runtime
- Supports custom strategy registration

---

### 10. **ValidationPlugin (Abstract Base Class)** (`src/config_validator/plugins/base_plugin.py`)
**Purpose:** Define interface for validation plugins

**Type:** Abstract Base Class

**Abstract Methods:**
- `validate(data: dict) -> List[str]`
  - Validate data and return list of error messages
  - Return empty list if validation passes

**Behavior:**
- Allows extension of validation logic without modifying core
- Each plugin validates specific concerns

---

### 11. **Plugin Implementations**

#### CheckEnvPlugin (`src/config_validator/plugins/check_env.py`)
- Validates environment variable requirements
- Checks for empty values, case sensitivity, required keys

#### CheckReplicaPlugin (`src/config_validator/plugins/check_replica.py`)
- Validates replica count constraints
- Custom error messages for replica violations

#### SamplePlugin (`src/config_validator/plugins/sample_plugin.py`)
- Example plugin for development and testing

---

### 12. **Plugin Loader** (`src/config_validator/core/plugins_loader.py`)
**Purpose:** Dynamically discover and load validation plugins

**Function:**

- `load_plugins() -> List[ValidationPlugin]`
  - Scans `config_validator.plugins` package
  - Finds all ValidationPlugin subclasses
  - Instantiates plugins with no-arg constructor
  - Returns list of plugin instances

**Behavior:**
- Automatic plugin discovery - no configuration needed
- Plugins must be in `config_validator.plugins` package
- Failures in individual plugins don't crash loading process

---

### 13. **Report Generator** (`src/config_validator/core/report.py`)
**Purpose:** Aggregate validation results and generate summary report

**Function:**

- `aggregate_and_summarize(results: Iterable[Dict]) -> Dict[str, Any]`
  - Aggregate validation results from multiple files
  - Count valid/invalid files and total issues
  - Count registry occurrences
  - Return structured report

**Report Structure:**
```python
{
    "summary": {
        "valid_count": int,
        "invalid_count": int,
        "total_issues": int,
        "registry_counts": {registry_name: count, ...}
    },
    "files": [
        {path, valid, errors, registry, data},
        ...
    ]
}
```

---

### 14. **File Watcher** (`src/config_validator/core/watcher.py`)
**Purpose:** Monitor file system for YAML changes and trigger revalidation

**Functions:**

- `_snapshot(root: Path) -> Dict[str, float]`
  - Create snapshot of all .yml/.yaml files with mtimes
  - Returns mapping of absolute paths to modification times

- `watch_polling(root: Path, on_change: Callable, interval: float = 1.0)`
  - Simple polling-based file watcher
  - Calls `on_change()` on initial run and whenever files change
  - Runs indefinitely until interrupted
  - Portable across platforms

**Behavior:**
- Uses file modification time comparison
- No external dependencies (unlike watchdog)
- Simple and reliable for small directories

---

### 15. **CLI Interface** (`src/config_validator/cli.py`)
**Purpose:** Command-line interface for running validator

**Functions:**

- `parse_args(argv: list[str] | None = None) -> argparse.Namespace`
  - Parse command-line arguments

- `run_once(root, report_path, config_path, replicas_min, replicas_max) -> dict`
  - Single validation run:
    1. Load validation config
    2. Discover YAML files using Discovery
    3. Validate each file using Validator
    4. Generate and save report

- `main(argv: list[str] | None = None) -> int`
  - Main entry point
  - Support watch mode for continuous validation

**Command-line Arguments:**
- `--path` - Root directory to scan
- `--report` - Output JSON report path
- `--config` - Validation configuration file
- `--replicas-min` - Minimum replicas override
- `--replicas-max` - Maximum replicas override
- `--watch` - Enable file watching mode
- `--verbose` - Verbose logging

---

## Data Flow

```
User Input (CLI)
    ↓
CLI Parser → run_once()
    ↓
Load ValidationConfig
    ↓
Create Discovery + Storage Strategy
    ↓
discover_yaml_files()
    ↓
For each YAML file:
    ├→ Validator.validate_file()
    │   ├→ Load YAML
    │   ├→ _validate_core()
    │   ├→ Load & run Plugins
    │   └→ Extract registry
    └→ Result: {path, valid, errors, registry, data}
    ↓
aggregate_and_summarize()
    ↓
Generate Report JSON
    ↓
Output Report
```

---

## Design Patterns Used

1. **Strategy Pattern** - StorageStrategy and implementations (Local, S3, HDFS)
2. **Factory Pattern** - StorageStrategyFactory for dynamic strategy creation
3. **Plugin Architecture** - ValidationPlugin interface for extensibility
4. **Dataclass Pattern** - Configuration management
5. **Singleton-like Pattern** - Global plugin and strategy registries
6. **Template Method** - Common validation workflow

---

## Key Features

✅ **Multi-Backend Support** - Local filesystem, AWS S3, HDFS
✅ **Extensible Validation** - Plugin-based custom rules
✅ **Configuration-Driven** - YAML-based validation config
✅ **File Watching** - Continuous validation with polling
✅ **Comprehensive Reporting** - JSON reports with summaries
✅ **Error Handling** - Non-critical failures don't crash validation
✅ **Logging** - Full operation logging for debugging

---

## Configuration Example

**validation-config.yaml:**
```yaml
replicas_min: 1
replicas_max: 50
image_pattern: ^(?P<registry>[\w.-]+(?::\d+)?)/(?P<service>[\w.-]+):(?P<version>[\w.-]+)$
required_fields:
  - service
  - image
  - replicas
env_key_case: UPPERCASE
custom_rules:
  - field: service
    rule_type: regex
    pattern: ^[a-z-]+$
    error_message: Service name must be lowercase with hyphens
```

---

## Usage Examples

**Basic Validation:**
```bash
python -m config_validator --path ./configs --report report.json
```

**With Custom Config:**
```bash
python -m config_validator --path ./configs --config custom-config.yaml
```

**Watch Mode:**
```bash
python -m config_validator --path ./configs --watch --verbose
```

**Override Parameters:**
```bash
python -m config_validator --path ./configs --replicas-min 2 --replicas-max 100
```

---

## Testing Structure

- **test_validation.py** - Validator class tests
- **test_discovery.py** - File discovery tests
- **test_plugins.py** - Plugin loading and execution tests
- **test_storage.py** - Storage strategy tests

# Config Validator - Logging Guide

## 📝 Overview

The config-validator now includes comprehensive logging throughout the application. Logs are written to:
1. **Console** - For immediate feedback during execution
2. **File** - For permanent record and debugging

---

## 📂 Where Are the Logs?

### Default Log Location
```
config-validator/
└── logs/
    └── config-validator.log
```

### Log File Path
```
logs/config-validator.log
```

---

## 🚀 How to Enable Logging

### Using Command Line

**Default (INFO level):**
```bash
config-validator --path ./configs --report report.json
```
Creates: `logs/config-validator.log`

**Verbose (DEBUG level):**
```bash
config-validator --path ./configs --report report.json --verbose
```
Creates: `logs/config-validator.log` with more detailed information

---

## 📋 Log Levels Explained

| Level | What It Shows | When to Use |
|-------|--------------|------------|
| **DEBUG** | Detailed diagnostic info | Development, troubleshooting |
| **INFO** | General informational messages | Normal operation |
| **WARNING** | Warning messages | Validation issues |
| **ERROR** | Error messages with exceptions | Something went wrong |
| **CRITICAL** | Critical errors | Application failure |

---

## 📊 Log Format

### Console Format (Standard)
```
2024-01-15 14:32:45 | INFO | config_validator.cli | Logging level set to: INFO
```

### File Format (Detailed)
```
2024-01-15 14:32:45 | INFO     | config_validator.cli:22 | _setup_logging() | Logging level set to: INFO
```

File logs include:
- Timestamp
- Log level
- Module name and line number
- Function name
- Message

---

## 📖 Example Log Output

### When Running Validation

```bash
$ config-validator --path ./configs --report report.json --verbose
```

### Console Output
```
2024-01-15 14:32:45 | DEBUG | config_validator.cli | Logging level set to: DEBUG
2024-01-15 14:32:46 | INFO | config_validator.cli | Logging configured. File logs: logs/config-validator.log
2024-01-15 14:32:46 | DEBUG | config_validator.core.validator | Starting validation for file: test-config.yaml
2024-01-15 14:32:46 | DEBUG | config_validator.core.validator | Successfully read file: test-config.yaml
2024-01-15 14:32:46 | DEBUG | config_validator.core.validator | Successfully parsed YAML from file: test-config.yaml
2024-01-15 14:32:46 | DEBUG | config_validator.core.validator | Starting core validation. Data type: <class 'dict'>
2024-01-15 14:32:46 | DEBUG | config_validator.core.validator | Replicas validation passed: 3
2024-01-15 14:32:46 | DEBUG | config_validator.core.validator | Image validation passed: myregistry.com/my-test-service:1.0.0
2024-01-15 14:32:46 | DEBUG | config_validator.core.validator | Environment variables case validation passed (UPPERCASE)
2024-01-15 14:32:46 | INFO | config_validator.core.validator | Core validation completed with 0 error(s)
2024-01-15 14:32:46 | DEBUG | config_validator.core.validator | Extracted registry: myregistry.com
2024-01-15 14:32:46 | DEBUG | config_validator.core.validator | Loaded 2 plugins
2024-01-15 14:32:46 | INFO | config_validator.core.validator | File test-config.yaml validation PASSED
```

### File Output (logs/config-validator.log)
Same as console, but with more details including line numbers and function names.

---

## 🔍 How to Read the Logs

### Find Errors
```bash
# Windows
findstr "ERROR\|CRITICAL" logs/config-validator.log

# Linux/Mac
grep "ERROR\|CRITICAL" logs/config-validator.log
```

### Find Validation Failures
```bash
# Windows
findstr "FAILED" logs/config-validator.log

# Linux/Mac
grep "FAILED" logs/config-validator.log
```

### Find Specific File Issues
```bash
# Windows
findstr "test-config.yaml" logs/config-validator.log

# Linux/Mac
grep "test-config.yaml" logs/config-validator.log
```

### Show Last N Lines
```bash
# Windows (PowerShell)
Get-Content logs/config-validator.log -Tail 50

# Linux/Mac
tail -50 logs/config-validator.log
```

---

## 💻 View Logs in Real Time

### Windows (PowerShell)
```powershell
# Follow log file in real-time
Get-Content logs/config-validator.log -Wait -Tail 20
```

### Linux/Mac
```bash
# Follow log file in real-time
tail -f logs/config-validator.log
```

---

## 📝 What Gets Logged

### File Reading
```
✓ File successfully read
✓ File read failed with error
```

### YAML Parsing
```
✓ YAML successfully parsed
✗ YAML parse error details
```

### Core Validation
```
✓ Required fields validation
✓ Replicas range validation
✓ Image format validation
✓ Environment variables validation
```

### Plugin Execution
```
✓ Number of plugins loaded
✓ Plugin validation results
✗ Plugin errors
```

### Overall Results
```
✓ File validation PASSED
✗ File validation FAILED with X errors
```

---

## 🐍 Programmatic Logging Usage

### In Python Code

```python
from config_validator.utils.logging_setup import configure_logging
from config_validator.core.validator import ValidationSession
from config_validator.storage.local_strategy import LocalStrategy
from config_validator.core.config import ValidationConfig
import logging

# Setup logging
configure_logging(level="DEBUG", log_file="my_logs.log")

# Get logger
logger = logging.getLogger(__name__)

# Now your code can use logging
logger.info("Starting my application")
logger.debug("Debug information")
logger.warning("This is a warning")
logger.error("An error occurred", exc_info=True)
```

### Create Custom Logger

```python
import logging

logger = logging.getLogger("my_module")
logger.info("Message from my module")
```

---

## 🔧 Advanced: Customize Logging

### Change Log File Location

```python
from config_validator.utils.logging_setup import configure_logging

# Log to custom location
configure_logging(level="DEBUG", log_file="./my_custom_logs/validator.log")
```

### Log Levels in Code

```python
import logging

logger = logging.getLogger("config_validator")

logger.debug("Development info")      # Level 0
logger.info("General info")           # Level 1
logger.warning("Warning")             # Level 2
logger.error("Error occurred")        # Level 3
logger.critical("Critical failure")   # Level 4
```

---

## 📊 Log Analysis

### Find All Errors
```bash
# PowerShell
(Get-Content logs/config-validator.log) | Select-String "ERROR"

# Bash
grep ERROR logs/config-validator.log
```

### Count Validations
```bash
# PowerShell
(Get-Content logs/config-validator.log) | Select-String "validation" | Measure-Object

# Bash
grep validation logs/config-validator.log | wc -l
```

### Extract Error Messages
```bash
# PowerShell
(Get-Content logs/config-validator.log) | Select-String "ERROR" | ForEach-Object { $_.Line }

# Bash
grep ERROR logs/config-validator.log | awk -F'|' '{print $NF}'
```

---

## 🎯 Debugging with Logs

### Step 1: Run with Verbose Mode
```bash
config-validator --path ./configs --verbose
```

### Step 2: Check Log File
```bash
# View entire log
cat logs/config-validator.log

# View last 100 lines
tail -100 logs/config-validator.log
```

### Step 3: Search for Issues
```bash
# Find error files
grep "validation FAILED" logs/config-validator.log

# Find which file had issues
grep "File.*FAILED" logs/config-validator.log
```

### Step 4: Analyze Error
```bash
# See error details for specific file
grep "test-config.yaml" logs/config-validator.log
```

---

## 🚨 Common Log Messages

### Success
```
File test-config.yaml validation PASSED
Core validation completed with 0 error(s)
```

### File Not Found
```
ERROR | Failed to read file: [Errno 2] No such file or directory
```

### Invalid YAML
```
ERROR | YAML parse error in test-config.yaml: ...
```

### Validation Failures
```
WARNING | Missing required keys: ['service', 'image']
WARNING | replicas must be an integer between 1 and 50
WARNING | image must match <registry>/<service>:<version>
```

### Plugin Error
```
ERROR | Plugin CheckEnvPlugin error: ...
```

---

## 📈 Log Rotation (Optional)

To prevent logs from growing too large, use log rotation:

```python
from logging.handlers import RotatingFileHandler
import logging

# Create rotating file handler
handler = RotatingFileHandler(
    'logs/config-validator.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5  # Keep 5 backup files
)
```

---

## ✅ Best Practices

1. **Always enable DEBUG mode when troubleshooting:**
   ```bash
   config-validator --path ./configs --verbose
   ```

2. **Check logs after running validator:**
   ```bash
   tail logs/config-validator.log
   ```

3. **Save logs for analysis:**
   ```bash
   cp logs/config-validator.log logs/backup_$(date +%Y%m%d_%H%M%S).log
   ```

4. **Review logs regularly for patterns**

5. **Archive old logs periodically**

---

## 📞 Troubleshooting

### Logs Not Being Created
```bash
# Make sure logs directory exists
mkdir -p logs

# Run validator again
config-validator --path ./configs
```

### Logs File Too Large
```bash
# Clear old logs (Windows)
del logs\config-validator.log

# Clear old logs (Linux/Mac)
rm logs/config-validator.log
```

### Can't Find Specific File in Logs
```bash
# Search for file
grep "yourfile" logs/config-validator.log

# If not found, check if file was validated
dir *.yaml  # List YAML files
```

---

## 🎯 Summary

- **Logs stored in:** `logs/config-validator.log`
- **Console logs:** Real-time feedback (controlled by `--verbose`)
- **File logs:** Permanent record of all events
- **Enable debugging:** Use `--verbose` flag
- **View logs:** Use `tail`, `cat`, or text editor

Logs are now comprehensive and help you debug any issues! 🚀

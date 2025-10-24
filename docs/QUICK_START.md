# Quick Start Guide

Get up and running with the storage backend system in 5 minutes.

## 1. Installation

The storage system is included in the project. Optional backends require additional packages:

```bash
# For AWS S3 support
pip install boto3

# For Hadoop HDFS support
pip install hdfs3
```

## 2. Configuration

Choose your storage backend and copy the appropriate configuration:

### Option A: Local File System (Development)
```bash
cp config/examples/storage-local.yaml storage-config.yaml
```

### Option B: AWS S3 (Production)
```bash
cp config/examples/storage-s3.yaml storage-config.yaml
# Edit with your bucket details
```

### Option C: Hadoop HDFS (Big Data)
```bash
cp config/examples/storage-hdfs.yaml storage-config.yaml
# Edit with your namenode details
```

### Option D: Use a Template
```bash
cp config/templates/storage-config.template.yaml storage-config.yaml
# Edit with your desired settings
```

## 3. Basic Usage

```python
import yaml
from pathlib import Path
from config_validator.storage import load_storage_strategy

# Load configuration
with open("storage-config.yaml") as f:
    config = yaml.safe_load(f)

# Create storage strategy
storage = load_storage_strategy(config["storage"])

# Upload a file
storage.upload(Path("report.json"), "reports/2025-01-01.json")

# Download a file
storage.download("reports/2025-01-01.json", Path("downloaded.json"))

# Check if file exists
if storage.exists("reports/2025-01-01.json"):
    print("File exists!")

# List files
files = storage.list_files("reports/")
for f in files:
    print(f)

# Delete a file
storage.delete("reports/2025-01-01.json")
```

## 4. Common Operations

### Upload
```python
storage.upload(Path("local_file.txt"), "remote/path/file.txt")
```

### Download
```python
storage.download("remote/path/file.txt", Path("local_file.txt"))
```

### Check Existence
```python
if storage.exists("remote/path/file.txt"):
    print("File exists")
```

### List Files
```python
# List all files
all_files = storage.list_files()

# List files with prefix
config_files = storage.list_files("configs/")
```

### Delete
```python
storage.delete("remote/path/file.txt")
```

## 5. Configuration Details

### Local Storage
```yaml
storage:
  type: local
  config:
    base_path: ./data
```

### AWS S3
```yaml
storage:
  type: s3
  config:
    bucket_name: my-bucket
    region: us-east-1
```

### Hadoop HDFS
```yaml
storage:
  type: hdfs
  config:
    host: namenode.example.com
    port: 8020
```

## 6. Error Handling

All operations return `bool` for success/failure:

```python
result = storage.upload(local_path, remote_path)
if result:
    print("Success!")
else:
    print("Failed - check logs")
```

Enable logging to see details:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 7. Troubleshooting

### Unknown storage strategy error
- Check the `type` field - must be: `local`, `s3`, or `hdfs`

### boto3 not installed
```bash
pip install boto3
```

### hdfs3 not installed
```bash
pip install hdfs3
```

### Upload/Download fails
- Enable DEBUG logging (see Error Handling above)
- Check file permissions
- Verify storage service is accessible

## 8. Next Steps

- See examples: `examples/storage_usage.py`
- Read full API: `docs/API_REFERENCE.md`
- View architecture: `docs/ARCHITECTURE.md`

---

**That's it! You're ready to use storage backends.** 🚀

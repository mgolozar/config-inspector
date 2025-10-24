# Configuration Guide

Complete guide to configuring storage backends.

## Configuration Format

All storage configurations follow this YAML structure:

```yaml
storage:
  type: <backend_type>        # s3, local, hdfs
  config:                     # Backend-specific configuration
    <key1>: <value1>
    <key2>: <value2>
```

## Local File System Backend

### Configuration
```yaml
storage:
  type: local
  config:
    base_path: ./data         # Can be absolute or relative path
```

### Use Cases
- Development and testing
- Single-machine deployments
- Temporary file storage

### Requirements
- Write permissions to the base directory
- No external dependencies

### Example
```yaml
storage:
  type: local
  config:
    base_path: /var/storage/configs
```

---

## AWS S3 Backend

### Configuration
```yaml
storage:
  type: s3
  config:
    bucket_name: my-bucket                    # S3 bucket name (required)
    region: us-east-1                         # AWS region (required)
    aws_access_key_id: ${AWS_ACCESS_KEY_ID}   # Optional (uses AWS chain if not set)
    aws_secret_access_key: ${AWS_SECRET_KEY}  # Optional (uses AWS chain if not set)
    prefix: configs/                          # Optional: prefix for all objects
```

### Use Cases
- Production deployments
- Multi-region distribution
- Cloud-native applications
- Scalable storage

### Requirements
```bash
pip install boto3
```

### AWS Credentials

The system uses AWS's credential chain in this order:
1. Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
2. AWS credentials file (`~/.aws/credentials`)
3. IAM instance role (if running on EC2)
4. Values in configuration file

### Example - Development
```yaml
storage:
  type: s3
  config:
    bucket_name: dev-configs
    region: us-east-1
```

### Example - Production
```yaml
storage:
  type: s3
  config:
    bucket_name: prod-configs
    region: us-east-1
    prefix: production/
```

### Example - With Environment Variables
```yaml
storage:
  type: s3
  config:
    bucket_name: ${S3_BUCKET}
    region: ${AWS_REGION}
    prefix: configs/
```

---

## Hadoop HDFS Backend

### Configuration
```yaml
storage:
  type: hdfs
  config:
    host: namenode.example.com              # HDFS namenode host (required)
    port: 8020                              # HDFS port (optional, default: 8020)
    user: hadoop                            # HDFS user (optional, default: hadoop)
    base_path: /configs                     # Base path in HDFS (optional, default: /)
```

### Use Cases
- Big data environments
- Hadoop clusters
- Large-scale data processing
- Distributed storage

### Requirements
```bash
pip install hdfs3
```

### Example - Development Cluster
```yaml
storage:
  type: hdfs
  config:
    host: namenode-dev.internal
    port: 8020
    user: hadoop
    base_path: /data/configs
```

### Example - Production Cluster
```yaml
storage:
  type: hdfs
  config:
    host: namenode-prod.internal
    port: 8020
    user: hadoop
    base_path: /production/configs
```

---

## Environment Variables

You can use environment variables in your YAML files:

```yaml
storage:
  type: ${STORAGE_TYPE}                  # local, s3, hdfs
  config:
    bucket_name: ${S3_BUCKET}
    region: ${AWS_REGION}
    base_path: ${STORAGE_BASE_PATH}
```

Load and interpolate in Python:
```python
import os
import yaml

# Load YAML
with open("storage-config.yaml") as f:
    content = f.read()

# Interpolate environment variables
content = content.format(**os.environ)

# Parse YAML
config = yaml.safe_load(content)
```

---

## Configuration Best Practices

### 1. Use Configuration Files
Never hardcode storage configuration in code. Always use YAML files.

```python
# ✅ Good
with open("config/storage-config.yaml") as f:
    config = yaml.safe_load(f)
strategy = load_storage_strategy(config["storage"])

# ❌ Bad
strategy = StorageStrategyFactory.create("s3", {
    "bucket_name": "my-bucket"
})
```

### 2. Environment-Specific Configuration
Create separate config files for each environment:

```
config/
├── storage-dev.yaml         # Development
├── storage-staging.yaml     # Staging
└── storage-prod.yaml        # Production
```

Load based on environment:
```python
import os
env = os.getenv("ENVIRONMENT", "dev")
config_file = f"config/storage-{env}.yaml"
```

### 3. Use Templates
Start from a template and customize:

```bash
cp config/templates/storage-config.template.yaml storage-config.yaml
# Edit storage-config.yaml with your values
```

### 4. Store Secrets Securely
Don't commit credentials to version control:

```yaml
storage:
  type: s3
  config:
    bucket_name: my-bucket          # OK to commit
    region: us-east-1               # OK to commit
    aws_access_key_id: ${AWS_KEY}    # Use environment variables
    aws_secret_access_key: ${AWS_SECRET}
```

Add to `.gitignore`:
```
# Exclude configuration with secrets
storage-config.yaml
config/storage-*.yaml  # if containing secrets
```

### 5. Document Your Configuration
Add comments to help users understand required settings:

```yaml
# Storage Backend Configuration
# This file defines where and how files are stored

storage:
  # Backend type: local, s3, hdfs
  type: s3
  
  config:
    # S3 bucket name (required)
    bucket_name: my-production-bucket
    
    # AWS region (required)
    region: us-east-1
    
    # Optional: prefix for organizing objects
    prefix: configs/
```

### 6. Validate Configuration
Always validate before using:

```python
try:
    strategy = load_storage_strategy(config["storage"])
    print("✅ Configuration valid")
except ValueError as e:
    print(f"❌ Configuration error: {e}")
```

---

## Common Configuration Scenarios

### Scenario 1: Local Development
```yaml
storage:
  type: local
  config:
    base_path: ./storage/local
```

### Scenario 2: AWS S3 Production
```yaml
storage:
  type: s3
  config:
    bucket_name: prod-configs-bucket
    region: us-east-1
    prefix: application/
```

### Scenario 3: Hadoop Cluster
```yaml
storage:
  type: hdfs
  config:
    host: namenode.bigdata.cluster
    port: 8020
    user: analytics
    base_path: /data/configs
```

### Scenario 4: Multi-Environment with Environment Variables
```yaml
storage:
  type: ${STORAGE_TYPE}
  config:
    # For S3
    bucket_name: ${S3_BUCKET}
    region: ${AWS_REGION}
    # For HDFS
    host: ${HDFS_HOST}
    port: ${HDFS_PORT}
    # For Local
    base_path: ${STORAGE_PATH}
```

---

## Troubleshooting

### Configuration Not Found
- Check file path is correct
- Verify file exists: `ls -la config/storage-config.yaml`

### Invalid Configuration Error
- Check YAML syntax: Use a YAML validator
- Verify required fields are present
- Check field names are correct (case-sensitive)

### Connection Fails After Configuration
- Verify service is running (S3, HDFS, etc.)
- Check network connectivity
- Verify credentials/permissions
- Enable logging: `logging.basicConfig(level=logging.DEBUG)`

### Template Not Working
- Copy template correctly: `cp config/templates/storage-config.template.yaml config/storage-config.yaml`
- Don't forget to edit the placeholders
- Validate with your values

---

## Next Steps

- View examples: `config/examples/`
- See templates: `config/templates/`
- Read quick start: `docs/QUICK_START.md`
- Check API: `docs/API_REFERENCE.md`

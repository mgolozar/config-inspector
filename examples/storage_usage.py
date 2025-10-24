#!/usr/bin/env python3
"""
Storage Backend Usage Examples

This file demonstrates various ways to use the storage backend system.
Run this with: python examples/storage_usage.py
"""

import yaml
import logging
from pathlib import Path

from config_validator.storage import (
    load_storage_strategy,
    StorageStrategyFactory,
)


# Setup logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def example_1_local_storage():
    """Example 1: Using local file system storage"""
    print("\n" + "="*60)
    print("Example 1: Local File System Storage")
    print("="*60)
    
    # Create storage strategy for local file system
    strategy = StorageStrategyFactory.create("local", {
        "base_path": "./examples/storage"
    })
    
    # Create a test file
    test_file = Path("./examples/test_file.txt")
    test_file.write_text("Hello, Storage Backend!")
    print(f"Created test file: {test_file}")
    
    # Upload to storage
    uploaded = strategy.upload(test_file, "documents/greeting.txt")
    print(f"Upload result: {uploaded}")
    
    # Check if file exists
    exists = strategy.exists("documents/greeting.txt")
    print(f"File exists: {exists}")
    
    # List files
    files = strategy.list_files()
    print(f"Files in storage: {files}")
    
    # Download from storage
    download_path = Path("./examples/downloaded_file.txt")
    downloaded = strategy.download("documents/greeting.txt", download_path)
    print(f"Download result: {downloaded}")
    if downloaded:
        print(f"Content: {download_path.read_text()}")
    
    # Cleanup
    strategy.delete("documents/greeting.txt")
    print("Cleaned up test files")


def example_2_configuration_file():
    """Example 2: Loading configuration from file"""
    print("\n" + "="*60)
    print("Example 2: Loading from Configuration File")
    print("="*60)
    
    # Create example config file
    config_path = Path("./examples/storage-config.yaml")
    config_content = """
storage:
  type: local
  config:
    base_path: ./examples/config_storage
"""
    config_path.write_text(config_content)
    print(f"Created config file: {config_path}")
    
    # Load configuration
    with open(config_path) as f:
        config = yaml.safe_load(f)
    print(f"Loaded config: {config}")
    
    # Create strategy from configuration
    strategy = load_storage_strategy(config["storage"])
    print(f"Strategy created: {strategy.__class__.__name__}")
    
    # Cleanup
    config_path.unlink()
    print("Cleaned up config file")


def example_3_multiple_backends():
    """Example 3: Switching between different backends"""
    print("\n" + "="*60)
    print("Example 3: Multiple Backends (Showing Flexibility)")
    print("="*60)
    
    backends_to_try = ["local", "s3", "hdfs"]
    
    for backend in backends_to_try:
        print(f"\n--- Backend: {backend} ---")
        try:
            if backend == "local":
                config = {"base_path": "./examples/multi_storage"}
            elif backend == "s3":
                config = {
                    "bucket_name": "example-bucket",
                    "region": "us-east-1"
                }
            else:  # hdfs
                config = {"host": "namenode.example.com"}
            
            strategy = StorageStrategyFactory.create(backend, config)
            print(f"✓ {backend.upper()} strategy created successfully")
            print(f"  Type: {type(strategy).__name__}")
        except Exception as e:
            print(f"✗ Error (expected if dependencies not installed): {e}")


def example_4_factory_registration():
    """Example 4: Extending the system with custom strategies"""
    print("\n" + "="*60)
    print("Example 4: Custom Strategy Registration")
    print("="*60)
    
    from config_validator.storage import (
        StorageStrategy,
        StorageStrategyFactory,
    )
    
    class DemoStrategy(StorageStrategy):
        """A demo storage strategy for demonstration"""
        
        def __init__(self, config):
            super().__init__(config)
            self.name = config.get("name", "Demo Storage")
        
        def upload(self, local_path, remote_path):
            print(f"[DEMO] Would upload {local_path} to {remote_path}")
            return True
        
        def download(self, remote_path, local_path):
            print(f"[DEMO] Would download {remote_path} to {local_path}")
            return True
        
        def exists(self, remote_path):
            print(f"[DEMO] Would check if {remote_path} exists")
            return True
        
        def delete(self, remote_path):
            print(f"[DEMO] Would delete {remote_path}")
            return True
        
        def list_files(self, prefix=""):
            print(f"[DEMO] Would list files with prefix: {prefix}")
            return ["file1.txt", "file2.txt"]
        
        def validate_config(self):
            return True
    
    # Register the custom strategy
    StorageStrategyFactory.register("demo", DemoStrategy)
    print("✓ Custom 'demo' strategy registered")
    
    # Use the custom strategy
    strategy = StorageStrategyFactory.create("demo", {"name": "My Demo"})
    print(f"✓ Custom strategy created: {strategy.name}")
    
    # Try some operations
    strategy.upload(Path("test.txt"), "remote/test.txt")
    print(f"Available strategies: {StorageStrategyFactory.get_available_strategies()}")


def example_5_error_handling():
    """Example 5: Error handling and validation"""
    print("\n" + "="*60)
    print("Example 5: Error Handling & Validation")
    print("="*60)
    
    # Try invalid strategy
    try:
        strategy = StorageStrategyFactory.create("invalid", {})
    except ValueError as e:
        print(f"✓ Caught expected error: {e}")
    
    # Try missing required config
    try:
        strategy = StorageStrategyFactory.create("local", {})
    except ValueError as e:
        print(f"✓ Caught expected error: {e}")
    
    # Try invalid config format
    try:
        from config_validator.storage import load_storage_strategy
        load_storage_strategy({"config": "not a dict"})
    except ValueError as e:
        print(f"✓ Caught expected error: {e}")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("Storage Backend System - Usage Examples")
    print("="*60)
    
    try:
        example_1_local_storage()
        example_2_configuration_file()
        example_3_multiple_backends()
        example_4_factory_registration()
        example_5_error_handling()
        
        print("\n" + "="*60)
        print("✓ All examples completed successfully!")
        print("="*60 + "\n")
        
    except Exception as e:
        logger.error(f"Error running examples: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

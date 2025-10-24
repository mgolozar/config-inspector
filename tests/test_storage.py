"""Integration tests for storage backend strategies."""

import pytest
import tempfile
from pathlib import Path

from config_validator.storage import (
    StorageStrategyFactory,
    load_storage_strategy,
    StorageStrategy,
    LocalStrategy,
)


class TestStorageStrategyFactory:
    """Tests for StorageStrategyFactory."""
    
    def test_create_local_strategy(self, tmp_path):
        """Test creating a local storage strategy."""
        config = {"base_path": str(tmp_path)}
        strategy = StorageStrategyFactory.create("local", config)
        assert isinstance(strategy, LocalStrategy)
        assert strategy.base_path == tmp_path
    
    def test_create_strategy_case_insensitive(self, tmp_path):
        """Test that strategy type is case insensitive."""
        config = {"base_path": str(tmp_path)}
        strategy = StorageStrategyFactory.create("LOCAL", config)
        assert isinstance(strategy, LocalStrategy)
    
    def test_create_unknown_strategy_raises_error(self):
        """Test that unknown strategy type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown storage strategy"):
            StorageStrategyFactory.create("unknown", {})
    
    def test_get_available_strategies(self):
        """Test getting list of available strategies."""
        strategies = StorageStrategyFactory.get_available_strategies()
        assert "local" in strategies
        assert "s3" in strategies
        assert "hdfs" in strategies
        assert len(strategies) >= 3
    
    def test_register_custom_strategy(self, tmp_path):
        """Test registering a custom strategy."""
        class MockStrategy(StorageStrategy):
            def upload(self, local_path, remote_path):
                return True
            def download(self, remote_path, local_path):
                return True
            def exists(self, remote_path):
                return True
            def delete(self, remote_path):
                return True
            def list_files(self, prefix=""):
                return []
            def validate_config(self):
                return True
        
        StorageStrategyFactory.register("mock", MockStrategy)
        strategies = StorageStrategyFactory.get_available_strategies()
        assert "mock" in strategies
        
        strategy = StorageStrategyFactory.create("mock", {})
        assert isinstance(strategy, MockStrategy)


class TestLoadStorageStrategy:
    """Tests for load_storage_strategy function."""
    
    def test_load_local_strategy_from_config(self, tmp_path):
        """Test loading local strategy from config dict."""
        config = {
            "type": "local",
            "config": {
                "base_path": str(tmp_path)
            }
        }
        strategy = load_storage_strategy(config)
        assert isinstance(strategy, LocalStrategy)
    
    def test_load_strategy_with_empty_config(self, tmp_path):
        """Test loading strategy with empty backend config."""
        config = {
            "type": "local",
            "config": {}  # Empty, should use defaults
        }
        # This should raise an error because base_path is required
        with pytest.raises(ValueError):
            load_storage_strategy(config)
    
    def test_load_strategy_missing_type(self):
        """Test loading without type raises error."""
        config = {"config": {}}
        with pytest.raises(ValueError, match="'type' key"):
            load_storage_strategy(config)
    
    def test_load_strategy_invalid_config_dict(self):
        """Test loading with invalid config dict raises error."""
        config = {"type": "local", "config": "not-a-dict"}
        with pytest.raises(ValueError, match="must be a dictionary"):
            load_storage_strategy(config)


class TestLocalStrategy:
    """Tests for LocalStrategy implementation."""
    
    def test_upload_file(self, tmp_path):
        """Test uploading a file."""
        storage_path = tmp_path / "storage"
        config = {"base_path": str(storage_path)}
        strategy = LocalStrategy(config)
        
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        # Upload
        assert strategy.upload(test_file, "remote/test.txt")
        
        # Verify
        uploaded = storage_path / "remote" / "test.txt"
        assert uploaded.exists()
        assert uploaded.read_text() == "test content"
    
    def test_upload_nonexistent_file_returns_false(self, tmp_path):
        """Test uploading nonexistent file returns False."""
        config = {"base_path": str(tmp_path)}
        strategy = LocalStrategy(config)
        
        result = strategy.upload(Path("nonexistent.txt"), "remote/test.txt")
        assert result is False
    
    def test_download_file(self, tmp_path):
        """Test downloading a file."""
        storage_path = tmp_path / "storage"
        config = {"base_path": str(storage_path)}
        strategy = LocalStrategy(config)
        
        # Create a remote file
        remote_file = storage_path / "remote" / "test.txt"
        remote_file.parent.mkdir(parents=True)
        remote_file.write_text("remote content")
        
        # Download
        download_path = tmp_path / "downloaded.txt"
        assert strategy.download("remote/test.txt", download_path)
        
        # Verify
        assert download_path.exists()
        assert download_path.read_text() == "remote content"
    
    def test_exists_file(self, tmp_path):
        """Test checking if file exists."""
        storage_path = tmp_path / "storage"
        config = {"base_path": str(storage_path)}
        strategy = LocalStrategy(config)
        
        # Create a file
        test_file = storage_path / "test.txt"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("content")
        
        # Check exists
        assert strategy.exists("test.txt") is True
        assert strategy.exists("nonexistent.txt") is False
    
    def test_delete_file(self, tmp_path):
        """Test deleting a file."""
        storage_path = tmp_path / "storage"
        config = {"base_path": str(storage_path)}
        strategy = LocalStrategy(config)
        
        # Create a file
        test_file = storage_path / "test.txt"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("content")
        
        # Delete
        assert strategy.delete("test.txt") is True
        assert not test_file.exists()
        
        # Delete nonexistent returns False
        assert strategy.delete("nonexistent.txt") is False
    
    def test_list_files(self, tmp_path):
        """Test listing files."""
        storage_path = tmp_path / "storage"
        config = {"base_path": str(storage_path)}
        strategy = LocalStrategy(config)
        
        # Create some files
        storage_path.mkdir(parents=True)
        (storage_path / "file1.txt").write_text("1")
        (storage_path / "file2.txt").write_text("2")
        (storage_path / "subdir").mkdir()
        (storage_path / "subdir" / "file3.txt").write_text("3")
        
        # List files
        files = strategy.list_files()
        assert len(files) == 3
        assert "file1.txt" in files
        assert "file2.txt" in files
        assert str(Path("subdir") / "file3.txt") in files
    
    def test_list_files_with_prefix(self, tmp_path):
        """Test listing files with prefix."""
        storage_path = tmp_path / "storage"
        config = {"base_path": str(storage_path)}
        strategy = LocalStrategy(config)
        
        # Create files in subdirectory
        storage_path.mkdir(parents=True)
        subdir = storage_path / "configs"
        subdir.mkdir()
        (subdir / "config1.yaml").write_text("1")
        (subdir / "config2.yaml").write_text("2")
        
        # List with prefix
        files = strategy.list_files("configs")
        assert len(files) == 2
    
    def test_validate_config_missing_base_path(self):
        """Test validation fails without base_path."""
        with pytest.raises(ValueError, match="'base_path'"):
            LocalStrategy({})
    
    def test_validate_config_with_base_path(self, tmp_path):
        """Test validation succeeds with base_path."""
        config = {"base_path": str(tmp_path)}
        assert LocalStrategy.validate_config(config) is True


@pytest.fixture
def temp_storage():
    """Fixture providing a temporary storage directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

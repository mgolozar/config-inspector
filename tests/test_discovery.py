from __future__ import annotations

from pathlib import Path

from config_validator.core.discovery import Discovery
from config_validator.storage.local_strategy import LocalStrategy


def test_discovery_with_local_storage(tmp_path: Path) -> None:
    """Test discovery finds YAML files using local storage strategy."""
    # Create test directory structure with YAML files
    test_files = [
        "service1.yaml",
        "service2.yml", 
        "nested/service3.yaml",
        "deep/nested/service4.yml",
        "config.json",  # Non-YAML file
        "readme.txt",   # Non-YAML file
    ]
    
    for file_path in test_files:
        full_path = tmp_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text("test: data", encoding="utf-8")
    
    # Create storage strategy
    storage = LocalStrategy({"base_path": str(tmp_path)})
    discovery = Discovery(tmp_path, storage)
    
    # Discover YAML files
    yaml_files = discovery.discover_yaml_files(tmp_path)
    
    # Verify results
    assert len(yaml_files) == 4
    yaml_paths = {str(p).replace("\\", "/") for p in yaml_files}
    expected_paths = {
        "service1.yaml",
        "service2.yml", 
        "nested/service3.yaml",
        "deep/nested/service4.yml"
    }
    assert yaml_paths == expected_paths

def test_discovery_with_no_yaml_files(tmp_path: Path) -> None:
    """Test discovery with directory containing only non-YAML files."""
    # Create non-YAML files
    non_yaml_files = ["config.json", "readme.txt", "data.csv", "script.py"]
    for file_path in non_yaml_files:
        (tmp_path / file_path).write_text("some content", encoding="utf-8")
    
    storage = LocalStrategy({"base_path": str(tmp_path)})
    discovery = Discovery(tmp_path, storage)
    
    yaml_files = discovery.discover_yaml_files(tmp_path)
    assert yaml_files == []

def test_discovery_with_nested_directories(tmp_path: Path) -> None:
    """Test discovery recursively finds YAML files in nested directories."""
    # Create nested structure
    nested_structure = [
        "root.yaml",
        "level1/service1.yaml",
        "level1/level2/service2.yml",
        "level1/level2/level3/service3.yaml",
        "other/service4.yml",
    ]
    
    for file_path in nested_structure:
        full_path = tmp_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text("test: data", encoding="utf-8")
    
    storage = LocalStrategy({"base_path": str(tmp_path)})
    discovery = Discovery(tmp_path, storage)
    
    yaml_files = discovery.discover_yaml_files(tmp_path)
    
    assert len(yaml_files) == 5
    yaml_paths = {str(p).replace("\\", "/") for p in yaml_files}
    expected_paths = {
        "root.yaml",
        "level1/service1.yaml",
        "level1/level2/service2.yml",
        "level1/level2/level3/service3.yaml",
        "other/service4.yml"
    }
    assert yaml_paths == expected_paths
 
def test_discovery_with_large_directory_structure(tmp_path: Path) -> None:
    """Test discovery performance with many files and directories."""
    # Create a large directory structure
    for i in range(10):
        for j in range(5):
            dir_path = tmp_path / f"level{i}" / f"sublevel{j}"
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # Create YAML files
            (dir_path / f"service_{i}_{j}.yaml").write_text("test: data", encoding="utf-8")
            (dir_path / f"config_{i}_{j}.yml").write_text("test: data", encoding="utf-8")
            
            # Create non-YAML files
            (dir_path / f"readme_{i}_{j}.txt").write_text("readme", encoding="utf-8")
    
    storage = LocalStrategy({"base_path": str(tmp_path)})
    discovery = Discovery(tmp_path, storage)
    
    yaml_files = discovery.discover_yaml_files(tmp_path)
    
    # Should find all YAML files (10 * 5 * 2 = 100 files)
    assert len(yaml_files) == 100
    
    # Verify all files are YAML files
    for file_path in yaml_files:
        assert file_path.suffix.lower() in {'.yml', '.yaml'}

# from os import name
# from pathlib import Path
# from config_validator.discovery import discover_configs

# def touch(p: Path, content="x"):
#     p.parent.mkdir(parents=True, exist_ok=True)
#     p.write_text(content)



# def test_returns_only_yaml_and_sorted(tmp_path: Path):
#     # Arrange
#     root = tmp_path / "test_fixtures"
#     touch(root / "a.yaml", "test")
#     touch(root / "b.yml", "test")
#     touch(root / "c.txt", "test")               
#     touch(root / "sub" / "d.yaml", "test")
#     # Act
#     result = discover_configs(root)             
#     # Assert
#     names = [p.name for p in result]
#     assert names == ["a.yaml", "b.yml", "d.yaml"]
#     assert result == sorted(result)



# def test_ignores_hidden_dirs_and_files(tmp_path: Path):
#     # Arrange
#     root = tmp_path / "test_fixtures"
#     root.mkdir(parents=True, exist_ok=True)
#     (root / ".git").mkdir(parents=True, exist_ok=True)
#     touch(root / ".git" / "ignored.yaml", "x")
#     touch(root / ".secret.yaml", "x")
#     touch(root / "visible.yaml", "ok")
#     # Act
#     result = discover_configs(root)
#     # Assert: 
#     names = [p.name for p in result]
#     assert names== ["visible.yaml"]

# def test_case_insensitive_suffix(tmp_path: Path):

#     root = tmp_path / "test_fixtures"
#     touch(root / "sensitive" / "upper.YAML", "x")
#     touch(root / "sensitive" / "upper.YML", "x")
#     touch(root / "sensitive" / "nope.Ya", "bad")
    

#     result = discover_configs(tmp_path)

#     names = [p.name for p in result]
#     assert names== ["upper.YAML", "upper.YML"]

# def test_empty_when_no_yaml(tmp_path: Path):

#     root = tmp_path / "test_fixtures"
#     touch(root / "empty" / "a.txt", "x")
#     touch(root / "empty" / "b.json", "{}")
    
#     result = discover_configs(tmp_path)

#     assert result == []




# def test_deep_nested_and_sorted(tmp_path: Path):

#     root = tmp_path / "test_fixtures"
#     root.mkdir(parents=True)
#     touch(root / "nested" / "x" / "y" / "z"/ "one.yaml", "1")
#     touch(root / "nested"/ "x" / "y" / "a.yml", "2")

#     result = discover_configs(tmp_path)
#     names = [p.name for p in result]
#     assert names== ["a.yml", "one.yaml"]   
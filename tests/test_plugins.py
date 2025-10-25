

from __future__ import annotations

from pathlib import Path
from config_validator.core.sync_validator import SyncValidator
from config_validator.core.config import ValidationConfig
from config_validator.storage.local_strategy import LocalStrategy
from config_validator.rules.check_env import EnvValueNotEmpty


def test_plugin_env_value_not_empty(tmp_path: Path) -> None:
    """Test that the EnvValueNotEmpty plugin correctly identifies empty env values."""
    f = tmp_path / "svc.yaml"
    f.write_text(
        """
        service: user-api
        replicas: 2
        image: myregistry.com/user-api:1.0.0
        env:
            DATABASE_URL: ""
            REDIS_URL: redis://cache:6379
        """,
        encoding="utf-8",
        )

    # Create test configuration and storage strategy
    config = ValidationConfig()
    storage = LocalStrategy({"base_path": str(tmp_path)})
    validator = SyncValidator(config, storage)

    res = validator.validate_file(str(f))
    assert res.valid is False
    # plugin should flag DATABASE_URL as empty
    assert any("env values must be non-empty strings" in e for e in res.errors)


def test_plugin_env_value_valid(tmp_path: Path) -> None:
    """Test that the EnvValueNotEmpty plugin passes valid env values."""
    f = tmp_path / "svc.yaml"
    f.write_text(
        """
        service: user-api
        replicas: 2
        image: myregistry.com/user-api:1.0.0
        env:
            DATABASE_URL: "postgres://db:5432/x"
            REDIS_URL: "redis://cache:6379"
        """,
        encoding="utf-8",
        )

    # Create test configuration and storage strategy
    config = ValidationConfig()
    storage = LocalStrategy({"base_path": str(tmp_path)})
    validator = SyncValidator(config, storage)

    res = validator.validate_file(str(f))
    # Should be valid since all env values are non-empty
    assert res.valid is True
    assert not any("env values must be non-empty strings" in e for e in res.errors)



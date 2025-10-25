from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class ValidationRule:
    """Represents a single validation rule."""

    field: str
    rule_type: str  # 'range', 'regex', 'required', 'enum', etc.
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    pattern: Optional[str] = None
    allowed_values: Optional[List[str]] = None
    error_message: Optional[str] = None


@dataclass
class ValidationConfig:
    """Configuration for validation rules and settings."""

    replicas_min: int = 1
    replicas_max: int = 50
    image_pattern: str = r"^(?P<registry>[\w.-]+(?::\d+)?)/(?P<service>[\w.-]+):(?P<version>[\w.-]+)$"
    required_fields: List[str] = None
    env_key_case: str = "UPPERCASE"   
    custom_rules: List[ValidationRule] = None

    def __post_init__(self) -> None:
        """Initialize default values after dataclass creation."""
        if self.required_fields is None:
            self.required_fields = ["service", "image", "replicas"]
        if self.custom_rules is None:
            self.custom_rules = []


def load_validation_config(config_path: Optional[Path] = None) -> ValidationConfig:
    """Load validation configuration from YAML file or return defaults."""
    if config_path and config_path.exists():
        with config_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        
        return ValidationConfig(
            replicas_min=data.get("replicas_min", 1),
            replicas_max=data.get("replicas_max", 50),
            image_pattern=data.get("image_pattern", r"^(?P<registry>[\w.-]+(?::\d+)?)/(?P<service>[\w.-]+):(?P<version>[\w.-]+)$"),
            required_fields=data.get("required_fields", ["service", "image", "replicas"]),
            env_key_case=data.get("env_key_case", "UPPERCASE"),
            custom_rules=[
                ValidationRule(**rule) for rule in data.get("custom_rules", [])
            ]
        )
    
    return ValidationConfig()


def save_validation_config(config: ValidationConfig, config_path: Path) -> None:
    """Save validation configuration to YAML file."""
    data = {
        "replicas_min": config.replicas_min,
        "replicas_max": config.replicas_max,
        "image_pattern": config.image_pattern,
        "required_fields": config.required_fields,
        "env_key_case": config.env_key_case,
        "custom_rules": [
            {
                "field": rule.field,
                "rule_type": rule.rule_type,
                "min_value": rule.min_value,
                "max_value": rule.max_value,
                "pattern": rule.pattern,
                "allowed_values": rule.allowed_values,
                "error_message": rule.error_message,
            }
            for rule in config.custom_rules
        ]
    }
    
    with config_path.open("w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, indent=2)

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from ..rules.base_rule import ValidationRule
from ..storage.base_strategy import StorageStrategy
from .config import ValidationConfig
from .rules_loader import load_rules

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ValidationResult:
    """Result of validating a single file."""
    path: str
    valid: bool
    errors: List[str]
    registry: str | None
    data: Dict[str, Any] | None


class BaseValidator(ABC):
    """Abstract base class for all validators."""
    
    def __init__(self, config: ValidationConfig, storage: StorageStrategy) -> None:
        """Initialize validator with config and storage strategy."""
        self.config = config
        self.storage = storage
        self._rules: List[ValidationRule] | None = None
    
    @property
    def rules(self) -> List[ValidationRule]:
        """Lazy load rules when first accessed."""
        if self._rules is None:
            self._rules = load_rules(self.config)
        return self._rules
    
    def _read_and_parse_file(self, file_path: str) -> tuple[Dict[str, Any] | None, List[str]]:
        """Read and parse a YAML file, returning data and any errors."""
        errors: List[str] = []
        
        try:
            # Read file content
            content = self.storage.read_file(file_path)
            logger.debug(f"Successfully read file: {file_path}")
        except Exception as e:
            error_msg = f"Failed to read file {file_path}: {e}"
            logger.error(error_msg, exc_info=True)
            return None, [error_msg]
        
        try:
            # Parse YAML
            import yaml
            data = yaml.safe_load(content) or {}
            logger.debug(f"Successfully parsed YAML from file: {file_path}")
        except yaml.YAMLError as e:
            error_msg = f"YAML parse error in {file_path}: {e}"
            logger.error(error_msg, exc_info=True)
            return None, [error_msg]
        except Exception as e:
            error_msg = f"Error parsing YAML from {file_path}: {e}"
            logger.error(error_msg, exc_info=True)
            return None, [error_msg]
        
        # Handle list data structures
        try:
            if isinstance(data, list):
                logger.debug(f"File contains list data, converting to dict")
                d = {}
                for x in data:
                    if isinstance(x, dict):
                        d.update(x)
                data = d
                logger.debug(f"Successfully converted list to dict")
        except Exception as e:
            error_msg = f"Error processing list data from {file_path}: {e}"
            logger.error(error_msg, exc_info=True)
            errors.append(error_msg)
        
        return data, errors
    
    def _extract_registry(self, data: Dict[str, Any]) -> str | None:
        """Extract registry from image field in data."""
        try:
            img = data.get("image")
            if isinstance(img, str):
                import re
                image_re = re.compile(self.config.image_pattern)
                m = image_re.match(img)
                if m:
                    registry = m.group("registry")
                    logger.debug(f"Extracted registry: {registry}")
                    return registry
        except Exception as e:
            error_msg = f"Error extracting registry: {e}"
            logger.warning(error_msg, exc_info=True)
            
        return None
    
    def _run_validation_rules(self, data: Dict[str, Any], file_path: str) -> List[str]:
        """Run all validation rules on the data."""
        errors: List[str] = []
        
        try:
            for rule in self.rules:
                try:
                    rule_errors = rule.validate(data)
                    if rule_errors:
                        logger.debug(f"Rule {rule.__class__.__name__} found {len(rule_errors)} error(s)")
                        errors.extend(rule_errors)
                except Exception as rule_exc:
                    error_msg = f"Rule {rule.__class__.__name__} error: {rule_exc}"
                    logger.exception(error_msg)
                    errors.append(error_msg)
        except Exception as e:
            error_msg = f"Error loading or running rules for {file_path}: {e}"
            logger.error(error_msg, exc_info=True)
            errors.append(error_msg)
        
        return errors
    
    @abstractmethod
    def validate_file(self, file_path: str) -> ValidationResult:
        """Validate a single file and return the result."""
        pass
    
    @abstractmethod
    def validate_files(self, file_paths: List[str]) -> List[ValidationResult]:
        """Validate multiple files and return results."""
        pass

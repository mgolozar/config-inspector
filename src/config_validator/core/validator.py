from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import yaml
from yaml import CSafeLoader as SafeLoader

from ..rules.base_rule import ValidationRule
from ..storage.base_strategy import StorageStrategy
from .config import ValidationConfig, load_validation_config
from .rules_loader import load_rules

logger = logging.getLogger(__name__)


class ValidationSession:
    """Validation session for processing YAML files with rules."""

    def __init__(self, config: ValidationConfig, storage: StorageStrategy) -> None:
        """Initialize validation session with config and storage strategy."""
        self.config = config
        self.storage = storage



    def validate_file(self, file_path: str) -> Dict[str, Any]:
       
        logger.debug(f"Starting validation for file: {file_path}")
        
        try:
            # Read file content
            try:
                content = self.storage.read_file(file_path)
                logger.debug(f"Successfully read file: {file_path}")
            except Exception as e:
                error_msg = f"Failed to read file {file_path}: {e}"
                logger.error(error_msg, exc_info=True)
                return {
                    "path": file_path,
                    "valid": False,
                    "errors": [error_msg],
                    "registry": None,
                    "data": None
                }
            
            # Parse YAML
            try:
                data = yaml.safe_load(content) or {}
                logger.debug(f"Successfully parsed YAML from file: {file_path}")
            except yaml.YAMLError as e:
                error_msg = f"YAML parse error in {file_path}: {e}"
                logger.error(error_msg, exc_info=True)
                return {
                    "path": file_path,
                    "valid": False,
                    "errors": [error_msg],
                    "registry": None,
                    "data": None
                }
            except Exception as e:
                error_msg = f"Error parsing YAML from {file_path}: {e}"
                logger.error(error_msg, exc_info=True)
                return {
                    "path": file_path,
                    "valid": False,
                    "errors": [error_msg],
                    "registry": None,
                    "data": None
                }
            
            errors: list[str] = []
            registry: str | None = None

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
            
            # Run rules (including core validation)
            try:
                if isinstance(data, dict):
                    rules = load_rules(self.config)
                    logger.debug(f"Loaded {len(rules)} rules")
                    
                    for rule in rules:
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

            # Extract registry
            try:
                img = data.get("image") if isinstance(data, dict) else None
                if isinstance(img, str):
                    image_re = re.compile(self.config.image_pattern)
                    m = image_re.match(img)
                    if m:
                        registry = m.group("registry")
                        logger.debug(f"Extracted registry: {registry}")
            except Exception as e:
                error_msg = f"Error extracting registry from {file_path}: {e}"
                logger.warning(error_msg, exc_info=True)
                # Don't add to errors - registry extraction is not critical

            
            valid = len(errors) == 0
            result: Dict[str, Any] = {
                "path": str(file_path),
                "valid": valid,
                "errors": errors,
                "registry": registry,
                "data": data,
            }
            
            if valid:
                logger.info(f"File {file_path} validation PASSED")
            else:
                logger.warning(f"File {file_path} validation FAILED with {len(errors)} error(s)")
            
            return result

        except Exception as exc:
            error_msg = f"Unexpected error validating {file_path}: {exc}"
            logger.critical(error_msg, exc_info=True)
            return {
                "path": file_path,
                "valid": False,
                "errors": [error_msg],
                "registry": None,
                "data": None
            }

    



@dataclass(slots=True)
class FileResult:
    path: str
    valid: bool
    errors: list[str]
    registry: str | None
    data: dict[str, Any] | None


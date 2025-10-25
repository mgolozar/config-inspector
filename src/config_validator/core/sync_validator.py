from __future__ import annotations

import logging
from typing import List

from .base_validator import BaseValidator, ValidationResult

logger = logging.getLogger(__name__)


class SyncValidator(BaseValidator):
    """Synchronous validator for processing YAML files with rules."""

    def validate_file(self, file_path: str) -> ValidationResult:
        """Validate a single file synchronously."""
        logger.debug(f"Starting validation for file: {file_path}")
        
        try:
           
            data, errors = self._read_and_parse_file(file_path)
            if data is None:
                return ValidationResult(
                    path=file_path,
                    valid=False,
                    errors=errors,
                    registry=None,
                    data=None
                )
            
           
            if isinstance(data, dict):
                rule_errors = self._run_validation_rules(data, file_path)
                errors.extend(rule_errors)
            
            
            registry = self._extract_registry(data) if isinstance(data, dict) else None
            
             
            valid = len(errors) == 0
            
            result = ValidationResult(
                path=file_path,
                valid=valid,
                errors=errors,
                registry=registry,
                data=data
            )
            
            if valid:
                logger.info(f"File {file_path} validation PASSED")
            else:
                logger.warning(f"File {file_path} validation FAILED with {len(errors)} error(s)")
            
            return result
            
        except Exception as exc:
            error_msg = f"Unexpected error validating {file_path}: {exc}"
            logger.critical(error_msg, exc_info=True)
            return ValidationResult(
                path=file_path,
                valid=False,
                errors=[error_msg],
                registry=None,
                data=None
            )
    
    def validate_files(self, file_paths: List[str]) -> List[ValidationResult]:
        """Validate multiple files synchronously."""
        results = []
        for file_path in file_paths:
            result = self.validate_file(file_path)
            results.append(result)
        return results

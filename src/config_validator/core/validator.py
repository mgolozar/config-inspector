from __future__ import annotations


import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


import yaml
from yaml import CSafeLoader as SafeLoader


from ..plugins.base_plugin import ValidationPlugin
from .plugins_loader import load_plugins
from .config import ValidationConfig, load_validation_config

from ..storage.base_strategy import StorageStrategy


logger = logging.getLogger(__name__)
class ValidationSession:
    def __init__(self, config: ValidationConfig, storage: StorageStrategy):
        self.config = config
        self.storage = storage


    @staticmethod
    def _validate_core(data: dict[str, Any], config: ValidationConfig) -> list[str]:
 
        errors: list[str] = []

        try:
            logger.debug(f"Starting core validation. Data type: {type(data)}")
            
            # Check if data is actually a dictionary
            if not isinstance(data, dict):
                error_msg = f"Configuration must be a dictionary, got {type(data).__name__}"
                logger.warning(error_msg)
                errors.append(error_msg)
                return errors

            # Check required fields
            try:
                missing = set(config.required_fields) - data.keys()
                if missing:
                    error_msg = f"Missing required keys: {sorted(missing)}"
                    logger.warning(error_msg)
                    errors.append(error_msg)
            except Exception as e:
                error_msg = f"Error checking required fields: {e}"
                logger.error(error_msg, exc_info=True)
                errors.append(error_msg)

            # Replicas validation with configurable range
            try:
                rep = data.get("replicas")
                if not isinstance(rep, int) or not (config.replicas_min <= rep <= config.replicas_max):
                    error_msg = f"replicas must be an integer between {config.replicas_min} and {config.replicas_max}"
                    logger.warning(error_msg)
                    errors.append(error_msg)
                else:
                    logger.debug(f"Replicas validation passed: {rep}")
            except Exception as e:
                error_msg = f"Error validating replicas: {e}"
                logger.error(error_msg, exc_info=True)
                errors.append(error_msg)

            # Image validation with configurable pattern
            try:
                img = data.get("image")
                if not isinstance(img, str):
                    error_msg = "image must be a string like registry/service:version"
                    logger.warning(error_msg)
                    errors.append(error_msg)
                else:
                    image_re = re.compile(config.image_pattern)
                    if not image_re.match(img):
                        error_msg = "image must match <registry>/<service>:<version>"
                        logger.warning(error_msg)
                        errors.append(error_msg)
                    else:
                        logger.debug(f"Image validation passed: {img}")
            except Exception as e:
                error_msg = f"Error validating image: {e}"
                logger.error(error_msg, exc_info=True)
                errors.append(error_msg)

            # Environment variables validation with configurable case requirements
            try:
                env = data.get("env", {})
                if env and isinstance(env, dict):
                    if config.env_key_case == "UPPERCASE":
                        non_upper = [k for k in env.keys() if not (isinstance(k, str) and k.isupper())]
                        if non_upper:
                            error_msg = f"env keys must be UPPERCASE: {sorted(non_upper)}"
                            logger.warning(error_msg)
                            errors.append(error_msg)
                        else:
                            logger.debug("Environment variables case validation passed (UPPERCASE)")
                    elif config.env_key_case == "lowercase":
                        non_lower = [k for k in env.keys() if not (isinstance(k, str) and k.islower())]
                        if non_lower:
                            error_msg = f"env keys must be lowercase: {sorted(non_lower)}"
                            logger.warning(error_msg)
                            errors.append(error_msg)
                        else:
                            logger.debug("Environment variables case validation passed (lowercase)")
                elif env not in (None, {}):
                    error_msg = "env must be a mapping of key->value"
                    logger.warning(error_msg)
                    errors.append(error_msg)
            except Exception as e:
                error_msg = f"Error validating environment variables: {e}"
                logger.error(error_msg, exc_info=True)
                errors.append(error_msg)

            logger.info(f"Core validation completed with {len(errors)} error(s)")
            return errors
            
        except Exception as e:
            error_msg = f"Unexpected error during core validation: {e}"
            logger.critical(error_msg, exc_info=True)
            return [error_msg]

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
            
            # Validate core rules
            try:
                if isinstance(data, dict):
                    core_errors = self._validate_core(data, self.config)
                    errors.extend(core_errors)
                    if core_errors:
                        logger.warning(f"Core validation found {len(core_errors)} error(s) in {file_path}")
            except Exception as e:
                error_msg = f"Error during core validation of {file_path}: {e}"
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

            # Run plugins
            try:
                if isinstance(data, dict):
                    plugins = load_plugins()
                    logger.debug(f"Loaded {len(plugins)} plugins")
                    
                    for plugin in plugins:
                        try:
                            plugin_errors = plugin.validate(data)
                            if plugin_errors:
                                logger.debug(f"Plugin {plugin.__class__.__name__} found {len(plugin_errors)} error(s)")
                                errors.extend(plugin_errors)
                        except Exception as plugin_exc:
                            error_msg = f"Plugin {plugin.__class__.__name__} error: {plugin_exc}"
                            logger.exception(error_msg)
                            errors.append(error_msg)
            except Exception as e:
                error_msg = f"Error loading or running plugins for {file_path}: {e}"
                logger.error(error_msg, exc_info=True)
                errors.append(error_msg)
            
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


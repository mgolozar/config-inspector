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


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class FileResult:
    path: str
    valid: bool
    errors: list[str]
    registry: str | None
    data: dict[str, Any] | None


class Validator:
    """Validator class for YAML configuration files."""
    
    @staticmethod
    def parse_yaml(path) -> dict[str, Any]:
        """Parse YAML file at given path."""
        try:
            with open(path) as f:
                return yaml.load(f, Loader=SafeLoader)
        except Exception as exc:  # broad: we want to capture malformed files as validation errors
            raise ValueError(f"YAML parse error: {exc}")
    
    @staticmethod
    def _load_yaml(path: Path) -> dict[str, Any]:
        """Load YAML file and return as dictionary."""
        try:
            with path.open("r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as exc:  # broad: we want to capture malformed files as validation errors
            raise ValueError(f"YAML parse error: {exc}")
    
    @staticmethod
    def _validate_core(data: dict[str, Any], config: ValidationConfig) -> list[str]:
        """Validate core configuration rules."""
        errors: list[str] = []

        print("data", data)
        print(type(data))
        
        # Check if data is actually a dictionary
        if not isinstance(data, dict):
            errors.append(f"Configuration must be a dictionary, got {type(data).__name__}")
            return errors

        missing = set(config.required_fields) - data.keys()
        if missing:
            errors.append(f"Missing required keys: {sorted(missing)}")


        # replicas validation with configurable range
        rep = data.get("replicas")
        if not isinstance(rep, int) or not (config.replicas_min <= rep <= config.replicas_max):
            errors.append(f"replicas must be an integer between {config.replicas_min} and {config.replicas_max}")


        # image validation with configurable pattern
        img = data.get("image")
        if not isinstance(img, str):
            errors.append("image must be a string like registry/service:version")
        else:
            image_re = re.compile(config.image_pattern)
            if not image_re.match(img):
                errors.append("image must match <registry>/<service>:<version>")


        # env validation with configurable case requirements
        env = data.get("env", {})
        if env and isinstance(env, dict):
            if config.env_key_case == "UPPERCASE":
                non_upper = [k for k in env.keys() if not (isinstance(k, str) and k.isupper())]
                if non_upper:
                    errors.append(f"env keys must be UPPERCASE: {sorted(non_upper)}")
            elif config.env_key_case == "lowercase":
                non_lower = [k for k in env.keys() if not (isinstance(k, str) and k.islower())]
                if non_lower:
                    errors.append(f"env keys must be lowercase: {sorted(non_lower)}")
        elif env not in (None, {}):
            errors.append("env must be a mapping of key->value")


        return errors
    
    @staticmethod
    def validate_file(path: Path, config: ValidationConfig = None) -> Dict[str, Any]:
        """Validate a single file and return a structured result dict.

        This function does not raise; it returns errors in the structure.
        """
        
        
        if config is None:
            config = ValidationConfig()  # Use defaults
        
        errors: list[str] = []
        data: dict[str, Any] | None = None
        registry: str | None = None

        print("validate_file", path)
        try:
            data = Validator._load_yaml(path)
            print("data", data)

            if isinstance(data, list):
                d = {}                  
                for x in data:
                    if isinstance(x, dict):    
                        d.update(x) 
                        data = d
             
            
            # Only validate core rules if data is a dictionary
            if isinstance(data, dict):
                errors.extend(Validator._validate_core(data, config))



            # Extract registry if possible
            img = data.get("image") if isinstance(data, dict) else None
            print("img", img)
            if isinstance(img, str):
                image_re = re.compile(config.image_pattern)
                m = image_re.match(img)
                if m:
                    registry = m.group("registry")

            # Run plugins only if data is a dictionary
            if isinstance(data, dict):
                for plugin in load_plugins():
                    try:
                        print("plugin", plugin)
                        plugin_errors = plugin.validate(data)
                        print("plugin_errors", plugin_errors)
                        if plugin_errors:
                            errors.extend(plugin_errors)
                    except Exception as exc: 
                        print("exc", exc)  # defensive: plugin failures shouldn't crash core
                        logger.exception("Plugin %s failed: %s", plugin.__class__.__name__, exc)
                        errors.append(f"Plugin {plugin.__class__.__name__} error: {exc}")
            
            valid = len(errors) == 0
            result: Dict[str, Any] = {
                "path": str(path),
                "valid": valid,
                "errors": errors,
                "registry": registry,
                "data": data,
            }
            return result

        except Exception as exc:
            errors.append(str(exc))
            valid = len(errors) == 0
            result: Dict[str, Any] = {
                "path": str(path),
                "valid": valid,
                "errors": errors,
                "registry": registry,
                "data": data,
            }
            return result

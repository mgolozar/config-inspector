from __future__ import annotations

import logging
import re
from typing import Any, Dict, List

from .base_rule import ValidationRule

logger = logging.getLogger(__name__)


class CheckCore(ValidationRule):
    """Core validation rule that checks basic configuration requirements."""

    def __init__(self, config: Any = None):
        """Initialize the core validation rule with configuration."""
        self.config = config

    def validate(self, data: dict) -> List[str]:
        """Validate core configuration requirements."""
        errors: list[str] = []

        try:
            logger.debug(f"Starting core validation. Data type: {type(data)}")
            
             
            if not isinstance(data, dict):
                error_msg = f"Configuration must be a dictionary, got {type(data).__name__}"
                logger.warning(error_msg)
                errors.append(error_msg)
                return errors

             
            try:
                missing = set(self.config.required_fields) - data.keys()
                if missing:
                    error_msg = f"Missing required keys: {sorted(missing)}"
                    logger.warning(error_msg)
                    errors.append(error_msg)
            except Exception as e:
                error_msg = f"Error checking required fields: {e}"
                logger.error(error_msg, exc_info=True)
                errors.append(error_msg)

             
            try:
                rep = data.get("replicas")
                if not isinstance(rep, int) or not (self.config.replicas_min <= rep <= self.config.replicas_max):
                    error_msg = f"replicas must be an integer between {self.config.replicas_min} and {self.config.replicas_max}"
                    logger.warning(error_msg)
                    errors.append(error_msg)
                else:
                    logger.debug(f"Replicas validation passed: {rep}")
            except Exception as e:
                error_msg = f"Error validating replicas: {e}"
                logger.error(error_msg, exc_info=True)
                errors.append(error_msg)

             
            try:
                img = data.get("image")
                if not isinstance(img, str):
                    error_msg = "image must be a string like registry/service:version"
                    logger.warning(error_msg)
                    errors.append(error_msg)
                else:
                    image_re = re.compile(self.config.image_pattern)
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

             
            try:
                env = data.get("env", {})
                if env and isinstance(env, dict):
                    if self.config.env_key_case == "UPPERCASE":
                        non_upper = [k for k in env.keys() if not (isinstance(k, str) and k.isupper())]
                        if non_upper:
                            error_msg = f"env keys must be UPPERCASE: {sorted(non_upper)}"
                            logger.warning(error_msg)
                            errors.append(error_msg)
                        else:
                            logger.debug("Environment variables case validation passed (UPPERCASE)")
                    elif self.config.env_key_case == "lowercase":
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

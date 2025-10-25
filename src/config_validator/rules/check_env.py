from __future__ import annotations


from typing import List


from .base_rule import ValidationRule




class EnvValueNotEmpty(ValidationRule):
    """Ensure all env values are non-empty strings."""


    def validate(self, data: dict) -> List[str]:
        errs: list[str] = []
        env = data.get("env")
        if isinstance(env, dict):
            bad = [k for k, v in env.items() if not isinstance(v, str) or v.strip() == ""]
            if bad:
                errs.append(f"env values must be non-empty strings: {sorted(bad)}")
        return errs
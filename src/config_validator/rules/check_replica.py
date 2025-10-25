from __future__ import annotations


from typing import List


from .base_rule import ValidationRule




class ReplicasInRange(ValidationRule):
    """Ensure all replica values is between 1 and 10."""


    def validate(self, data: dict) -> List[str]:
        errs: list[str] = []
        replicas = data.get("replicas")
        if not isinstance(replicas, int) or not (1 <= replicas <= 10):
            errs.append("replicas must be an integer between 1 and 10")

        # if isinstance(env, dict):
        #     bad = [k for k, v in env.items() if not isinstance(v, str) or v.strip() == ""]
        #     if bad:
        #         errs.append(f"env values must be non-empty strings: {sorted(bad)}")
        return errs
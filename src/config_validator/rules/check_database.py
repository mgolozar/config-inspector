from __future__ import annotations


from typing import List


from .base_rule import ValidationRule




class EnvValueNotDatabaseName(ValidationRule):
 

    def validate(self, data: dict) -> List[str]:
        errs: list[str] = []
        env = data.get("env")
        if isinstance(env, dict):
            bad = [k for k, v in env.items() if (k.strip() == "DATABASE_URL" and v.strip() == "test") ]
            if bad:
                errs.append(f"Database name cannot be 'test': {sorted(bad)}")
        return errs
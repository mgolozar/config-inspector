# from __future__ import annotations
# from pathlib import Path
# from typing import List
# from ..validation.core import RulesRegistry


# # Example plugin contributes a simple rule


# def _rule_filename_matches_name(path: Path, data: dict | None) -> List[str]:
#     issues: List[str] = []
#     print(f"path: {path}")
#     print(f"data: {data}")
    
#     if not isinstance(data, dict) or "name" not in data:
#         return issues
#     expected = f"{data['name']}.yaml"
#     if path.name != expected:
#         issues.append(f"Filename should be '{expected}' to match name")
#     return issues




# def register(registry: RulesRegistry) -> None:
#     registry.add(_rule_filename_matches_name)
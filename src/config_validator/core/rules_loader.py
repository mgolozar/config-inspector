from __future__ import annotations


import importlib
import pkgutil
from typing import Iterable, List


from ..rules.base_rule import ValidationRule




_DEF_PKG = "config_validator.rules"




def load_rules(config=None) -> List[ValidationRule]:

    rules: list[ValidationRule] = []
    pkg = importlib.import_module(_DEF_PKG)
    for m in pkgutil.iter_modules(pkg.__path__, prefix=f"{_DEF_PKG}."):
        module = importlib.import_module(m.name)
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            try:
                if isinstance(attr, type) and issubclass(attr, ValidationRule) and attr is not ValidationRule:
                    # Check if the rule accepts config in its constructor
                    try:
                        # Try to instantiate with config first
                        rule_instance = attr(config) if config is not None else attr()
                    except TypeError:
                        # If it doesn't accept config, instantiate without it
                        rule_instance = attr()
                    rules.append(rule_instance)
            except Exception:
            # Non-class attribute or unrelated type
                continue
    print("--------------------------------------------------")        
    print("rules",rules)
    print("--------------------------------------------------")
    return rules
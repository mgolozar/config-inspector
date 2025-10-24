from __future__ import annotations


import importlib
import pkgutil
from typing import Iterable, List


from ..plugins.base_plugin import ValidationPlugin




_DEF_PKG = "config_validator.plugins"




def load_plugins() -> List[ValidationPlugin]:
    """Dynamically discover and instantiate plugins in `config_validator.plugins`.


    - Scans package modules
    - Finds subclasses of ValidationPlugin
    - Instantiates with no-arg constructor
    """
    plugins: list[ValidationPlugin] = []
    pkg = importlib.import_module(_DEF_PKG)
    for m in pkgutil.iter_modules(pkg.__path__, prefix=f"{_DEF_PKG}."):
        module = importlib.import_module(m.name)
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            try:
                if isinstance(attr, type) and issubclass(attr, ValidationPlugin) and attr is not ValidationPlugin:
                    plugins.append(attr())
            except Exception:
            # Non-class attribute or unrelated type
                continue
    print("--------------------------------------------------")        
    print("plugins",plugins)
    print("--------------------------------------------------")
    return plugins
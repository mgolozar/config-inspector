from __future__ import annotations


import time
from pathlib import Path
from typing import Callable, Dict




def _snapshot(root: Path) -> Dict[str, float]:
    """Return {absolute_path: mtime} for .yml/.yaml files."""
    mtimes: dict[str, float] = {}
    for pat in ("**/*.yml", "**/*.yaml"):
        for p in root.glob(pat):
            try:
                mtimes[str(p.resolve())] = p.stat().st_mtime
            except FileNotFoundError:
                continue
    return mtimes




def watch_polling(root: Path, on_change: Callable[[], None], interval: float = 1.0) -> None:
    """Simple portable polling watcher.


    Calls `on_change()` on initial run and whenever any YAML file changes.
    """
    prev = {}
    on_change() # initial
    while True:
        time.sleep(interval)
        cur = _snapshot(root)
        if cur != prev:
            on_change()
        prev = cur
       




 
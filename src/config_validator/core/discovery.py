from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, List

EXCLUDED_DIRS = {'.git', 'node_modules', '.idea', '.venv', '__pycache__'}
EXCLUDED_EXTS = {'.zip', '.tar', '.gz', '.rar'}


def fast_walk(root: Path) -> Iterable[Path]:
    """Yield all files under root (non-recursive stack, no symlinks)."""
    stack = [root]
    while stack:
        d = stack.pop()
        try:
            with os.scandir(d) as it:
                for entry in it:
                    if entry.is_dir(follow_symlinks=False):
                    
                        if entry.name in EXCLUDED_DIRS:
                            continue
                        stack.append(Path(entry.path))
                                        # Files (and only files)
                    elif not entry.is_file(follow_symlinks=False):
                        continue    
                    else:
                    
                        p = Path(entry.path)
                        if p.suffix.lower() in EXCLUDED_EXTS:
                            continue
                        yield p
        except (PermissionError, FileNotFoundError):
       
            continue


def get_yaml_files(root: Path) -> Iterable[Path]:
    """Yield only YAML files discovered by fast_walk."""
    for p in fast_walk(root):
        if p.suffix.lower() in {'.yml', '.yaml'}:
            yield p


 
def discover_yaml_files(root: Path) -> List[Path]:
  
    unique = sorted({p.resolve() for p in get_yaml_files(root)})
    return list(unique)
  
 
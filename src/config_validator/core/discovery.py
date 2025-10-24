from __future__ import annotations

import os
from pathlib import Path
from typing import List
from ..storage.base_strategy import StorageStrategy

class Discovery:

    _storageStrategy: StorageStrategy   
    def __init__(self, root: Path, storageStrategy: StorageStrategy):
        self.root = root
        self._storageStrategy = storageStrategy
 
 
    def discover_yaml_files(self, root: Path) -> List[Path]:
    
        unique = self._storageStrategy.get_yaml_files(root)
        return list(unique)
  
 
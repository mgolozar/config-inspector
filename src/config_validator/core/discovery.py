from __future__ import annotations

from pathlib import Path
from typing import List

from ..storage.base_strategy import StorageStrategy


class Discovery:
    """File discovery service using storage strategy."""

    def __init__(self, root: Path, storage_strategy: StorageStrategy) -> None:
        """Initialize discovery with root path and storage strategy."""
        self.root = root
        self._storage_strategy = storage_strategy

    def discover_yaml_files(self, root: Path) -> List[Path]:
        """Discover all YAML files in the given root directory."""
        unique = self._storage_strategy.get_yaml_files(root)
        return list(unique)
 
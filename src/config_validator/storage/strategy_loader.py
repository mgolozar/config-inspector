"""Storage strategy factory and loader for dynamic runtime strategy selection."""

import logging
from typing import Any, Dict, Optional

from .base_strategy import StorageStrategy
from .local_strategy import LocalStrategy
from .s3_strategy import S3Strategy
from .hdfs_strategy import HDFSStrategy


logger = logging.getLogger(__name__)

# Registry of available storage strategies
STRATEGIES: Dict[str, type] = {
    "local": LocalStrategy,
    "s3": S3Strategy,
    "hdfs": HDFSStrategy,
}


class StorageStrategyFactory:
 
    
    @staticmethod
    def create(strategy_type: str, config: Dict[str, Any]) -> StorageStrategy:
 
        strategy_type = strategy_type.lower().strip()
        
        if strategy_type not in STRATEGIES:
            available = ", ".join(STRATEGIES.keys())
            raise ValueError(
                f"Unknown storage strategy: '{strategy_type}'. "
                f"Available strategies: {available}"
            )
        
        strategy_class = STRATEGIES[strategy_type]
        logger.info(f"Creating storage strategy: {strategy_type}")
        
        try:
            return strategy_class(config)
        except Exception as e:
            logger.error(f"Failed to create {strategy_type} strategy: {e}")
            raise
    
    @staticmethod
    def register(name: str, strategy_class: type) -> None:
 
        if not issubclass(strategy_class, StorageStrategy):
            raise ValueError(
                f"{strategy_class.__name__} must inherit from StorageStrategy"
            )
        
        STRATEGIES[name.lower()] = strategy_class
        logger.info(f"Registered new storage strategy: {name}")
    
    @staticmethod
    def get_available_strategies() -> list[str]:
 
        return sorted(list(STRATEGIES.keys()))


def load_storage_strategy(
    storage_config: Dict[str, Any],
) -> StorageStrategy:
 
    if not isinstance(storage_config, dict):
        raise ValueError("storage_config must be a dictionary")
    
    strategy_type = storage_config.get("type")
    if not strategy_type:
        raise ValueError("storage_config must contain 'type' key")
    
    config = storage_config.get("config", {})
    if not isinstance(config, dict):
        raise ValueError("storage_config['config'] must be a dictionary")
    
    logger.info(f"Loading storage strategy from config: type={strategy_type}")
    return StorageStrategyFactory.create(strategy_type, config)

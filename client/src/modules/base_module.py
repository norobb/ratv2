"""
Base Module Class - Template for all client modules
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from ..core.config import ClientConfig


class BaseModule(ABC):
    """Base class for all client modules"""

    def __init__(self, config: ClientConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.is_initialized = False
        self.is_running = False
        self._background_task: Optional[asyncio.Task] = None

    @abstractmethod
    async def initialize(self):
        """Initialize the module"""
        pass

    @abstractmethod
    async def cleanup(self):
        """Cleanup module resources"""
        pass

    async def start(self):
        """Start the module"""
        if not self.is_initialized:
            await self.initialize()

        self.is_running = True
        self.logger.info(f"Module {self.__class__.__name__} started")

    async def stop(self):
        """Stop the module"""
        self.is_running = False

        if self._background_task:
            self._background_task.cancel()
            try:
                await self._background_task
            except asyncio.CancelledError:
                pass

        self.logger.info(f"Module {self.__class__.__name__} stopped")

    async def get_status(self) -> Dict[str, Any]:
        """Get module status"""
        return {
            "name": self.__class__.__name__,
            "initialized": self.is_initialized,
            "running": self.is_running,
            "config": self.get_config_info()
        }

    def get_config_info(self) -> Dict[str, Any]:
        """Get module configuration information"""
        return {
            "enabled": self.__class__.__name__.lower() in self.config.enabled_modules
        }

    async def execute_background_task(self, task_func):
        """Execute a background task"""
        if self._background_task:
            self._background_task.cancel()

        self._background_task = asyncio.create_task(task_func())

    def log_info(self, message: str):
        """Log info message"""
        self.logger.info(message)

    def log_error(self, message: str, exc_info: bool = False):
        """Log error message"""
        self.logger.error(message, exc_info=exc_info)

    def log_warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)

    def log_debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)

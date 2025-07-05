"""
Module Manager - Handles loading and execution of client modules
"""

import asyncio
import importlib
import logging
from typing import Any, Dict, List, Optional

from ..core.config import ClientConfig


class ModuleManager:
    """Manages client modules and their execution"""

    def __init__(self, config: ClientConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.modules: Dict[str, Any] = {}
        self.module_tasks: Dict[str, asyncio.Task] = {}

    async def initialize(self):
        """Initialize all enabled modules"""
        self.logger.info("Initializing modules...")

        for module_name in self.config.enabled_modules:
            try:
                await self.load_module(module_name)
            except Exception as e:
                self.logger.error(f"Failed to load module {module_name}: {e}")

        self.logger.info(f"Initialized {len(self.modules)} modules")

    async def load_module(self, module_name: str):
        """Load a specific module"""
        try:
            # Import module dynamically
            module_path = f"..modules.{module_name}.{module_name}"
            module = importlib.import_module(module_path, package=__name__)

            # Get module class (assuming class name is capitalized module name)
            class_name = ''.join(word.capitalize() for word in module_name.split('_'))
            module_class = getattr(module, class_name)

            # Initialize module instance
            module_instance = module_class(self.config)
            await module_instance.initialize()

            self.modules[module_name] = module_instance
            self.logger.info(f"Module {module_name} loaded successfully")

        except Exception as e:
            self.logger.error(f"Failed to load module {module_name}: {e}")
            raise

    async def unload_module(self, module_name: str):
        """Unload a specific module"""
        if module_name in self.modules:
            try:
                # Stop module task if running
                if module_name in self.module_tasks:
                    self.module_tasks[module_name].cancel()
                    del self.module_tasks[module_name]

                # Cleanup module
                await self.modules[module_name].cleanup()
                del self.modules[module_name]

                self.logger.info(f"Module {module_name} unloaded")

            except Exception as e:
                self.logger.error(f"Error unloading module {module_name}: {e}")

    async def enable_module(self, module_name: str):
        """Enable a module"""
        if module_name not in self.modules:
            await self.load_module(module_name)

        self.config.enable_module(module_name)

    async def disable_module(self, module_name: str):
        """Disable a module"""
        await self.unload_module(module_name)
        self.config.disable_module(module_name)

    async def reload_module(self, module_name: str):
        """Reload a module"""
        await self.unload_module(module_name)
        await self.load_module(module_name)

    async def execute_command(self, module_name: str, command: str, parameters: Dict) -> Any:
        """Execute a command on a specific module"""
        if module_name not in self.modules:
            raise ValueError(f"Module {module_name} not loaded")

        module = self.modules[module_name]

        if not hasattr(module, command):
            raise ValueError(f"Command {command} not found in module {module_name}")

        # Execute command
        command_method = getattr(module, command)

        if asyncio.iscoroutinefunction(command_method):
            return await command_method(**parameters)
        else:
            return command_method(**parameters)

    async def get_module_status(self) -> Dict[str, Dict]:
        """Get status of all modules"""
        status = {}

        for module_name, module in self.modules.items():
            try:
                if hasattr(module, 'get_status'):
                    module_status = await module.get_status()
                else:
                    module_status = {"status": "active", "info": "No status method"}

                status[module_name] = module_status

            except Exception as e:
                status[module_name] = {"status": "error", "error": str(e)}

        return status

    async def cleanup(self):
        """Cleanup all modules"""
        self.logger.info("Cleaning up modules...")

        # Cancel all running tasks
        for task in self.module_tasks.values():
            task.cancel()

        # Cleanup all modules
        for module_name in list(self.modules.keys()):
            await self.unload_module(module_name)

        self.logger.info("Module cleanup complete")

    def get_loaded_modules(self) -> List[str]:
        """Get list of loaded modules"""
        return list(self.modules.keys())

    def is_module_loaded(self, module_name: str) -> bool:
        """Check if a module is loaded"""
        return module_name in self.modules

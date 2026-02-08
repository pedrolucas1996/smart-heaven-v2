"""MQTT Client Service with async support."""
import asyncio
import json
import logging
from typing import Callable, Dict, Optional
from aiomqtt import Client, Message

from src.core.config import settings

logger = logging.getLogger(__name__)


class MQTTService:
    """Async MQTT client service."""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.is_connected = False
        self.message_handlers: Dict[str, Callable] = {}
        self._task: Optional[asyncio.Task] = None
        self._connect_lock = asyncio.Lock()
        self._reconnecting = False
    
    async def connect(self):
        """Connect to MQTT broker."""
        try:
            self.client = Client(
                hostname=settings.MQTT_BROKER_HOST,
                port=settings.MQTT_BROKER_PORT,
                identifier=settings.MQTT_CLIENT_ID,
            )
            
            # Set username/password if provided
            if settings.MQTT_USERNAME:
                self.client._client.username_pw_set(
                    settings.MQTT_USERNAME,
                    settings.MQTT_PASSWORD
                )
            
            await self.client.__aenter__()
            self.is_connected = True
            logger.info(f"Connected to MQTT broker at {settings.MQTT_BROKER_HOST}")

            # Restore subscriptions after reconnect
            if self.message_handlers:
                for topic in self.message_handlers.keys():
                    await self.client.subscribe(topic)
                logger.info("Re-subscribed to MQTT topics after reconnect")
            
            # Start message loop
            self._task = asyncio.create_task(self._message_loop())
            
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            self.is_connected = False
            raise
    
    async def disconnect(self):
        """Disconnect from MQTT broker."""
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        if self.client:
            await self.client.__aexit__(None, None, None)
            self.is_connected = False
            logger.info("Disconnected from MQTT broker")
        self.client = None
        self._task = None

    async def ensure_connected(self):
        """Ensure MQTT client is connected (with reconnect)."""
        if self.client and self.is_connected:
            return

        async with self._connect_lock:
            if self.client and self.is_connected:
                return

            if self.client and not self.is_connected:
                try:
                    await self.client.__aexit__(None, None, None)
                except Exception:
                    pass
                self.client = None
                self._task = None

            await self.connect()
    
    async def subscribe(self, topic: str, handler: Callable):
        """Subscribe to a topic with a handler."""
        if not self.client:
            await self.ensure_connected()
        
        await self.client.subscribe(topic)
        self.message_handlers[topic] = handler
        logger.info(f"Subscribed to topic: {topic}")
    
    async def publish(self, topic: str, payload: dict):
        """Publish a message to a topic."""
        if not self.client or not self.is_connected:
            await self.ensure_connected()
        
        try:
            message = json.dumps(payload)
            await self.client.publish(topic, message)
            logger.debug(f"Published to {topic}: {message}")
        except Exception as e:
            logger.error(f"Failed to publish to {topic}: {e}")
            self.is_connected = False
            try:
                await self.ensure_connected()
                await self.client.publish(topic, message)
                logger.debug(f"Published to {topic} after reconnect: {message}")
            except Exception:
                raise
    
    async def publish_state(self, comodo: str, estado: str):
        """Publish light state."""
        topic = f"{settings.MQTT_TOPIC_STATE}/{comodo}"
        await self.client.publish(topic, estado)
        logger.debug(f"Published state: {comodo} = {estado}")
    
    async def publish_debug(self, message: str):
        """Publish debug message."""
        await self.client.publish(settings.MQTT_TOPIC_DEBUG, message)
    
    async def _message_loop(self):
        """Internal message loop."""
        try:
            async for message in self.client.messages:
                await self._handle_message(message)
        except asyncio.CancelledError:
            logger.info("Message loop cancelled")
        except Exception as e:
            logger.error(f"Error in message loop: {e}")
            self.is_connected = False
            await self._reconnect()

    async def _reconnect(self):
        if self._reconnecting:
            return
        self._reconnecting = True
        try:
            await asyncio.sleep(1)
            await self.ensure_connected()
        except Exception as e:
            logger.error(f"MQTT reconnect failed: {e}")
        finally:
            self._reconnecting = False
    
    async def _handle_message(self, message: Message):
        """Handle incoming MQTT message."""
        topic = str(message.topic)
        
        # Find matching handler
        handler = None
        for subscribed_topic, topic_handler in self.message_handlers.items():
            if self._topic_matches(topic, subscribed_topic):
                handler = topic_handler
                break
        
        if handler:
            try:
                try:
                    payload = message.payload.decode("utf-8")
                except UnicodeDecodeError:
                    logger.warning(
                        "UTF-8 decode failed for topic %s, trying latin-1 with errors='ignore'",
                        topic
                    )
                    payload = message.payload.decode("latin-1", errors="ignore")
                await handler(topic, payload)
            except Exception as e:
                logger.error(f"Error handling message from {topic}: {e}")
        else:
            logger.warning(f"No handler for topic: {topic}")
    
    def _topic_matches(self, topic: str, pattern: str) -> bool:
        """Check if topic matches pattern (supports # and + wildcards)."""
        topic_parts = topic.split("/")
        pattern_parts = pattern.split("/")
        
        if len(pattern_parts) > len(topic_parts):
            return False
        
        for i, pattern_part in enumerate(pattern_parts):
            if pattern_part == "#":
                return True
            if pattern_part != "+" and pattern_part != topic_parts[i]:
                return False
        
        return len(topic_parts) == len(pattern_parts)


# Global MQTT service instance
mqtt_service = MQTTService()

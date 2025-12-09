"""FastAPI application main entry point."""
import logging
import json
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.infra.db import init_db, close_db, database
from src.services.mqtt_service import mqtt_service
from src.services.scheduler_service import scheduler
from src.services.light_service import LightService
from src.services.switch_service import SwitchService
from src.services.event_service import EventService
from src.services.event_cache import EventCache
from src.services.legacy_adapter import LegacyAdapter
from src.repositories.mapping_repo import MappingRepository
from src.repositories.lamp_repo import LampRepository
from src.repositories.light_repo import LightRepository
from src.namespaces.events.schemas import EventPayload, StatePayload
from src.namespaces.lights import controller as lights
from src.namespaces.lamps import controller as lamps
from src.namespaces.switches import controller as switches
from src.namespaces.logs import controller as logs
from src.namespaces.system import controller as system
from src.namespaces.events import controller as events
from src.namespaces.websocket import controller as websocket

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize event system
event_cache = EventCache(ttl_seconds=5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Smart Heaven Backend...")
    
    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    
    # Initialize event service
    async with database.session() as session:
        mapping_repo = MappingRepository(session)
        lamp_repo = LampRepository(session)
        light_repo = LightRepository(session)
        event_service = EventService(
            mapping_repo=mapping_repo,
            lamp_repo=lamp_repo,
            light_repo=light_repo,
            mqtt_service=mqtt_service,
            event_cache=event_cache
        )
    
    # Connect to MQTT broker
    try:
        await mqtt_service.connect()
        logger.info("MQTT connected")
        
        # Subscribe to topics with async handlers
        async def handle_state_update(topic: str, payload: str):
            """Handle state confirmation from devices (supports legacy formats)."""
            try:
                # Parse state payload
                import json
                data = json.loads(payload)
                
                # Check if legacy format and convert
                if LegacyAdapter.is_legacy_format(data):
                    logger.info(f"Legacy format detected, converting: {data}")
                    msg_type, state = LegacyAdapter.convert_legacy_message(data, topic)
                    if msg_type != "state":
                        logger.warning(f"Expected state message, got {msg_type}")
                        return
                else:
                    # Modern format - create StatePayload schema
                    state = StatePayload(
                        v=data.get("v", "1.0"),
                        comodo=data.get("comodo", data.get("lamp", "unknown")),
                        state=data.get("state", "OFF"),
                        origin=data.get("origin", "unknown"),
                        ts=data.get("ts", datetime.utcnow())
                    )
                
                # Process through EventService
                async with database.session() as session:
                    mapping_repo = MappingRepository(session)
                    lamp_repo = LampRepository(session)
                    light_repo = LightRepository(session)
                    event_svc = EventService(
                        mapping_repo=mapping_repo,
                        lamp_repo=lamp_repo,
                        light_repo=light_repo,
                        mqtt_service=mqtt_service,
                        event_cache=event_cache
                    )
                    result = await event_svc.process_state_confirmation(state)
                
                logger.info(f"State confirmation processed: {result}")
            except Exception as e:
                logger.error(f"Error processing state update: {e}")
        
        async def handle_button_event(topic: str, payload: str):
            """Handle button press events from devices (supports legacy formats)."""
            try:
                # Parse event payload
                import json
                data = json.loads(payload)
                
                # Check if legacy format and convert
                if LegacyAdapter.is_legacy_format(data):
                    logger.info(f"Legacy format detected, converting: {data}")
                    msg_type, event = LegacyAdapter.convert_legacy_message(data, topic)
                    if msg_type != "event":
                        logger.warning(f"Expected button event, got {msg_type}")
                        return
                else:
                    # Modern format - create EventPayload schema
                    event = EventPayload(
                        v=data.get("v", "1.0"),
                        device=data.get("device", "unknown"),
                        type=data.get("type", "button"),
                        button=data.get("button", "unknown"),
                        action=data.get("action", "press"),
                        rssi=data.get("rssi"),
                        origin=data.get("origin", "esp"),
                        ts=data.get("ts", datetime.utcnow())
                    )
                
                # Process through EventService
                async with database.session() as session:
                    mapping_repo = MappingRepository(session)
                    lamp_repo = LampRepository(session)
                    light_repo = LightRepository(session)
                    event_svc = EventService(
                        mapping_repo=mapping_repo,
                        lamp_repo=lamp_repo,
                        light_repo=light_repo,
                        mqtt_service=mqtt_service,
                        event_cache=event_cache
                    )
                    result = await event_svc.process_button_event(event)
                
                logger.info(f"Button event processed: {result}")
            except Exception as e:
                logger.error(f"Error processing button event: {e}")
        
        async def handle_web_command(topic: str, payload: str):
            """Handle commands from web interface."""
            logger.info(f"Web command received: {payload}")
            # Web commands bypass automation - handled by LampController
        
        await mqtt_service.subscribe(
            f"{settings.MQTT_TOPIC_STATE}/#",
            handle_state_update
        )
        await mqtt_service.subscribe(
            settings.MQTT_TOPIC_BUTTON,
            handle_button_event
        )
        await mqtt_service.subscribe(
            settings.MQTT_TOPIC_WEB_COMMAND,
            handle_web_command
        )
        
        logger.info("MQTT subscriptions configured with EventService")
    except Exception as e:
        logger.error(f"Failed to connect to MQTT: {e}")
    
    # Start cleanup scheduler
    try:
        await scheduler.start()
        logger.info("Cleanup scheduler started")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Smart Heaven Backend...")
    
    # Stop scheduler
    try:
        await scheduler.stop()
        logger.info("Scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
    
    try:
        await mqtt_service.disconnect()
        logger.info("MQTT disconnected")
    except Exception as e:
        logger.error(f"Error disconnecting MQTT: {e}")
    
    try:
        await close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Smart Heaven Home Automation API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(system.router, prefix="/api/v1")
app.include_router(lights.router, prefix="/api/v1")
app.include_router(lamps.router, prefix="/api/v1")
app.include_router(switches.router, prefix="/api/v1")
app.include_router(logs.router, prefix="/api/v1")
app.include_router(events.router)  # Already includes /api/v1/events prefix
app.include_router(websocket.router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

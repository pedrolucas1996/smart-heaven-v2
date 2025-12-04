"""FastAPI application main entry point."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.infra.db import init_db, close_db
from src.services.mqtt_service import mqtt_service
from src.services.light_service import LightService
from src.services.switch_service import SwitchService
from src.namespaces.lights import controller as lights
from src.namespaces.switches import controller as switches
from src.namespaces.logs import controller as logs
from src.namespaces.system import controller as system
from src.namespaces.websocket import controller as websocket

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


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
    
    # Connect to MQTT broker
    try:
        await mqtt_service.connect()
        logger.info("MQTT connected")
        
        # Subscribe to topics
        await mqtt_service.subscribe(
            f"{settings.MQTT_TOPIC_STATE}/#",
            lambda topic, payload: logger.info(f"State update: {topic}")
        )
        await mqtt_service.subscribe(
            settings.MQTT_TOPIC_BUTTON,
            lambda topic, payload: logger.info(f"Button event: {payload}")
        )
        await mqtt_service.subscribe(
            settings.MQTT_TOPIC_WEB_COMMAND,
            lambda topic, payload: logger.info(f"Web command: {payload}")
        )
        
        logger.info("MQTT subscriptions configured")
    except Exception as e:
        logger.error(f"Failed to connect to MQTT: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Smart Heaven Backend...")
    
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
app.include_router(switches.router, prefix="/api/v1")
app.include_router(logs.router, prefix="/api/v1")
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

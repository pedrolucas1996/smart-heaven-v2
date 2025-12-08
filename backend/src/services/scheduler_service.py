"""Background task scheduler for periodic cleanup."""
import asyncio
import logging
from datetime import datetime
from typing import Optional

from src.infra.db import database
from src.services.cleanup_service import CleanupService

logger = logging.getLogger(__name__)


class SchedulerService:
    """Service for scheduling periodic background tasks."""
    
    def __init__(
        self,
        cleanup_logs_days: int = 7,
        cleanup_logs_limit: int = 1000,
        cleanup_interval_hours: int = 24
    ):
        self.cleanup_logs_days = cleanup_logs_days
        self.cleanup_logs_limit = cleanup_logs_limit
        self.cleanup_interval_hours = cleanup_interval_hours
        self._task: Optional[asyncio.Task] = None
        self._running = False
    
    async def start(self):
        """Start the scheduler."""
        if self._running:
            logger.warning("Scheduler already running")
            return
        
        self._running = True
        self._task = asyncio.create_task(self._run())
        logger.info(
            f"Scheduler started - cleanup every {self.cleanup_interval_hours}h, "
            f"keeping logs: {self.cleanup_logs_days} days or {self.cleanup_logs_limit} records"
        )
    
    async def stop(self):
        """Stop the scheduler."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Scheduler stopped")
    
    async def _run(self):
        """Main scheduler loop."""
        while self._running:
            try:
                # Wait for the interval
                await asyncio.sleep(self.cleanup_interval_hours * 3600)
                
                if not self._running:
                    break
                
                # Run cleanup
                await self._run_cleanup()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                # Wait a bit before retrying
                await asyncio.sleep(60)
    
    async def _run_cleanup(self):
        """Execute cleanup tasks."""
        try:
            logger.info(f"Starting scheduled cleanup at {datetime.utcnow()}")
            
            async with database.session() as db:
                service = CleanupService(db)
                
                # Get stats before cleanup
                stats_before = await service.get_logs_statistics()
                logger.info(f"Logs before cleanup: {stats_before['total_logs']}")
                
                # Clean old logs
                deleted_old = await service.cleanup_old_logs(self.cleanup_logs_days)
                logger.info(f"Deleted {deleted_old} logs older than {self.cleanup_logs_days} days")
                
                # Keep only recent N logs
                deleted_limit = await service.cleanup_logs_by_limit(self.cleanup_logs_limit)
                logger.info(f"Deleted {deleted_limit} logs to keep limit of {self.cleanup_logs_limit}")
                
                # Get stats after cleanup
                stats_after = await service.get_logs_statistics()
                logger.info(f"Logs after cleanup: {stats_after['total_logs']}")
                
                # Clean duplicate lights
                deleted_dupes = await service.cleanup_duplicate_lights()
                if deleted_dupes > 0:
                    logger.info(f"Deleted {deleted_dupes} duplicate light records")
                
                logger.info("Scheduled cleanup completed successfully")
                
        except Exception as e:
            logger.error(f"Error during cleanup: {e}", exc_info=True)
    
    async def run_now(self):
        """Run cleanup immediately (manual trigger)."""
        logger.info("Manual cleanup triggered")
        await self._run_cleanup()


# Global scheduler instance
scheduler = SchedulerService(
    cleanup_logs_days=7,
    cleanup_logs_limit=1000,
    cleanup_interval_hours=24
)

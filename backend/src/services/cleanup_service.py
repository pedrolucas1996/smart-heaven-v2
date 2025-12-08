"""Cleanup service for maintaining database hygiene."""
import logging
from datetime import datetime, timedelta
from sqlalchemy import delete, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.log import Log
from src.models.light import Light

logger = logging.getLogger(__name__)


class CleanupService:
    """Service for database cleanup operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def cleanup_old_logs(self, days: int = 7) -> int:
        """
        Delete logs older than specified days.
        
        Args:
            days: Number of days to retain (default: 7)
            
        Returns:
            Number of deleted records
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        result = await self.db.execute(
            delete(Log).where(Log.data_hora < cutoff_date)
        )
        
        deleted_count = result.rowcount
        await self.db.commit()
        
        logger.info(f"Deleted {deleted_count} log records older than {days} days")
        return deleted_count
    
    async def cleanup_logs_by_limit(self, max_records: int = 1000) -> int:
        """
        Keep only the most recent N log records, delete older ones.
        
        Args:
            max_records: Maximum number of records to keep (default: 1000)
            
        Returns:
            Number of deleted records
        """
        # Count total records
        count_result = await self.db.execute(
            select(func.count(Log.id))
        )
        total_count = count_result.scalar()
        
        if total_count <= max_records:
            logger.info(f"Log count ({total_count}) within limit ({max_records}), no cleanup needed")
            return 0
        
        # Get the ID of the Nth most recent record
        subquery = select(Log.id).order_by(Log.data_hora.desc()).limit(max_records).subquery()
        
        # Delete all records not in the top N
        result = await self.db.execute(
            delete(Log).where(Log.id.notin_(select(subquery.c.id)))
        )
        
        deleted_count = result.rowcount
        await self.db.commit()
        
        logger.info(f"Deleted {deleted_count} log records, kept {max_records} most recent")
        return deleted_count
    
    async def cleanup_duplicate_lights(self) -> int:
        """
        Remove duplicate entries in luzes table, keeping only the most recent.
        
        Returns:
            Number of deleted records
        """
        # Get all lampada names with duplicates
        duplicates_query = select(
            Light.lampada,
            func.count(Light.id).label('count')
        ).group_by(Light.lampada).having(func.count(Light.id) > 1)
        
        duplicates_result = await self.db.execute(duplicates_query)
        duplicates = duplicates_result.all()
        
        deleted_count = 0
        
        for lampada_name, count in duplicates:
            # Get all records for this lampada, ordered by id (most recent last)
            records_result = await self.db.execute(
                select(Light.id)
                .where(Light.lampada == lampada_name)
                .order_by(Light.id.asc())
            )
            record_ids = [row[0] for row in records_result.all()]
            
            # Keep only the last one, delete the rest
            if len(record_ids) > 1:
                ids_to_delete = record_ids[:-1]
                result = await self.db.execute(
                    delete(Light).where(Light.id.in_(ids_to_delete))
                )
                deleted_count += result.rowcount
                logger.info(f"Deleted {len(ids_to_delete)} duplicate records for '{lampada_name}'")
        
        await self.db.commit()
        logger.info(f"Total duplicate lights deleted: {deleted_count}")
        return deleted_count
    
    async def get_logs_statistics(self) -> dict:
        """Get statistics about logs table."""
        # Total count
        total_result = await self.db.execute(select(func.count(Log.id)))
        total_count = total_result.scalar()
        
        # Oldest record
        oldest_result = await self.db.execute(
            select(func.min(Log.data_hora))
        )
        oldest_date = oldest_result.scalar()
        
        # Newest record
        newest_result = await self.db.execute(
            select(func.max(Log.data_hora))
        )
        newest_date = newest_result.scalar()
        
        # Records per day (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_result = await self.db.execute(
            select(func.count(Log.id))
            .where(Log.data_hora >= seven_days_ago)
        )
        recent_count = recent_result.scalar()
        
        return {
            "total_logs": total_count,
            "oldest_log": oldest_date.isoformat() if oldest_date else None,
            "newest_log": newest_date.isoformat() if newest_date else None,
            "logs_last_7_days": recent_count,
            "avg_logs_per_day": round(recent_count / 7, 2) if recent_count else 0
        }
    
    async def get_lights_statistics(self) -> dict:
        """Get statistics about luzes table."""
        # Total count
        total_result = await self.db.execute(select(func.count(Light.id)))
        total_count = total_result.scalar()
        
        # Count duplicates
        duplicates_query = select(
            func.count(Light.lampada).label('unique_count')
        ).group_by(Light.lampada).having(func.count(Light.id) > 1)
        
        duplicates_result = await self.db.execute(duplicates_query)
        duplicate_groups = len(duplicates_result.all())
        
        # Unique lampadas
        unique_result = await self.db.execute(
            select(func.count(func.distinct(Light.lampada)))
        )
        unique_count = unique_result.scalar()
        
        return {
            "total_records": total_count,
            "unique_lights": unique_count,
            "duplicate_groups": duplicate_groups,
            "duplicates_exist": total_count > unique_count
        }

"""Event cache for idempotency."""
import time
import hashlib
from typing import Dict, Tuple
from threading import Lock


class EventCache:
    """Cache for tracking recent events to prevent duplicates."""
    
    def __init__(self, ttl_seconds: int = 5):
        """
        Initialize event cache.
        
        Args:
            ttl_seconds: Time to live for cached events in seconds
        """
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, float] = {}
        self._lock = Lock()
    
    def _cleanup_expired(self):
        """Remove expired entries from cache."""
        now = time.time()
        expired_keys = [
            key for key, timestamp in self._cache.items()
            if now - timestamp > self.ttl_seconds
        ]
        for key in expired_keys:
            del self._cache[key]
    
    def generate_event_hash(
        self, 
        device: str, 
        button: str, 
        action: str,
        timestamp: str = None
    ) -> str:
        """
        Generate hash for an event.
        
        Args:
            device: Device/base name
            button: Button name
            action: Action performed
            timestamp: Optional timestamp for uniqueness
            
        Returns:
            SHA256 hash of the event
        """
        # Create unique identifier without timestamp for deduplication
        event_str = f"{device}:{button}:{action}"
        return hashlib.sha256(event_str.encode()).hexdigest()
    
    def is_duplicate(self, event_hash: str) -> bool:
        """
        Check if event is a duplicate.
        
        Args:
            event_hash: Hash of the event
            
        Returns:
            True if event was recently processed
        """
        with self._lock:
            self._cleanup_expired()
            
            now = time.time()
            
            # Check if event exists and is still valid
            if event_hash in self._cache:
                age = now - self._cache[event_hash]
                if age <= self.ttl_seconds:
                    return True
            
            # Mark event as processed
            self._cache[event_hash] = now
            return False
    
    def mark_processed(self, event_hash: str):
        """
        Mark an event as processed.
        
        Args:
            event_hash: Hash of the event
        """
        with self._lock:
            self._cache[event_hash] = time.time()
    
    def clear(self):
        """Clear all cached events."""
        with self._lock:
            self._cache.clear()
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        with self._lock:
            self._cleanup_expired()
            return {
                "total_cached": len(self._cache),
                "ttl_seconds": self.ttl_seconds
            }


# Global event cache instance
event_cache = EventCache(ttl_seconds=5)

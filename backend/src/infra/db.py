"""Database configuration and custom database class."""
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, AsyncEngine
from sqlalchemy.orm import declarative_base
from sqlalchemy import text

from src.core.config import settings


class CustomDatabase:
    """Custom database class for managing database connections and sessions."""
    
    def __init__(self, database_url: str, echo: bool = False):
        """
        Initialize the database connection.
        
        Args:
            database_url: Database connection URL
            echo: Whether to echo SQL queries
        """
        self.database_url = database_url
        self.echo = echo
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker] = None
        
    @property
    def engine(self) -> AsyncEngine:
        """Get or create the async engine."""
        if self._engine is None:
            self._engine = create_async_engine(
                self.database_url,
                echo=self.echo,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
            )
        return self._engine
    
    @property
    def session_factory(self) -> async_sessionmaker:
        """Get or create the session factory."""
        if self._session_factory is None:
            self._session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )
        return self._session_factory
    
    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get a database session context manager.
        
        Usage:
            async with db.session() as session:
                result = await session.execute(query)
        """
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Dependency for getting async database session.
        
        Usage:
            @app.get("/items")
            async def get_items(db: AsyncSession = Depends(database.get_session)):
                ...
        """
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def init_db(self, base):
        """
        Initialize database tables.
        
        Args:
            base: SQLAlchemy declarative base with models
        """
        async with self.engine.begin() as conn:
            await conn.run_sync(base.metadata.create_all)
    
    async def check_connection(self) -> bool:
        """
        Check if database connection is alive.
        
        Returns:
            True if connected, False otherwise
        """
        try:
            async with self.session() as session:
                await session.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
    
    async def close(self):
        """Close database connections and dispose of the engine."""
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None


# Base class for models
Base = declarative_base()

# Global database instance
database = CustomDatabase(
    database_url=settings.DATABASE_URL,
    echo=settings.DB_ECHO
)


# Backward compatibility functions
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session (backward compatibility).
    
    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async for session in database.get_session():
        yield session


async def init_db():
    """Initialize database tables (backward compatibility)."""
    await database.init_db(Base)


async def close_db():
    """Close database connections (backward compatibility)."""
    await database.close()

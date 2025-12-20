"""Database configuration and connection pooling."""
from typing import Optional
from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool, NullPool
import logging

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Configuration for database connections."""
    
    def __init__(
        self,
        database_url: str,
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        echo: bool = False,
        use_pool: bool = True
    ):
        """Initialize database configuration.
        
        Args:
            database_url: SQLAlchemy database URL
            pool_size: Size of the connection pool
            max_overflow: Max connections beyond pool_size
            pool_timeout: Timeout for getting connection from pool
            pool_recycle: Recycle connections after this many seconds
            echo: Echo SQL statements to log
            use_pool: Use connection pooling (False for SQLite)
        """
        self.database_url = database_url
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
        self.echo = echo
        self.use_pool = use_pool
        self._engine: Optional[Engine] = None
        self._session_factory = None
    
    def create_engine(self) -> Engine:
        """Create SQLAlchemy engine with pooling configuration.
        
        Returns:
            Configured database engine
        """
        if self._engine is not None:
            return self._engine
        
        engine_kwargs = {
            'echo': self.echo,
        }
        
        # Configure pooling based on database type
        if self.use_pool and not self.database_url.startswith('sqlite'):
            engine_kwargs.update({
                'poolclass': QueuePool,
                'pool_size': self.pool_size,
                'max_overflow': self.max_overflow,
                'pool_timeout': self.pool_timeout,
                'pool_recycle': self.pool_recycle,
                'pool_pre_ping': True,  # Verify connections before using
            })
        else:
            # SQLite doesn't support connection pooling well
            engine_kwargs['poolclass'] = NullPool
        
        self._engine = create_engine(self.database_url, **engine_kwargs)
        
        # Add event listeners
        self._setup_event_listeners(self._engine)
        
        logger.info(f"Created database engine for {self.database_url}")
        return self._engine
    
    def _setup_event_listeners(self, engine: Engine) -> None:
        """Setup event listeners for connection management.
        
        Args:
            engine: Database engine
        """
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            """Enable foreign keys and WAL mode for SQLite."""
            if 'sqlite' in str(dbapi_conn):
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.close()
        
        @event.listens_for(engine, "checkin")
        def receive_checkin(dbapi_conn, connection_record):
            """Log connection checkin."""
            logger.debug("Connection returned to pool")
        
        @event.listens_for(engine, "checkout")
        def receive_checkout(dbapi_conn, connection_record, connection_proxy):
            """Log connection checkout."""
            logger.debug("Connection retrieved from pool")
    
    def get_session_factory(self) -> scoped_session:
        """Get thread-safe session factory.
        
        Returns:
            Scoped session factory
        """
        if self._session_factory is None:
            engine = self.create_engine()
            session_factory = sessionmaker(bind=engine)
            self._session_factory = scoped_session(session_factory)
            logger.info("Created scoped session factory")
        return self._session_factory
    
    def get_session(self):
        """Get a new database session.
        
        Returns:
            Database session (context manager)
        """
        Session = self.get_session_factory()
        return Session()
    
    def dispose(self) -> None:
        """Dispose of the engine and close all connections."""
        if self._engine is not None:
            self._engine.dispose()
            logger.info("Database engine disposed")
        if self._session_factory is not None:
            self._session_factory.remove()
            logger.info("Session factory removed")
    
    def get_pool_status(self) -> dict:
        """Get current connection pool status.
        
        Returns:
            Dictionary with pool statistics
        """
        if self._engine is None or not self.use_pool:
            return {}
        
        pool = self._engine.pool
        return {
            'size': pool.size(),
            'checked_in': pool.checkedin(),
            'checked_out': pool.checkedout(),
            'overflow': pool.overflow(),
            'total': pool.size() + pool.overflow()
        }

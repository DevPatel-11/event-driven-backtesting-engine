"""Database migration utilities."""
from typing import List, Callable
from sqlalchemy import inspect, Table, MetaData
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class MigrationManager:
    """Manager for database schema migrations."""
    
    def __init__(self, engine):
        """Initialize migration manager.
        
        Args:
            engine: SQLAlchemy engine
        """
        self.engine = engine
        self.metadata = MetaData()
        self.migrations: List[Migration] = []
    
    def register_migration(self, migration: 'Migration') -> None:
        """Register a migration.
        
        Args:
            migration: Migration to register
        """
        self.migrations.append(migration)
        self.migrations.sort(key=lambda m: m.version)
        logger.info(f"Registered migration v{migration.version}: {migration.name}")
    
    def get_current_version(self) -> int:
        """Get current database schema version.
        
        Returns:
            Current version number
        """
        inspector = inspect(self.engine)
        if 'schema_version' not in inspector.get_table_names():
            return 0
        
        with Session(self.engine) as session:
            result = session.execute(
                "SELECT version FROM schema_version ORDER BY version DESC LIMIT 1"
            )
            row = result.first()
            return row[0] if row else 0
    
    def set_version(self, version: int) -> None:
        """Set database schema version.
        
        Args:
            version: Version number to set
        """
        with Session(self.engine) as session:
            session.execute(
                "INSERT INTO schema_version (version, applied_at) VALUES (?, CURRENT_TIMESTAMP)",
                (version,)
            )
            session.commit()
        logger.info(f"Set schema version to {version}")
    
    def create_version_table(self) -> None:
        """Create schema version tracking table if it doesn't exist."""
        with Session(self.engine) as session:
            session.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version INTEGER NOT NULL,
                    applied_at TIMESTAMP NOT NULL
                )
            """)
            session.commit()
        logger.info("Created schema_version table")
    
    def migrate(self, target_version: int = None) -> None:
        """Run migrations up to target version.
        
        Args:
            target_version: Version to migrate to (None for latest)
        """
        self.create_version_table()
        current_version = self.get_current_version()
        
        if target_version is None:
            target_version = self.migrations[-1].version if self.migrations else 0
        
        logger.info(f"Current version: {current_version}, Target: {target_version}")
        
        for migration in self.migrations:
            if current_version < migration.version <= target_version:
                logger.info(f"Applying migration v{migration.version}: {migration.name}")
                migration.upgrade(self.engine)
                self.set_version(migration.version)
                logger.info(f"Migration v{migration.version} applied successfully")
    
    def rollback(self, target_version: int) -> None:
        """Rollback migrations to target version.
        
        Args:
            target_version: Version to roll back to
        """
        current_version = self.get_current_version()
        logger.info(f"Rolling back from v{current_version} to v{target_version}")
        
        for migration in reversed(self.migrations):
            if target_version < migration.version <= current_version:
                logger.info(f"Rolling back migration v{migration.version}: {migration.name}")
                migration.downgrade(self.engine)
                logger.info(f"Migration v{migration.version} rolled back")


class Migration:
    """Base class for database migrations."""
    
    def __init__(self, version: int, name: str):
        """Initialize migration.
        
        Args:
            version: Migration version number
            name: Migration name/description
        """
        self.version = version
        self.name = name
    
    def upgrade(self, engine) -> None:
        """Apply migration.
        
        Args:
            engine: Database engine
        """
        raise NotImplementedError("Subclasses must implement upgrade()")
    
    def downgrade(self, engine) -> None:
        """Revert migration.
        
        Args:
            engine: Database engine
        """
        raise NotImplementedError("Subclasses must implement downgrade()")


class AddIndexMigration(Migration):
    """Migration to add database indexes for performance."""
    
    def __init__(self):
        super().__init__(version=1, name="Add performance indexes")
    
    def upgrade(self, engine) -> None:
        """Add indexes to improve query performance."""
        with Session(engine) as session:
            # Add index on backtest_runs.strategy_name for faster filtering
            session.execute("""
                CREATE INDEX IF NOT EXISTS idx_backtest_runs_strategy 
                ON backtest_runs(strategy_name)
            """)
            
            # Add index on backtest_runs.created_at for sorting
            session.execute("""
                CREATE INDEX IF NOT EXISTS idx_backtest_runs_created 
                ON backtest_runs(created_at)
            """)
            
            # Add index on trades.backtest_run_id for joins
            session.execute("""
                CREATE INDEX IF NOT EXISTS idx_trades_backtest_run 
                ON trades(backtest_run_id)
            """)
            
            # Add index on trades.symbol for filtering
            session.execute("""
                CREATE INDEX IF NOT EXISTS idx_trades_symbol 
                ON trades(symbol)
            """)
            
            session.commit()
    
    def downgrade(self, engine) -> None:
        """Remove indexes."""
        with Session(engine) as session:
            session.execute("DROP INDEX IF EXISTS idx_backtest_runs_strategy")
            session.execute("DROP INDEX IF EXISTS idx_backtest_runs_created")
            session.execute("DROP INDEX IF EXISTS idx_trades_backtest_run")
            session.execute("DROP INDEX IF EXISTS idx_trades_symbol")
            session.commit()

"""
Database connection management for Procure-Pro-ISO.

Provides SQLAlchemy engine and session management.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from procure_pro_iso.config import settings


class DatabaseManager:
    """
    Manages database connections and sessions.

    Provides connection pooling and session lifecycle management.
    """

    def __init__(
        self,
        database_url: str | None = None,
        pool_size: int | None = None,
        max_overflow: int | None = None,
        pool_timeout: int | None = None,
        pool_recycle: int | None = None,
        echo: bool = False,
    ):
        """
        Initialize the database manager.

        Args:
            database_url: PostgreSQL connection URL.
            pool_size: Connection pool size.
            max_overflow: Max connections beyond pool_size.
            pool_timeout: Timeout for getting connection from pool.
            pool_recycle: Recycle connections after this many seconds.
            echo: If True, log all SQL statements.
        """
        self.database_url = database_url or settings.sync_database_url
        self.pool_size = pool_size or settings.db_pool_size
        self.max_overflow = max_overflow or settings.db_max_overflow
        self.pool_timeout = pool_timeout or settings.db_pool_timeout
        self.pool_recycle = pool_recycle or settings.db_pool_recycle
        self.echo = echo or settings.debug

        self._engine: Engine | None = None
        self._session_factory: sessionmaker | None = None

    @property
    def engine(self) -> Engine:
        """Get or create the SQLAlchemy engine."""
        if self._engine is None:
            self._engine = create_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_timeout=self.pool_timeout,
                pool_recycle=self.pool_recycle,
                pool_pre_ping=True,  # Verify connections before using
                echo=self.echo,
            )

            # Set up connection event listeners
            @event.listens_for(self._engine, "connect")
            def set_search_path(dbapi_connection, connection_record):
                """Set default schema on new connections."""
                cursor = dbapi_connection.cursor()
                cursor.execute("SET search_path TO public")
                cursor.close()

        return self._engine

    @property
    def session_factory(self) -> sessionmaker:
        """Get or create the session factory."""
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
            )
        return self._session_factory

    def get_session(self) -> Session:
        """
        Create a new database session.

        Returns:
            SQLAlchemy Session instance.
        """
        return self.session_factory()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Provide a transactional scope around a series of operations.

        Yields:
            SQLAlchemy Session instance.

        Example:
            with db_manager.session_scope() as session:
                session.add(item)
                session.commit()
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def create_all_tables(self) -> None:
        """Create all database tables defined in models."""
        from procure_pro_iso.database.models import Base

        Base.metadata.create_all(bind=self.engine)

    def drop_all_tables(self) -> None:
        """Drop all database tables. Use with caution!"""
        from procure_pro_iso.database.models import Base

        Base.metadata.drop_all(bind=self.engine)

    def check_connection(self) -> bool:
        """
        Check if database connection is working.

        Returns:
            True if connection is successful.
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    def dispose(self) -> None:
        """Dispose of the connection pool."""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            self._session_factory = None


# Global database manager instance
_db_manager: DatabaseManager | None = None


def get_db_manager() -> DatabaseManager:
    """
    Get the global database manager instance.

    Returns:
        DatabaseManager instance.
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database sessions.

    Yields:
        SQLAlchemy Session instance.

    Example:
        def my_function(db: Session = Depends(get_db)):
            ...
    """
    db_manager = get_db_manager()
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    """
    Initialize the database.

    Creates all tables if they don't exist.
    """
    db_manager = get_db_manager()
    db_manager.create_all_tables()

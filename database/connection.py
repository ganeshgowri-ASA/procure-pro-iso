"""
Database Connection Module
Handles PostgreSQL database connections using SQLAlchemy
"""

import os
import logging
from contextlib import contextmanager
from flask import g, current_app
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

# Global database engine and session factory
_engine = None
_session_factory = None


def get_database_url():
    """
    Get database URL from environment variables.
    Handles Railway's DATABASE_URL format.
    """
    database_url = os.environ.get('DATABASE_URL')

    if database_url:
        # Railway uses postgres:// but SQLAlchemy needs postgresql://
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        return database_url

    # Build URL from individual components
    return (
        f"postgresql://"
        f"{os.environ.get('PGUSER', 'postgres')}:"
        f"{os.environ.get('PGPASSWORD', 'password')}@"
        f"{os.environ.get('PGHOST', 'localhost')}:"
        f"{os.environ.get('PGPORT', '5432')}/"
        f"{os.environ.get('PGDATABASE', 'procure_pro_iso')}"
    )


def init_db(app=None):
    """
    Initialize database connection.

    Args:
        app: Flask application instance (optional)
    """
    global _engine, _session_factory

    try:
        database_url = get_database_url()

        # Create engine with connection pooling
        _engine = create_engine(
            database_url,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
            pool_pre_ping=True,
            echo=os.environ.get('SQLALCHEMY_ECHO', 'False').lower() == 'true'
        )

        # Create session factory
        _session_factory = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=_engine
            )
        )

        logger.info("Database connection initialized successfully")

        # Test connection
        with _engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("Database connection test successful")

    except SQLAlchemyError as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise


def get_db():
    """
    Get database session for current request.

    Returns:
        SQLAlchemy session
    """
    if 'db' not in g:
        if _session_factory is None:
            init_db()
        g.db = _session_factory()
    return g.db


def close_db(exception=None):
    """
    Close database session at end of request.

    Args:
        exception: Exception that occurred (if any)
    """
    db = g.pop('db', None)
    if db is not None:
        if exception:
            db.rollback()
        db.close()


@contextmanager
def get_db_session():
    """
    Context manager for database sessions outside of Flask request context.

    Usage:
        with get_db_session() as session:
            result = session.execute(text("SELECT * FROM users"))

    Yields:
        SQLAlchemy session
    """
    if _session_factory is None:
        init_db()

    session = _session_factory()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        session.close()


def execute_query(query, params=None):
    """
    Execute a raw SQL query.

    Args:
        query: SQL query string
        params: Query parameters (optional)

    Returns:
        Query result
    """
    with get_db_session() as session:
        result = session.execute(text(query), params or {})
        return result


def execute_script(script_path):
    """
    Execute a SQL script file.

    Args:
        script_path: Path to SQL script file

    Returns:
        True if successful
    """
    try:
        with open(script_path, 'r') as f:
            script = f.read()

        with get_db_session() as session:
            # Split by semicolon and execute each statement
            statements = [s.strip() for s in script.split(';') if s.strip()]
            for statement in statements:
                if statement:
                    session.execute(text(statement))

        logger.info(f"SQL script executed successfully: {script_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to execute SQL script: {str(e)}")
        raise


def check_connection():
    """
    Check if database connection is healthy.

    Returns:
        dict with status and details
    """
    try:
        with get_db_session() as session:
            result = session.execute(text("SELECT version()"))
            version = result.scalar()

        return {
            'status': 'healthy',
            'database': 'postgresql',
            'version': version
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        }


def get_table_info():
    """
    Get information about all tables in the database.

    Returns:
        List of table information dictionaries
    """
    query = """
        SELECT
            table_name,
            (SELECT COUNT(*) FROM information_schema.columns
             WHERE table_name = t.table_name) as column_count
        FROM information_schema.tables t
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """

    with get_db_session() as session:
        result = session.execute(text(query))
        tables = []
        for row in result:
            tables.append({
                'table_name': row[0],
                'column_count': row[1]
            })
        return tables

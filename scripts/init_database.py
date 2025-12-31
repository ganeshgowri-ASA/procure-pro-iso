#!/usr/bin/env python3
"""
Initialize the Procure-Pro-ISO database.

This script:
1. Connects to the PostgreSQL database
2. Creates all required tables
3. Verifies the connection
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


def main():
    """Initialize the database."""
    print("=" * 60)
    print("Procure-Pro-ISO Database Initialization")
    print("=" * 60)

    try:
        from procure_pro_iso.config import settings
        from procure_pro_iso.database.connection import get_db_manager

        print(f"\nDatabase URL: {settings.database_url[:50]}...")
        print(f"Pool Size: {settings.db_pool_size}")
        print(f"Max Overflow: {settings.db_max_overflow}")

        # Get database manager
        db_manager = get_db_manager()

        # Check connection
        print("\nChecking database connection...")
        if db_manager.check_connection():
            print("✓ Database connection successful!")
        else:
            print("✗ Database connection failed!")
            return 1

        # Create tables
        print("\nCreating database tables...")
        db_manager.create_all_tables()
        print("✓ All tables created successfully!")

        # Verify tables
        print("\nVerifying tables...")
        from sqlalchemy import inspect

        inspector = inspect(db_manager.engine)
        tables = inspector.get_table_names()
        print(f"Found {len(tables)} tables:")
        for table in sorted(tables):
            print(f"  - {table}")

        print("\n" + "=" * 60)
        print("Database initialization completed successfully!")
        print("=" * 60)

        return 0

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

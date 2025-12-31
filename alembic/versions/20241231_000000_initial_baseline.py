"""Initial baseline - schema created via migration_runner.

Revision ID: 001_baseline
Revises:
Create Date: 2024-12-31 00:00:00.000000

This migration represents the baseline schema created by database/schema.sql.
It serves as the starting point for Alembic-managed migrations.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "001_baseline"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema.

    Note: The initial schema is created by database/schema.sql via migration_runner.
    This migration exists to establish a baseline for Alembic tracking.

    Run the following to apply the initial schema:
        python -m database.migration_runner migrate
    """
    # Check if schema already exists by looking for a known table
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'organizations')"
        )
    )
    schema_exists = result.fetchone()[0]

    if schema_exists:
        print("Schema already exists - skipping baseline creation")
        return

    print("WARNING: Initial schema should be created via migration_runner")
    print("Run: python -m database.migration_runner migrate")


def downgrade() -> None:
    """Downgrade database schema.

    WARNING: This will drop ALL tables in the public schema.
    Use with extreme caution!
    """
    conn = op.get_bind()

    # Get all tables
    result = conn.execute(
        sa.text(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
        )
    )
    tables = [row[0] for row in result.fetchall()]

    # Drop each table with CASCADE
    for table in tables:
        op.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')

#!/usr/bin/env python3
"""
Database Migration Runner for Procure-Pro-ISO
Connects to Railway PostgreSQL and executes migrations.
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

import psycopg2
from psycopg2 import sql, OperationalError
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

console = Console()

# Database connection parameters from environment
DB_CONFIG = {
    "host": os.getenv("PGHOST", os.getenv("DB_HOST", "localhost")),
    "port": os.getenv("PGPORT", os.getenv("DB_PORT", "5432")),
    "database": os.getenv("PGDATABASE", os.getenv("DB_NAME", "procure_pro_iso")),
    "user": os.getenv("PGUSER", os.getenv("DB_USER", "postgres")),
    "password": os.getenv("PGPASSWORD", os.getenv("DB_PASSWORD", "postgres")),
}


def get_database_url() -> str:
    """Build database URL from environment variables."""
    # Check for direct DATABASE_URL first
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    return (
        f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )


def get_connection(max_retries: int = 3, retry_delay: int = 5):
    """
    Establish database connection with retry logic.

    Args:
        max_retries: Maximum number of connection attempts
        retry_delay: Delay between retries in seconds

    Returns:
        psycopg2 connection object
    """
    # Try DATABASE_URL first (Railway format)
    database_url = os.getenv("DATABASE_URL")

    for attempt in range(max_retries):
        try:
            if database_url:
                console.print(f"[dim]Connecting via DATABASE_URL...[/dim]")
                conn = psycopg2.connect(database_url)
            else:
                console.print(f"[dim]Connecting via individual parameters...[/dim]")
                conn = psycopg2.connect(**DB_CONFIG)

            console.print("[green]✓[/green] Database connection established")
            return conn

        except OperationalError as e:
            if attempt < max_retries - 1:
                console.print(
                    f"[yellow]Connection attempt {attempt + 1} failed. "
                    f"Retrying in {retry_delay}s...[/yellow]"
                )
                time.sleep(retry_delay)
            else:
                console.print(f"[red]✗ Failed to connect after {max_retries} attempts[/red]")
                console.print(f"[red]Error: {e}[/red]")
                raise


def check_database_health() -> dict:
    """
    Check database connectivity and return health status.

    Returns:
        Dictionary with health check results
    """
    try:
        conn = get_connection(max_retries=1)
        cursor = conn.cursor()

        # Basic connectivity
        cursor.execute("SELECT 1")

        # Get database version
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]

        # Get current database
        cursor.execute("SELECT current_database()")
        db_name = cursor.fetchone()[0]

        # Get table count
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """)
        table_count = cursor.fetchone()[0]

        # Get schema version if exists
        schema_version = None
        try:
            cursor.execute("SELECT version, applied_at FROM schema_version ORDER BY id DESC LIMIT 1")
            result = cursor.fetchone()
            if result:
                schema_version = {"version": result[0], "applied_at": str(result[1])}
        except:
            pass

        cursor.close()
        conn.close()

        return {
            "status": "healthy",
            "connected": True,
            "database": db_name,
            "version": version.split(",")[0] if version else None,
            "table_count": table_count,
            "schema_version": schema_version,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "connected": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


def run_schema_migration(schema_path: Optional[str] = None) -> bool:
    """
    Execute the main schema SQL file.

    Args:
        schema_path: Path to schema.sql file

    Returns:
        True if successful, False otherwise
    """
    if schema_path is None:
        schema_path = Path(__file__).parent / "schema.sql"
    else:
        schema_path = Path(schema_path)

    if not schema_path.exists():
        console.print(f"[red]✗ Schema file not found: {schema_path}[/red]")
        return False

    console.print(f"\n[bold]Running Schema Migration[/bold]")
    console.print(f"[dim]Source: {schema_path}[/dim]\n")

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Read schema file
        with open(schema_path, "r") as f:
            schema_sql = f.read()

        # Execute schema
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Creating tables and indexes...", total=None)

            cursor.execute(schema_sql)
            conn.commit()

            progress.update(task, description="[green]Schema migration complete![/green]")

        # Count created tables
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """)
        table_count = cursor.fetchone()[0]

        console.print(f"\n[green]✓[/green] Created {table_count} tables successfully")

        # List tables
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()

        table = Table(title="Created Tables", show_header=True)
        table.add_column("#", style="dim")
        table.add_column("Table Name", style="cyan")

        for i, (name,) in enumerate(tables, 1):
            table.add_row(str(i), name)

        console.print(table)

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        console.print(f"[red]✗ Migration failed: {e}[/red]")
        return False


def run_seed_data(seed_path: Optional[str] = None) -> bool:
    """
    Execute seed data SQL file.

    Args:
        seed_path: Path to seed data SQL file

    Returns:
        True if successful, False otherwise
    """
    if seed_path is None:
        seed_path = Path(__file__).parent / "seeds" / "seed_data.sql"
    else:
        seed_path = Path(seed_path)

    if not seed_path.exists():
        console.print(f"[yellow]! Seed file not found: {seed_path}[/yellow]")
        return False

    console.print(f"\n[bold]Running Seed Data[/bold]")
    console.print(f"[dim]Source: {seed_path}[/dim]\n")

    try:
        conn = get_connection()
        cursor = conn.cursor()

        with open(seed_path, "r") as f:
            seed_sql = f.read()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Inserting seed data...", total=None)

            cursor.execute(seed_sql)
            conn.commit()

            progress.update(task, description="[green]Seed data inserted![/green]")

        console.print("[green]✓[/green] Seed data inserted successfully")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        console.print(f"[red]✗ Seed data insertion failed: {e}[/red]")
        return False


def reset_database() -> bool:
    """
    Drop all tables and reset the database.
    USE WITH CAUTION!

    Returns:
        True if successful, False otherwise
    """
    console.print("\n[bold red]⚠️  DATABASE RESET[/bold red]")
    console.print("[yellow]This will drop all tables and data![/yellow]\n")

    confirm = input("Type 'RESET' to confirm: ")
    if confirm != "RESET":
        console.print("[dim]Reset cancelled[/dim]")
        return False

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Drop all tables in public schema
        cursor.execute("""
            DO $$
            DECLARE r RECORD;
            BEGIN
                FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public')
                LOOP
                    EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                END LOOP;
            END $$;
        """)

        conn.commit()
        console.print("[green]✓[/green] All tables dropped")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        console.print(f"[red]✗ Reset failed: {e}[/red]")
        return False


def show_status():
    """Display current database status."""
    console.print("\n[bold]Database Status[/bold]\n")

    health = check_database_health()

    if health["connected"]:
        status_table = Table(show_header=False)
        status_table.add_column("Property", style="dim")
        status_table.add_column("Value", style="cyan")

        status_table.add_row("Status", f"[green]{health['status']}[/green]")
        status_table.add_row("Database", health.get("database", "N/A"))
        status_table.add_row("Version", health.get("version", "N/A"))
        status_table.add_row("Tables", str(health.get("table_count", 0)))

        if health.get("schema_version"):
            status_table.add_row(
                "Schema Version",
                f"{health['schema_version']['version']} ({health['schema_version']['applied_at']})"
            )

        console.print(status_table)
    else:
        console.print(f"[red]Status: {health['status']}[/red]")
        console.print(f"[red]Error: {health.get('error', 'Unknown')}[/red]")


def main():
    """Main CLI entry point."""
    import click

    @click.group()
    def cli():
        """Procure-Pro-ISO Database Migration Tool"""
        pass

    @cli.command()
    def status():
        """Show database status"""
        show_status()

    @cli.command()
    def health():
        """Check database health"""
        result = check_database_health()
        console.print_json(data=result)

    @cli.command()
    @click.option("--schema", "-s", help="Path to schema.sql file")
    def migrate(schema):
        """Run schema migration"""
        success = run_schema_migration(schema)
        sys.exit(0 if success else 1)

    @cli.command()
    @click.option("--seed-file", "-f", help="Path to seed data SQL file")
    def seed(seed_file):
        """Run seed data"""
        success = run_seed_data(seed_file)
        sys.exit(0 if success else 1)

    @cli.command()
    @click.option("--with-seeds", is_flag=True, help="Also run seed data")
    def setup(with_seeds):
        """Run full database setup (migrate + optional seeds)"""
        console.print("[bold]Procure-Pro-ISO Database Setup[/bold]")
        console.print("=" * 40)

        if not run_schema_migration():
            sys.exit(1)

        if with_seeds:
            if not run_seed_data():
                console.print("[yellow]Warning: Seed data not applied[/yellow]")

        show_status()
        console.print("\n[green]✓ Database setup complete![/green]")

    @cli.command()
    def reset():
        """Reset database (DROP ALL TABLES)"""
        if reset_database():
            console.print("[green]✓ Database reset complete[/green]")
        else:
            sys.exit(1)

    @cli.command()
    def test_connection():
        """Test database connection"""
        console.print("[bold]Testing Database Connection[/bold]\n")
        console.print(f"Host: {DB_CONFIG['host']}")
        console.print(f"Port: {DB_CONFIG['port']}")
        console.print(f"Database: {DB_CONFIG['database']}")
        console.print(f"User: {DB_CONFIG['user']}")
        console.print()

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]

            console.print(f"[green]✓ Connection successful![/green]")
            console.print(f"[dim]{version}[/dim]")

            cursor.close()
            conn.close()

        except Exception as e:
            console.print(f"[red]✗ Connection failed: {e}[/red]")
            sys.exit(1)

    cli()


if __name__ == "__main__":
    main()

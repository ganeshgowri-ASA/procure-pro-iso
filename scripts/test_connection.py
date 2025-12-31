#!/usr/bin/env python3
"""
Test Database Connection Script for Procure-Pro-ISO
Tests connectivity to Railway PostgreSQL database.
"""

import os
import sys
import time
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Load environment variables
load_dotenv()

console = Console()


def get_connection_info() -> dict:
    """Get database connection information from environment."""
    return {
        "DATABASE_URL": os.getenv("DATABASE_URL", "Not set"),
        "PGHOST": os.getenv("PGHOST", os.getenv("DB_HOST", "Not set")),
        "PGPORT": os.getenv("PGPORT", os.getenv("DB_PORT", "5432")),
        "PGDATABASE": os.getenv("PGDATABASE", os.getenv("DB_NAME", "Not set")),
        "PGUSER": os.getenv("PGUSER", os.getenv("DB_USER", "Not set")),
        "PGPASSWORD": "***" if os.getenv("PGPASSWORD") or os.getenv("DB_PASSWORD") else "Not set",
    }


def test_psycopg2_connection() -> tuple[bool, str, dict]:
    """Test connection using psycopg2."""
    try:
        import psycopg2

        database_url = os.getenv("DATABASE_URL")

        if database_url:
            conn = psycopg2.connect(database_url)
        else:
            conn = psycopg2.connect(
                host=os.getenv("PGHOST", os.getenv("DB_HOST", "localhost")),
                port=os.getenv("PGPORT", os.getenv("DB_PORT", "5432")),
                database=os.getenv("PGDATABASE", os.getenv("DB_NAME", "procure_pro_iso")),
                user=os.getenv("PGUSER", os.getenv("DB_USER", "postgres")),
                password=os.getenv("PGPASSWORD", os.getenv("DB_PASSWORD", "postgres")),
            )

        cursor = conn.cursor()

        # Get version
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]

        # Get database name
        cursor.execute("SELECT current_database()")
        db_name = cursor.fetchone()[0]

        # Get table count
        cursor.execute(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"
        )
        table_count = cursor.fetchone()[0]

        # Get connection info
        cursor.execute("SELECT inet_server_addr(), inet_server_port()")
        server_info = cursor.fetchone()

        cursor.close()
        conn.close()

        return True, "Connection successful", {
            "database": db_name,
            "version": version.split(",")[0] if version else "Unknown",
            "table_count": table_count,
            "server": f"{server_info[0]}:{server_info[1]}" if server_info[0] else "Unknown",
        }

    except ImportError:
        return False, "psycopg2 not installed", {}
    except Exception as e:
        return False, str(e), {}


def test_sqlalchemy_connection() -> tuple[bool, str, dict]:
    """Test connection using SQLAlchemy."""
    try:
        from sqlalchemy import create_engine, text

        database_url = os.getenv("DATABASE_URL")

        if not database_url:
            pghost = os.getenv("PGHOST", os.getenv("DB_HOST", "localhost"))
            pgport = os.getenv("PGPORT", os.getenv("DB_PORT", "5432"))
            pgdatabase = os.getenv("PGDATABASE", os.getenv("DB_NAME", "procure_pro_iso"))
            pguser = os.getenv("PGUSER", os.getenv("DB_USER", "postgres"))
            pgpassword = os.getenv("PGPASSWORD", os.getenv("DB_PASSWORD", "postgres"))
            database_url = f"postgresql://{pguser}:{pgpassword}@{pghost}:{pgport}/{pgdatabase}"

        engine = create_engine(database_url)

        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()

        return True, "SQLAlchemy connection successful", {}

    except ImportError:
        return False, "SQLAlchemy not installed", {}
    except Exception as e:
        return False, str(e), {}


def run_tests():
    """Run all connection tests."""
    console.print("\n")
    console.print(
        Panel.fit(
            "[bold blue]Procure-Pro-ISO Database Connection Test[/bold blue]",
            border_style="blue",
        )
    )

    # Display connection info
    console.print("\n[bold]Connection Configuration:[/bold]")
    conn_info = get_connection_info()

    info_table = Table(show_header=False)
    info_table.add_column("Variable", style="dim")
    info_table.add_column("Value", style="cyan")

    for key, value in conn_info.items():
        # Mask the full DATABASE_URL for security
        if key == "DATABASE_URL" and value != "Not set":
            # Show partial URL
            if "://" in value:
                parts = value.split("@")
                if len(parts) > 1:
                    value = f"postgresql://***@{parts[-1]}"
        info_table.add_row(key, value)

    console.print(info_table)

    # Run tests
    console.print("\n[bold]Running Connection Tests:[/bold]\n")

    tests = [
        ("psycopg2", test_psycopg2_connection),
        ("SQLAlchemy", test_sqlalchemy_connection),
    ]

    all_passed = True

    for name, test_func in tests:
        start_time = time.time()
        success, message, details = test_func()
        elapsed = (time.time() - start_time) * 1000

        if success:
            console.print(f"[green]✓[/green] {name}: {message} ({elapsed:.0f}ms)")
            if details:
                for key, value in details.items():
                    console.print(f"  [dim]{key}:[/dim] {value}")
        else:
            console.print(f"[red]✗[/red] {name}: {message}")
            all_passed = False

    # Summary
    console.print()
    if all_passed:
        console.print(
            Panel.fit(
                "[green]All connection tests passed![/green]\n"
                "Database is ready for migrations.",
                border_style="green",
            )
        )
        return 0
    else:
        console.print(
            Panel.fit(
                "[red]Some connection tests failed![/red]\n"
                "Check your environment variables and database status.",
                border_style="red",
            )
        )
        return 1


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Test Railway PostgreSQL connection")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    args = parser.parse_args()

    if args.json:
        import json

        success, message, details = test_psycopg2_connection()
        result = {
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
            "config": get_connection_info(),
        }
        print(json.dumps(result, indent=2))
        sys.exit(0 if success else 1)
    else:
        sys.exit(run_tests())


if __name__ == "__main__":
    main()

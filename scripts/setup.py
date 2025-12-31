#!/usr/bin/env python3
"""
Full Database Setup Script for Procure-Pro-ISO
Runs migration, seeds, and verifies the setup.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

load_dotenv()

console = Console()


def main():
    """Run full database setup."""
    console.print("\n")
    console.print(
        Panel.fit(
            "[bold blue]Procure-Pro-ISO Database Setup[/bold blue]\n"
            "[dim]ISO-compliant Procurement Lifecycle Management System[/dim]",
            border_style="blue",
        )
    )

    # Import migration runner
    from database.migration_runner import (
        run_schema_migration,
        run_seed_data,
        show_status,
        check_database_health,
    )

    # Step 1: Test connection
    console.print("\n[bold]Step 1: Testing database connection...[/bold]")
    health = check_database_health()

    if not health["connected"]:
        console.print(f"[red]✗ Cannot connect to database: {health.get('error')}[/red]")
        console.print("\n[yellow]Please check your environment variables:[/yellow]")
        console.print("  - DATABASE_URL or")
        console.print("  - PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD")
        sys.exit(1)

    console.print("[green]✓[/green] Database connection successful")

    # Step 2: Run schema migration
    console.print("\n[bold]Step 2: Running schema migration...[/bold]")
    if not run_schema_migration():
        console.print("[red]✗ Schema migration failed[/red]")
        sys.exit(1)

    # Step 3: Run seed data
    console.print("\n[bold]Step 3: Inserting seed data...[/bold]")
    if not run_seed_data():
        console.print("[yellow]! Seed data not applied (file may not exist)[/yellow]")

    # Step 4: Show final status
    console.print("\n[bold]Step 4: Verifying setup...[/bold]")
    show_status()

    # Final summary
    console.print("\n")
    console.print(
        Panel.fit(
            "[bold green]✓ Database setup complete![/bold green]\n\n"
            "You can now:\n"
            "• Start the API: [cyan]uvicorn app.main:app --reload[/cyan]\n"
            "• Check health: [cyan]curl http://localhost:8000/health[/cyan]\n"
            "• View docs: [cyan]http://localhost:8000/docs[/cyan]",
            border_style="green",
        )
    )


if __name__ == "__main__":
    main()

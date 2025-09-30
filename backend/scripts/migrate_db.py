#!/usr/bin/env python3
"""
Database migration script for HackSeek.
Handles database schema upgrades and downgrades.
"""
import os
import sys
import asyncio
import subprocess
from pathlib import Path
import logging

# Add backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.config import settings
from app.database import engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_alembic_command(command: list[str]) -> bool:
    """Run an Alembic command and return success status."""
    try:
        # Change to backend directory for alembic commands
        backend_dir = Path(__file__).parent.parent
        os.chdir(backend_dir)

        # Run alembic command
        cmd = ['alembic'] + command
        logger.info(f"Running: {' '.join(cmd)}")

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info("Command completed successfully")
            if result.stdout:
                logger.info(f"Output: {result.stdout}")
            return True
        else:
            logger.error(f"Command failed with return code {result.returncode}")
            if result.stderr:
                logger.error(f"Error: {result.stderr}")
            if result.stdout:
                logger.info(f"Output: {result.stdout}")
            return False

    except Exception as e:
        logger.error(f"Failed to run alembic command: {e}")
        return False


def check_database_connection():
    """Check if database is accessible."""
    async def test_connection():
        try:
            async with engine.begin() as conn:
                result = await conn.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False

    return asyncio.run(test_connection())


def init_migrations():
    """Initialize Alembic migrations."""
    logger.info("Initializing Alembic migrations...")
    return run_alembic_command(['init', 'migrations'])


def create_migration(message: str, autogenerate: bool = True):
    """Create a new migration."""
    logger.info(f"Creating migration: {message}")

    cmd = ['revision']
    if autogenerate:
        cmd.append('--autogenerate')
    cmd.extend(['-m', message])

    return run_alembic_command(cmd)


def upgrade_database(revision: str = 'head'):
    """Upgrade database to a specific revision."""
    logger.info(f"Upgrading database to revision: {revision}")
    return run_alembic_command(['upgrade', revision])


def downgrade_database(revision: str):
    """Downgrade database to a specific revision."""
    logger.warning(f"Downgrading database to revision: {revision}")
    return run_alembic_command(['downgrade', revision])


def show_current_revision():
    """Show current database revision."""
    logger.info("Showing current database revision:")
    return run_alembic_command(['current'])


def show_migration_history():
    """Show migration history."""
    logger.info("Showing migration history:")
    return run_alembic_command(['history'])


def show_pending_migrations():
    """Show pending migrations."""
    logger.info("Checking for pending migrations:")
    return run_alembic_command(['check'])


def stamp_database(revision: str):
    """Stamp database with a specific revision without running migrations."""
    logger.info(f"Stamping database with revision: {revision}")
    return run_alembic_command(['stamp', revision])


def main():
    """Main function with command line interface."""
    import argparse

    parser = argparse.ArgumentParser(description="HackSeek Database Migration Tool")
    subparsers = parser.add_subparsers(dest='command', help='Migration commands')

    # Check connection
    subparsers.add_parser('check-connection', help='Check database connection')

    # Init command
    subparsers.add_parser('init', help='Initialize Alembic migrations')

    # Create migration command
    create_parser = subparsers.add_parser('create', help='Create a new migration')
    create_parser.add_argument('message', help='Migration message')
    create_parser.add_argument('--no-autogenerate', action='store_true',
                              help='Do not auto-generate migration')

    # Upgrade command
    upgrade_parser = subparsers.add_parser('upgrade', help='Upgrade database')
    upgrade_parser.add_argument('revision', nargs='?', default='head',
                               help='Target revision (default: head)')

    # Downgrade command
    downgrade_parser = subparsers.add_parser('downgrade', help='Downgrade database')
    downgrade_parser.add_argument('revision', help='Target revision')

    # Status commands
    subparsers.add_parser('current', help='Show current revision')
    subparsers.add_parser('history', help='Show migration history')
    subparsers.add_parser('pending', help='Show pending migrations')

    # Stamp command
    stamp_parser = subparsers.add_parser('stamp', help='Stamp database with revision')
    stamp_parser.add_argument('revision', help='Revision to stamp')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Check database connection first
    if args.command != 'init' and args.command != 'check-connection':
        logger.info("Checking database connection...")
        if not check_database_connection():
            logger.error("Cannot connect to database. Check your configuration.")
            sys.exit(1)

    # Execute command
    success = True

    if args.command == 'check-connection':
        success = check_database_connection()
        if success:
            logger.info("Database connection successful")

    elif args.command == 'init':
        success = init_migrations()

    elif args.command == 'create':
        autogenerate = not args.no_autogenerate
        success = create_migration(args.message, autogenerate)

    elif args.command == 'upgrade':
        success = upgrade_database(args.revision)

    elif args.command == 'downgrade':
        success = downgrade_database(args.revision)

    elif args.command == 'current':
        success = show_current_revision()

    elif args.command == 'history':
        success = show_migration_history()

    elif args.command == 'pending':
        success = show_pending_migrations()

    elif args.command == 'stamp':
        success = stamp_database(args.revision)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
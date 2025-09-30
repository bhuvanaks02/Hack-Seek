#!/usr/bin/env python3
"""
Database backup script for HackSeek production database.
Creates timestamped backups with compression and rotation.
"""
import os
import sys
import asyncio
import subprocess
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Add backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Backup configuration
BACKUP_DIR = Path("/var/backups/hackseek")
MAX_BACKUPS = 30  # Keep 30 days of backups
COMPRESSION_LEVEL = 6


def ensure_backup_directory():
    """Ensure backup directory exists."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Backup directory: {BACKUP_DIR}")


def get_database_config():
    """Extract database configuration from settings."""
    # Parse DATABASE_URL
    db_url = settings.database_url

    # Simple URL parsing for postgresql+asyncpg://user:password@host:port/database
    if "postgresql+asyncpg://" in db_url:
        db_url = db_url.replace("postgresql+asyncpg://", "")
    elif "postgresql://" in db_url:
        db_url = db_url.replace("postgresql://", "")

    # Extract components
    if "@" in db_url:
        auth, host_db = db_url.split("@", 1)
        username, password = auth.split(":", 1)

        if "/" in host_db:
            host_port, database = host_db.split("/", 1)
        else:
            host_port, database = host_db, "hackseek_db"

        if ":" in host_port:
            host, port = host_port.split(":", 1)
        else:
            host, port = host_port, "5432"
    else:
        # Fallback to environment variables
        host = os.getenv("DATABASE_HOST", "localhost")
        port = os.getenv("DATABASE_PORT", "5432")
        database = os.getenv("DATABASE_NAME", "hackseek_db")
        username = os.getenv("DATABASE_USER", "hackseek_user")
        password = os.getenv("DATABASE_PASSWORD", "password")

    return {
        "host": host,
        "port": port,
        "database": database,
        "username": username,
        "password": password
    }


def create_backup():
    """Create a database backup using pg_dump."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"hackseek_backup_{timestamp}.sql"
    backup_path = BACKUP_DIR / backup_filename
    compressed_path = BACKUP_DIR / f"{backup_filename}.gz"

    try:
        # Get database configuration
        db_config = get_database_config()
        logger.info(f"Creating backup for database: {db_config['database']}")

        # Set environment variables for pg_dump
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config['password']

        # Run pg_dump
        cmd = [
            'pg_dump',
            '-h', db_config['host'],
            '-p', db_config['port'],
            '-U', db_config['username'],
            '-d', db_config['database'],
            '--verbose',
            '--no-password',
            '--format=custom',
            '--compress=0',  # We'll compress manually
            '-f', str(backup_path)
        ]

        logger.info(f"Running: {' '.join(cmd[:-2])} -f {backup_path}")
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"pg_dump failed: {result.stderr}")
            return False

        # Compress the backup
        logger.info(f"Compressing backup to {compressed_path}")
        with open(backup_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb', compresslevel=COMPRESSION_LEVEL) as f_out:
                shutil.copyfileobj(f_in, f_out)

        # Remove uncompressed file
        backup_path.unlink()

        # Log backup size
        size_mb = compressed_path.stat().st_size / (1024 * 1024)
        logger.info(f"Backup created successfully: {compressed_path} ({size_mb:.2f} MB)")

        return True

    except Exception as e:
        logger.error(f"Backup failed: {e}")
        return False


def cleanup_old_backups():
    """Remove backups older than MAX_BACKUPS days."""
    try:
        cutoff_date = datetime.now() - timedelta(days=MAX_BACKUPS)
        removed_count = 0

        for backup_file in BACKUP_DIR.glob("hackseek_backup_*.sql.gz"):
            file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)

            if file_time < cutoff_date:
                logger.info(f"Removing old backup: {backup_file}")
                backup_file.unlink()
                removed_count += 1

        if removed_count > 0:
            logger.info(f"Removed {removed_count} old backup(s)")
        else:
            logger.info("No old backups to remove")

    except Exception as e:
        logger.error(f"Cleanup failed: {e}")


def list_backups():
    """List all available backups."""
    backups = sorted(BACKUP_DIR.glob("hackseek_backup_*.sql.gz"))

    if not backups:
        logger.info("No backups found")
        return

    logger.info(f"Found {len(backups)} backup(s):")
    for backup in backups:
        size_mb = backup.stat().st_size / (1024 * 1024)
        mtime = datetime.fromtimestamp(backup.stat().st_mtime)
        logger.info(f"  {backup.name} - {size_mb:.2f} MB - {mtime}")


def restore_backup(backup_filename: str):
    """Restore database from a backup file."""
    backup_path = BACKUP_DIR / backup_filename

    if not backup_path.exists():
        logger.error(f"Backup file not found: {backup_path}")
        return False

    try:
        db_config = get_database_config()
        logger.warning(f"Restoring database: {db_config['database']}")
        logger.warning("This will OVERWRITE the current database!")

        # Decompress backup if needed
        if backup_filename.endswith('.gz'):
            temp_sql = BACKUP_DIR / f"temp_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
            logger.info(f"Decompressing {backup_path} to {temp_sql}")

            with gzip.open(backup_path, 'rb') as f_in:
                with open(temp_sql, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            restore_file = temp_sql
        else:
            restore_file = backup_path

        # Set environment variables for pg_restore
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config['password']

        # Run pg_restore
        cmd = [
            'pg_restore',
            '-h', db_config['host'],
            '-p', db_config['port'],
            '-U', db_config['username'],
            '-d', db_config['database'],
            '--verbose',
            '--no-password',
            '--clean',
            '--if-exists',
            str(restore_file)
        ]

        logger.info(f"Running pg_restore...")
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)

        # Clean up temporary file
        if backup_filename.endswith('.gz') and temp_sql.exists():
            temp_sql.unlink()

        if result.returncode != 0:
            logger.error(f"pg_restore failed: {result.stderr}")
            return False

        logger.info("Database restored successfully")
        return True

    except Exception as e:
        logger.error(f"Restore failed: {e}")
        return False


def main():
    """Main function with command line interface."""
    import argparse

    parser = argparse.ArgumentParser(description="HackSeek Database Backup Tool")
    parser.add_argument('action', choices=['backup', 'list', 'restore', 'cleanup'],
                        help='Action to perform')
    parser.add_argument('--file', help='Backup file name for restore action')

    args = parser.parse_args()

    ensure_backup_directory()

    if args.action == 'backup':
        success = create_backup()
        if success:
            cleanup_old_backups()
        sys.exit(0 if success else 1)

    elif args.action == 'list':
        list_backups()

    elif args.action == 'restore':
        if not args.file:
            logger.error("--file argument required for restore action")
            sys.exit(1)
        success = restore_backup(args.file)
        sys.exit(0 if success else 1)

    elif args.action == 'cleanup':
        cleanup_old_backups()


if __name__ == "__main__":
    main()
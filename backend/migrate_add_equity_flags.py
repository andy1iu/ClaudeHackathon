"""
Database migration script to add equity_and_context_flags column to briefings table.

This script safely adds the new column to existing databases.
Run this before starting the server after updating the code.

Usage:
    python migrate_add_equity_flags.py
"""

from sqlalchemy import create_engine, text, inspect
from app.core.config import settings
import sys


def migrate():
    """Add equity_and_context_flags column to briefings table if it doesn't exist."""

    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)

        # Check if column already exists
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('briefings')]

        if 'equity_and_context_flags' in columns:
            print("✓ Column 'equity_and_context_flags' already exists. No migration needed.")
            return True

        print("Adding 'equity_and_context_flags' column to briefings table...")

        # Add the column
        with engine.connect() as connection:
            # Start a transaction
            with connection.begin():
                # Add column as nullable JSON with default empty array
                connection.execute(text(
                    "ALTER TABLE briefings ADD COLUMN equity_and_context_flags JSON DEFAULT '[]'::json"
                ))

        print("✓ Successfully added 'equity_and_context_flags' column!")
        print("✓ Migration complete!")
        return True

    except Exception as e:
        print(f"✗ Migration failed: {str(e)}", file=sys.stderr)
        return False


if __name__ == "__main__":
    success = migrate()
    sys.exit(0 if success else 1)

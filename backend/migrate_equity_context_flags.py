#!/usr/bin/env python3
"""
Migration script to add equity_and_context_flags column to the briefings table.
This adds support for health equity insights in clinical briefings.
"""
import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import Column, JSON, text
from sqlalchemy.orm import Session
from app.db.database import engine
from app.models.patient import Base


def migrate():
    """Add equity_and_context_flags column to briefings table"""
    
    print("🔄 Starting migration: Adding equity_and_context_flags column...")
    print()
    
    try:
        # Check if column already exists
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='briefings' 
                AND column_name='equity_and_context_flags'
            """))
            
            if result.fetchone():
                print("✅ Column 'equity_and_context_flags' already exists. No migration needed.")
                return
        
        print("📝 Adding 'equity_and_context_flags' column to briefings table...")
        
        # Add the new column
        with engine.connect() as conn:
            conn.execute(text("""
                ALTER TABLE briefings 
                ADD COLUMN equity_and_context_flags JSON
            """))
            conn.commit()
        
        print("✅ Successfully added equity_and_context_flags column")
        print()
        print("🎉 Migration complete!")
        print()
        print("📊 The briefings table now supports:")
        print("   • Clinical insights (key_insights_flags)")
        print("   • Health equity insights (equity_and_context_flags)")
        print("   • Structured symptoms")
        print("   • Relevant history")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        raise


if __name__ == "__main__":
    migrate()


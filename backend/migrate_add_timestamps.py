#!/usr/bin/env python3
"""
Migration script to add created_at and updated_at timestamp columns to all tables.
This follows Google L7 best practices for database timestamps:
- UTC timezone-aware timestamps
- Automatic defaults via server_default
- Auto-updating updated_at via triggers
- Indexed columns for query performance
"""
import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import text
from app.db.database import engine


def migrate():
    """Add created_at and updated_at columns to all tables"""
    
    print("🔄 Starting migration: Adding timestamp columns to all tables...")
    print()
    
    # Define tables and their timestamp columns
    tables = [
        ("patients", ["created_at", "updated_at"]),
        ("ehr_histories", ["created_at", "updated_at"]),
        ("patient_narratives", ["created_at", "updated_at"]),
        ("chat_conversations", ["updated_at"]),  # created_at already exists
        ("briefings", ["updated_at"]),  # created_at already exists
    ]
    
    try:
        with engine.connect() as conn:
            for table_name, columns in tables:
                print(f"📝 Processing table: {table_name}")
                
                for column_name in columns:
                    # Check if column already exists
                    result = conn.execute(text(f"""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name='{table_name}' 
                        AND column_name='{column_name}'
                    """))
                    
                    if result.fetchone():
                        print(f"   ✅ Column '{column_name}' already exists. Skipping.")
                        continue
                    
                    # Determine column type and default
                    if column_name == "created_at":
                        # Add created_at with default NOW()
                        conn.execute(text(f"""
                            ALTER TABLE {table_name} 
                            ADD COLUMN {column_name} TIMESTAMP WITH TIME ZONE 
                            NOT NULL DEFAULT NOW()
                        """))
                        # Create index
                        conn.execute(text(f"""
                            CREATE INDEX IF NOT EXISTS idx_{table_name}_{column_name} 
                            ON {table_name}({column_name})
                        """))
                        print(f"   ✅ Added '{column_name}' column with index")
                    
                    elif column_name == "updated_at":
                        # Add updated_at with default NOW()
                        conn.execute(text(f"""
                            ALTER TABLE {table_name} 
                            ADD COLUMN {column_name} TIMESTAMP WITH TIME ZONE 
                            NOT NULL DEFAULT NOW()
                        """))
                        # Create index
                        conn.execute(text(f"""
                            CREATE INDEX IF NOT EXISTS idx_{table_name}_{column_name} 
                            ON {table_name}({column_name})
                        """))
                        # Create trigger function for auto-updating updated_at
                        conn.execute(text(f"""
                            CREATE OR REPLACE FUNCTION update_{table_name}_updated_at()
                            RETURNS TRIGGER AS $$
                            BEGIN
                                NEW.{column_name} = NOW();
                                RETURN NEW;
                            END;
                            $$ LANGUAGE plpgsql;
                        """))
                        # Create trigger
                        conn.execute(text(f"""
                            DROP TRIGGER IF EXISTS trigger_update_{table_name}_updated_at ON {table_name};
                            CREATE TRIGGER trigger_update_{table_name}_updated_at
                            BEFORE UPDATE ON {table_name}
                            FOR EACH ROW
                            EXECUTE FUNCTION update_{table_name}_updated_at();
                        """))
                        print(f"   ✅ Added '{column_name}' column with index and auto-update trigger")
                
                print()
            
            # Commit all changes
            conn.commit()
        
        print("🎉 Migration complete!")
        print()
        print("📊 All tables now have:")
        print("   • created_at: UTC timestamp with timezone, indexed")
        print("   • updated_at: UTC timestamp with timezone, indexed, auto-updating")
        print()
        print("✨ Timestamps follow Google L7 best practices:")
        print("   • Timezone-aware (UTC)")
        print("   • Database-level defaults (server_default)")
        print("   • Automatic updated_at via triggers")
        print("   • Indexed for query performance")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    migrate()


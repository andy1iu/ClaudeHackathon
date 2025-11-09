#!/usr/bin/env python3
"""
Migration script to create the appointments table.
This adds support for appointment/meeting scheduling with date/time tracking.
"""
import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import text
from app.db.database import engine


def migrate():
    """Create appointments table if it doesn't exist"""
    
    print("🔄 Starting migration: Creating appointments table...")
    print()
    
    try:
        with engine.connect() as conn:
            # Check if table already exists
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name='appointments'
            """))
            
            if result.fetchone():
                print("✅ Table 'appointments' already exists. Skipping creation.")
                return
            
            print("📝 Creating 'appointments' table...")
            
            # Create appointments table
            conn.execute(text("""
                CREATE TABLE appointments (
                    appointment_id VARCHAR NOT NULL PRIMARY KEY,
                    patient_id VARCHAR NOT NULL,
                    appointment_date_time TIMESTAMP WITH TIME ZONE NOT NULL,
                    appointment_status VARCHAR NOT NULL DEFAULT 'scheduled',
                    appointment_type VARCHAR,
                    duration_minutes INTEGER DEFAULT 30,
                    location VARCHAR,
                    provider_name VARCHAR,
                    notes TEXT,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    CONSTRAINT fk_appointments_patient 
                        FOREIGN KEY (patient_id) 
                        REFERENCES patients(patient_id)
                )
            """))
            
            # Create indexes
            print("📊 Creating indexes...")
            conn.execute(text("""
                CREATE INDEX idx_appointments_appointment_id ON appointments(appointment_id)
            """))
            conn.execute(text("""
                CREATE INDEX idx_appointments_patient_id ON appointments(patient_id)
            """))
            conn.execute(text("""
                CREATE INDEX idx_appointments_date_time ON appointments(appointment_date_time)
            """))
            conn.execute(text("""
                CREATE INDEX idx_appointments_status ON appointments(appointment_status)
            """))
            conn.execute(text("""
                CREATE INDEX idx_appointments_created_at ON appointments(created_at)
            """))
            conn.execute(text("""
                CREATE INDEX idx_appointments_updated_at ON appointments(updated_at)
            """))
            
            # Create trigger function for auto-updating updated_at
            print("⚙️  Creating auto-update trigger...")
            conn.execute(text("""
                CREATE OR REPLACE FUNCTION update_appointments_updated_at()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = NOW();
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
            """))
            
            # Create trigger
            conn.execute(text("""
                DROP TRIGGER IF EXISTS trigger_update_appointments_updated_at ON appointments;
                CREATE TRIGGER trigger_update_appointments_updated_at
                BEFORE UPDATE ON appointments
                FOR EACH ROW
                EXECUTE FUNCTION update_appointments_updated_at();
            """))
            
            # Commit all changes
            conn.commit()
        
        print()
        print("🎉 Migration complete!")
        print()
        print("📊 The appointments table now supports:")
        print("   • Appointment date/time (timezone-aware)")
        print("   • Appointment status (scheduled, completed, cancelled, etc.)")
        print("   • Appointment type (initial, follow-up, consultation, etc.)")
        print("   • Duration, location, provider, and notes")
        print("   • Automatic timestamps (created_at, updated_at)")
        print("   • Indexed columns for query performance")
        print("   • Auto-updating updated_at via trigger")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    migrate()


#!/usr/bin/env python3
"""
Seed script to populate the database with synthetic patient data.
Run this script to initialize the database with test data.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.db.database import engine, Base
from app.models.patient import Patient, EHRHistory, PatientNarrative
import uuid


def load_json_file(filepath: str):
    """Load data from a JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)


def seed_database():
    """Main function to seed the database"""

    print("🌱 Starting database seed...")

    # Create all tables
    print("📦 Creating database tables...")
    Base.metadata.drop_all(bind=engine)  # Drop existing tables
    Base.metadata.create_all(bind=engine)  # Create fresh tables
    print("✅ Tables created")

    # Create a session
    db = Session(engine)

    try:
        # Load data files
        data_dir = Path(__file__).parent / "data"
        print(f"📂 Loading data from {data_dir}...")

        patients_data = load_json_file(data_dir / "patients.json")
        ehr_data = load_json_file(data_dir / "ehr.json")
        narratives_data = load_json_file(data_dir / "narratives.json")

        print(f"   - {len(patients_data)} patients")
        print(f"   - {len(ehr_data)} EHR records")
        print(f"   - {len(narratives_data)} narratives")

        # Insert patients
        print("\n👤 Inserting patients...")
        for patient_data in patients_data:
            patient = Patient(
                patient_id=patient_data["patient_id"],
                full_name=patient_data["full_name"],
                date_of_birth=datetime.strptime(patient_data["date_of_birth"], "%Y-%m-%d").date(),
                gender_identity=patient_data["gender_identity"],
                race=patient_data["race"],
                address_zip_code=patient_data["address_zip_code"]
            )
            db.add(patient)
        db.commit()
        print(f"✅ Inserted {len(patients_data)} patients")

        # Insert EHR histories
        print("\n🏥 Inserting EHR histories...")
        for ehr_record in ehr_data:
            ehr = EHRHistory(
                id=f"EHR-{uuid.uuid4().hex[:8].upper()}",
                patient_id=ehr_record["patient_id"],
                problem_list=ehr_record["problem_list"],
                medication_list=ehr_record["medication_list"],
                recent_labs=ehr_record["recent_labs"],
                surgical_history=ehr_record.get("surgical_history"),
                allergies=ehr_record.get("allergies"),
                social_history=ehr_record.get("social_history"),
                family_history=ehr_record.get("family_history"),
                vital_signs=ehr_record.get("vital_signs")
            )
            db.add(ehr)
        db.commit()
        print(f"✅ Inserted {len(ehr_data)} EHR records")

        # Insert narratives
        print("\n📝 Inserting patient narratives...")
        for narrative_data in narratives_data:
            narrative = PatientNarrative(
                narrative_id=narrative_data["narrative_id"],
                patient_id=narrative_data["patient_id"],
                narrative_title=narrative_data["narrative_title"],
                narrative_text=narrative_data["narrative_text"]
            )
            db.add(narrative)
        db.commit()
        print(f"✅ Inserted {len(narratives_data)} narratives")

        print("\n" + "="*50)
        print("🎉 Database seeding completed successfully!")
        print("="*50)
        print("\n📊 Summary:")
        print(f"   • {len(patients_data)} patients loaded")
        print(f"   • {len(ehr_data)} EHR histories loaded")
        print(f"   • {len(narratives_data)} narratives loaded")
        print("\n🚀 You can now start the API server!")

    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

#!/usr/bin/env python3
"""
Generate enhanced EHR data with comprehensive medical histories
Similar to the sample medical history format provided
"""

import json
import random
from datetime import datetime, timedelta

# Sample data pools
SURGICAL_PROCEDURES = [
    {"procedure": "Appendectomy", "indication": "Acute appendicitis"},
    {"procedure": "Cholecystectomy", "indication": "Cholelithiasis"},
    {"procedure": "Total hip replacement", "indication": "Severe osteoarthritis"},
    {"procedure": "Knee arthroscopy", "indication": "Meniscal tear"},
    {"procedure": "Hysterectomy", "indication": "Uterine fibroids"},
    {"procedure": "Cesarean section", "indication": "Obstetric delivery"},
    {"procedure": "Cataract surgery", "indication": "Visual impairment"},
    {"procedure": "Hernia repair", "indication": "Inguinal hernia"},
    {"procedure": "Tonsillectomy", "indication": "Recurrent tonsillitis"},
    {"procedure": "Coronary artery bypass", "indication": "Coronary artery disease"},
]

ALLERGIES = [
    {"allergen": "Penicillin", "reaction": "Rash and hives", "severity": "Moderate"},
    {"allergen": "Sulfa drugs", "reaction": "Stevens-Johnson syndrome", "severity": "Severe"},
    {"allergen": "Latex", "reaction": "Contact dermatitis", "severity": "Mild"},
    {"allergen": "Shellfish", "reaction": "Anaphylaxis", "severity": "Severe"},
    {"allergen": "Codeine", "reaction": "Nausea and vomiting", "severity": "Mild"},
    {"allergen": "Iodine contrast", "reaction": "Urticaria", "severity": "Moderate"},
    {"allergen": "Aspirin", "reaction": "Bronchospasm", "severity": "Moderate"},
]

TOBACCO_OPTIONS = ["Never smoker", "Former smoker (quit 5 years ago, 10 pack-year history)", "Current smoker (half pack per day)", "Current smoker (1 pack per day, 20 pack-year history)"]
ALCOHOL_OPTIONS = ["None", "Occasional (1-2 drinks per week)", "Moderate (3-7 drinks per week)", "Social drinker (2-3 drinks per week)"]
OCCUPATIONS = ["Teacher", "Software Engineer", "Nurse", "Retired", "Construction Worker", "Accountant", "Sales Manager", "Chef", "Mechanic", "Lawyer"]
LIVING_SITUATIONS = ["Lives alone", "Lives with spouse", "Lives with family", "Lives in assisted living"]

def generate_family_history():
    """Generate realistic family history"""
    histories = []

    # Mother
    mother_alive = random.choice([True, False])
    mother = {
        "relation": "Mother",
        "age": str(random.randint(65, 85)) if mother_alive else "deceased",
        "conditions": []
    }
    if mother_alive:
        mother["conditions"] = random.sample(["Hypertension", "Type 2 Diabetes", "Osteoporosis", "Hyperlipidemia"], k=random.randint(0, 2))
    else:
        mother["age_at_death"] = random.randint(55, 80)
        mother["cause_of_death"] = random.choice(["Heart attack", "Stroke", "Cancer", "Natural causes"])
        mother["conditions"] = random.sample(["Hypertension", "Breast cancer", "Alzheimer's disease"], k=random.randint(1, 2))
    histories.append(mother)

    # Father
    father_alive = random.choice([True, False])
    father = {
        "relation": "Father",
        "age": str(random.randint(65, 88)) if father_alive else "deceased",
        "conditions": []
    }
    if father_alive:
        father["conditions"] = random.sample(["Hypertension", "Coronary artery disease", "Type 2 Diabetes"], k=random.randint(0, 2))
    else:
        father["age_at_death"] = random.randint(50, 75)
        father["cause_of_death"] = random.choice(["Heart attack", "Stroke", "Cancer", "Pneumonia"])
        father["conditions"] = random.sample(["Hypertension", "Coronary artery disease", "Prostate cancer"], k=random.randint(1, 2))
    histories.append(father)

    # Siblings (0-3)
    num_siblings = random.randint(0, 3)
    for i in range(num_siblings):
        sibling = {
            "relation": random.choice(["Brother", "Sister"]),
            "age": str(random.randint(30, 70)),
            "conditions": random.sample(["Asthma", "Depression", "Hypertension", "Diabetes"], k=random.randint(0, 2))
        }
        histories.append(sibling)

    return histories

def generate_vital_signs():
    """Generate realistic vital signs"""
    return {
        "bp_systolic": random.randint(110, 150),
        "bp_diastolic": random.randint(70, 95),
        "heart_rate": random.randint(60, 90),
        "respiratory_rate": random.randint(12, 20),
        "temperature": round(random.uniform(97.5, 98.8), 1),
        "date": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
    }

def enhance_ehr_record(record):
    """Add comprehensive medical history to an EHR record"""

    # Update medication_list format
    if record.get("medication_list"):
        enhanced_meds = []
        for med in record["medication_list"]:
            # Parse existing format like "Metformin 500mg"
            parts = med.split()
            name = parts[0] if parts else med
            dosage = parts[1] if len(parts) > 1 else None

            enhanced_meds.append({
                "name": name,
                "dosage": dosage,
                "frequency": random.choice(["Daily", "Twice daily", "Three times daily", "As needed", "Weekly"])
            })
        record["medication_list"] = enhanced_meds

    # Update problem_list to include date_diagnosed
    if record.get("problem_list"):
        for problem in record["problem_list"]:
            years_ago = random.randint(1, 15)
            problem["date_diagnosed"] = (datetime.now() - timedelta(days=years_ago*365)).strftime("%Y-%m-%d")

    # Update recent_labs to include units
    if record.get("recent_labs"):
        for lab in record["recent_labs"]:
            if "A1c" in lab["test"]:
                lab["unit"] = "%"
            elif "Blood Pressure" in lab["test"]:
                lab["unit"] = "mmHg"
            elif "Peak Flow" in lab["test"]:
                lab["unit"] = "L/min"
            elif "TSH" in lab["test"]:
                lab["unit"] = "mIU/L"
            elif "Glucose" in lab["test"]:
                lab["unit"] = "mg/dL"
            elif "LDL" in lab["test"] or "HDL" in lab["test"]:
                lab["unit"] = "mg/dL"
            else:
                lab["unit"] = ""

    # Add surgical history (30% chance of having surgeries)
    if random.random() < 0.7:
        num_surgeries = random.randint(1, 3)
        record["surgical_history"] = []
        current_year = datetime.now().year
        for _ in range(num_surgeries):
            surgery = random.choice(SURGICAL_PROCEDURES).copy()
            surgery["year"] = random.randint(current_year - 30, current_year - 1)
            record["surgical_history"].append(surgery)
        record["surgical_history"].sort(key=lambda x: x["year"], reverse=True)

    # Add allergies (40% chance)
    if random.random() < 0.4:
        num_allergies = random.randint(1, 2)
        record["allergies"] = random.sample(ALLERGIES, k=num_allergies)
    else:
        record["allergies"] = [{"allergen": "No known drug allergies", "reaction": "None", "severity": "None"}]

    # Add social history
    record["social_history"] = {
        "tobacco": random.choice(TOBACCO_OPTIONS),
        "alcohol": random.choice(ALCOHOL_OPTIONS),
        "occupation": random.choice(OCCUPATIONS),
        "living_situation": random.choice(LIVING_SITUATIONS)
    }

    # Add family history
    record["family_history"] = generate_family_history()

    # Add vital signs
    record["vital_signs"] = generate_vital_signs()

    return record

def main():
    # Load existing EHR data
    with open("data/ehr.json", "r") as f:
        ehr_data = json.load(f)

    print(f"Enhancing {len(ehr_data)} EHR records...")

    # Enhance each record
    enhanced_data = []
    for record in ehr_data:
        enhanced_record = enhance_ehr_record(record)
        enhanced_data.append(enhanced_record)

    # Save enhanced data
    with open("data/ehr.json", "w") as f:
        json.dump(enhanced_data, f, indent=2)

    print(f"✅ Successfully enhanced {len(enhanced_data)} EHR records!")
    print("Sample enhanced record:")
    print(json.dumps(enhanced_data[0], indent=2))

if __name__ == "__main__":
    main()

import json
from utils.db import SessionLocal, User, EmergencyContact, Patient, HealthRecord
from utils.auth_utils import AuthManager
from utils.health_data import HealthDataManager
from datetime import datetime

def migrate_users():
    """Migrate users from JSON to database"""
    auth_manager = AuthManager()
    # This will ensure default users are created, so no need to migrate existing JSON users separately
    print("Default users ensured in database.")

def migrate_patients_and_records():
    """Migrate patients and health records from JSON files to database"""
    db = SessionLocal()
    try:
        with open("data/patients.json", "r") as f:
            patients_data = json.load(f)
    except FileNotFoundError:
        patients_data = {}

    try:
        with open("data/health_records.json", "r") as f:
            health_records_data = json.load(f)
    except FileNotFoundError:
        health_records_data = {}

    for patient_id, patient_data in patients_data.items():
        existing_patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
        if not existing_patient:
            patient = Patient(
                patient_id=patient_id,
                data=json.dumps(patient_data),
                created_at=datetime.utcnow(),
                last_updated=datetime.utcnow()
            )
            db.add(patient)
            db.commit()
            db.refresh(patient)
            # Migrate health records for this patient
            records = health_records_data.get(patient_id, [])
            for record in records:
                hr = HealthRecord(
                    patient_id=patient.id,
                    record_type=record.get("type", "unknown"),
                    data=json.dumps(record.get("data", {})),
                    timestamp=datetime.fromisoformat(record.get("timestamp")) if record.get("timestamp") else datetime.utcnow()
                )
                db.add(hr)
            db.commit()
    print("Patients and health records migration completed.")

def migrate_all():
    migrate_users()
    migrate_patients_and_records()

if __name__ == "__main__":
    migrate_all()

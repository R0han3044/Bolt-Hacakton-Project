
import json
from datetime import datetime
from utils.db import SessionLocal, Patient, HealthRecord
from sqlalchemy.orm import Session

class HealthDataManager:
    def __init__(self):
        self.db: Session = SessionLocal()

    def add_patient(self, patient_id, patient_data):
        """Add a new patient"""
        existing_patient = self.db.query(Patient).filter(Patient.patient_id == patient_id).first()
        if existing_patient:
            return False
        patient = Patient(
            patient_id=patient_id,
            data=json.dumps(patient_data),
            created_at=datetime.utcnow(),
            last_updated=datetime.utcnow()
        )
        self.db.add(patient)
        self.db.commit()
        self.db.refresh(patient)
        return True

    def get_patient(self, patient_id):
        """Get patient by ID"""
        patient = self.db.query(Patient).filter(Patient.patient_id == patient_id).first()
        if patient:
            return json.loads(patient.data)
        return None

    def get_all_patients(self):
        """Get all patients"""
        patients = self.db.query(Patient).all()
        return [json.loads(p.data) for p in patients]

    def update_patient(self, patient_id, updates):
        """Update patient information"""
        patient = self.db.query(Patient).filter(Patient.patient_id == patient_id).first()
        if not patient:
            return False
        data = json.loads(patient.data)
        data.update(updates)
        patient.data = json.dumps(data)
        patient.last_updated = datetime.utcnow()
        self.db.commit()
        return True

    def add_health_record(self, patient_id, record_type, data):
        """Add health record for patient"""
        patient = self.db.query(Patient).filter(Patient.patient_id == patient_id).first()
        if not patient:
            return None
        record = HealthRecord(
            patient_id=patient.id,
            record_type=record_type,
            data=json.dumps(data),
            timestamp=datetime.utcnow()
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record.id

    def get_health_records(self, patient_id, record_type=None, limit=None):
        """Get health records for patient"""
        patient = self.db.query(Patient).filter(Patient.patient_id == patient_id).first()
        if not patient:
            return []
        query = self.db.query(HealthRecord).filter(HealthRecord.patient_id == patient.id)
        if record_type:
            query = query.filter(HealthRecord.record_type == record_type)
        query = query.order_by(HealthRecord.timestamp.desc())
        if limit:
            query = query.limit(limit)
        records = query.all()
        return [ {"type": r.record_type, "data": json.loads(r.data), "timestamp": r.timestamp.isoformat(), "id": r.id} for r in records]

    def get_vital_signs(self, patient_id, days=30):
        """Get recent vital signs for patient"""
        return self.get_health_records(patient_id, "vital_signs", limit=days)

    def get_symptoms_history(self, patient_id, days=30):
        """Get recent symptoms for patient"""
        return self.get_health_records(patient_id, "symptoms", limit=days)

    def calculate_health_score(self, patient_id):
        """Calculate overall health score based on recent data"""
        vital_signs = self.get_vital_signs(patient_id, 7)
        symptoms = self.get_symptoms_history(patient_id, 7)

        score = 100

        for record in vital_signs:
            data = record["data"]
            if "blood_pressure_systolic" in data:
                systolic = data["blood_pressure_systolic"]
                if systolic > 140 or systolic < 90:
                    score -= 10

            if "heart_rate" in data:
                hr = data["heart_rate"]
                if hr > 100 or hr < 60:
                    score -= 5

            if "temperature" in data:
                temp = data["temperature"]
                if temp > 38 or temp < 36:
                    score -= 10

        for record in symptoms:
            severity = record["data"].get("severity", "mild")
            if severity == "severe":
                score -= 20
            elif severity == "moderate":
                score -= 10
            elif severity == "mild":
                score -= 5

        return max(0, score)

    def generate_wellness_insights(self, patient_id):
        """Generate wellness insights for patient"""
        health_score = self.calculate_health_score(patient_id)
        vital_signs = self.get_vital_signs(patient_id, 30)
        symptoms = self.get_symptoms_history(patient_id, 30)

        insights = []

        if health_score >= 90:
            insights.append({
                "type": "positive",
                "title": "Excellent Health",
                "message": "Your health metrics are looking great! Keep up the good work."
            })
        elif health_score >= 70:
            insights.append({
                "type": "warning",
                "title": "Good Health with Room for Improvement",
                "message": "Your health is generally good, but there are some areas to monitor."
            })
        else:
            insights.append({
                "type": "danger",
                "title": "Health Concerns Detected",
                "message": "Several health metrics need attention. Consider consulting a healthcare provider."
            })

        if len(vital_signs) >= 3:
            recent_bp = [r["data"].get("blood_pressure_systolic", 120) for r in vital_signs[:3]]
            if all(bp > 140 for bp in recent_bp):
                insights.append({
                    "type": "danger",
                    "title": "High Blood Pressure Pattern",
                    "message": "Your blood pressure has been consistently high. Please consult a doctor."
                })

        if len(symptoms) >= 3:
            severe_symptoms = [s for s in symptoms if s["data"].get("severity") == "severe"]
            if len(severe_symptoms) >= 2:
                insights.append({
                    "type": "danger",
                    "title": "Recurring Severe Symptoms",
                    "message": "You've reported multiple severe symptoms recently. Medical attention is recommended."
                })

        return insights

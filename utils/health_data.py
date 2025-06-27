import json
import os
from datetime import datetime, timedelta
import random

class HealthDataManager:
    def __init__(self):
        self.patients_file = "data/patients.json"
        self.health_records_file = "data/health_records.json"
        self.ensure_data_directory()
        self.load_data()
    
    def ensure_data_directory(self):
        """Ensure data directory exists"""
        os.makedirs("data", exist_ok=True)
    
    def load_data(self):
        """Load health data from JSON files"""
        # Load patients
        try:
            with open(self.patients_file, 'r') as f:
                self.patients = json.load(f)
        except FileNotFoundError:
            self.patients = {}
            self.save_patients()
        
        # Load health records
        try:
            with open(self.health_records_file, 'r') as f:
                self.health_records = json.load(f)
        except FileNotFoundError:
            self.health_records = {}
            self.save_health_records()
    
    def save_patients(self):
        """Save patients to JSON file"""
        with open(self.patients_file, 'w') as f:
            json.dump(self.patients, f, indent=2)
    
    def save_health_records(self):
        """Save health records to JSON file"""
        with open(self.health_records_file, 'w') as f:
            json.dump(self.health_records, f, indent=2)
    
    def add_patient(self, patient_id, patient_data):
        """Add a new patient"""
        self.patients[patient_id] = {
            **patient_data,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        self.save_patients()
    
    def get_patient(self, patient_id):
        """Get patient by ID"""
        return self.patients.get(patient_id)
    
    def get_all_patients(self):
        """Get all patients"""
        return self.patients
    
    def update_patient(self, patient_id, updates):
        """Update patient information"""
        if patient_id in self.patients:
            self.patients[patient_id].update(updates)
            self.patients[patient_id]["last_updated"] = datetime.now().isoformat()
            self.save_patients()
            return True
        return False
    
    def add_health_record(self, patient_id, record_type, data):
        """Add health record for patient"""
        if patient_id not in self.health_records:
            self.health_records[patient_id] = []
        
        record = {
            "type": record_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "id": len(self.health_records[patient_id])
        }
        
        self.health_records[patient_id].append(record)
        self.save_health_records()
        return record["id"]
    
    def get_health_records(self, patient_id, record_type=None, limit=None):
        """Get health records for patient"""
        if patient_id not in self.health_records:
            return []
        
        records = self.health_records[patient_id]
        
        if record_type:
            records = [r for r in records if r["type"] == record_type]
        
        # Sort by timestamp (newest first)
        records = sorted(records, key=lambda x: x["timestamp"], reverse=True)
        
        if limit:
            records = records[:limit]
        
        return records
    
    def get_vital_signs(self, patient_id, days=30):
        """Get recent vital signs for patient"""
        records = self.get_health_records(patient_id, "vital_signs", limit=days)
        return records
    
    def get_symptoms_history(self, patient_id, days=30):
        """Get recent symptoms for patient"""
        records = self.get_health_records(patient_id, "symptoms", limit=days)
        return records
    
    def calculate_health_score(self, patient_id):
        """Calculate overall health score based on recent data"""
        # This is a simplified health score calculation
        vital_signs = self.get_vital_signs(patient_id, 7)  # Last week
        symptoms = self.get_symptoms_history(patient_id, 7)
        
        score = 100  # Start with perfect score
        
        # Deduct points for concerning vital signs
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
        
        # Deduct points for symptoms
        for record in symptoms:
            severity = record["data"].get("severity", "mild")
            if severity == "severe":
                score -= 20
            elif severity == "moderate":
                score -= 10
            elif severity == "mild":
                score -= 5
        
        return max(0, score)  # Don't go below 0
    
    def generate_wellness_insights(self, patient_id):
        """Generate wellness insights for patient"""
        health_score = self.calculate_health_score(patient_id)
        vital_signs = self.get_vital_signs(patient_id, 30)
        symptoms = self.get_symptoms_history(patient_id, 30)
        
        insights = []
        
        # Health score insight
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
        
        # Trend analysis
        if len(vital_signs) >= 3:
            recent_bp = [r["data"].get("blood_pressure_systolic", 120) for r in vital_signs[:3]]
            if all(bp > 140 for bp in recent_bp):
                insights.append({
                    "type": "danger",
                    "title": "High Blood Pressure Pattern",
                    "message": "Your blood pressure has been consistently high. Please consult a doctor."
                })
        
        # Symptom patterns
        if len(symptoms) >= 3:
            severe_symptoms = [s for s in symptoms if s["data"].get("severity") == "severe"]
            if len(severe_symptoms) >= 2:
                insights.append({
                    "type": "danger",
                    "title": "Recurring Severe Symptoms",
                    "message": "You've reported multiple severe symptoms recently. Medical attention is recommended."
                })
        
        return insights

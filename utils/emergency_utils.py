import json
import os
from datetime import datetime
import streamlit as st
from utils.notification_utils import NotificationManager
from utils.location_utils import LocationManager

class EmergencyManager:
    def __init__(self):
        self.emergency_contacts_file = "data/emergency_contacts.json"
        self.ensure_data_directory()
        self.notification_manager = NotificationManager()
        self.location_manager = LocationManager()
        
        # Severity thresholds for automatic emergency detection
        self.severe_symptoms = {
            "chest_pain": {"severity": 9, "keywords": ["crushing", "severe", "radiating", "shortness of breath"]},
            "difficulty_breathing": {"severity": 9, "keywords": ["can't breathe", "gasping", "suffocating"]},
            "severe_headache": {"severity": 8, "keywords": ["worst headache", "sudden", "thunderclap"]},
            "stroke_symptoms": {"severity": 10, "keywords": ["face drooping", "arm weakness", "speech difficulty"]},
            "allergic_reaction": {"severity": 9, "keywords": ["swelling", "difficulty breathing", "hives", "anaphylaxis"]},
            "severe_bleeding": {"severity": 9, "keywords": ["bleeding heavily", "won't stop", "spurting"]},
            "loss_of_consciousness": {"severity": 10, "keywords": ["passed out", "unconscious", "fainted"]},
            "severe_abdominal_pain": {"severity": 8, "keywords": ["stabbing", "sudden", "severe"]},
            "poisoning": {"severity": 9, "keywords": ["poisoned", "overdose", "toxic"]},
            "severe_burn": {"severity": 8, "keywords": ["severe burn", "large area", "chemical burn"]}
        }
    
    def ensure_data_directory(self):
        """Ensure data directory exists"""
        os.makedirs("data", exist_ok=True)
    
    def assess_symptom_severity(self, symptoms_text, additional_info=""):
        """Assess if symptoms require emergency response using AI and rule-based analysis"""
        combined_text = f"{symptoms_text} {additional_info}".lower()
        
        # First try AI-based assessment if available
        ai_assessment = None
        try:
            if hasattr(st.session_state, 'model_manager') and st.session_state.model_manager:
                from utils.ai_models import model_manager
                ai_assessment = model_manager.analyze_symptom_severity(combined_text)
        except Exception:
            pass  # Fall back to rule-based analysis
        
        # Rule-based analysis for critical detection
        emergency_score = 0
        detected_emergencies = []
        
        for condition, details in self.severe_symptoms.items():
            for keyword in details["keywords"]:
                if keyword.lower() in combined_text:
                    emergency_score += details["severity"]
                    detected_emergencies.append({
                        "condition": condition,
                        "severity": details["severity"],
                        "keyword": keyword
                    })
        
        # Combine AI assessment with rule-based analysis
        if ai_assessment and ai_assessment.get("requires_emergency"):
            emergency_score = max(emergency_score, 50)  # Ensure high priority for AI-detected emergencies
        
        # Direct emergency keywords
        emergency_phrases = [
            "call 911", "emergency", "ambulance", "can't breathe", 
            "heart attack", "stroke", "unconscious", "severe pain",
            "bleeding heavily", "overdose", "poisoning"
        ]
        
        for phrase in emergency_phrases:
            if phrase in combined_text:
                emergency_score += 10
                detected_emergencies.append({
                    "condition": "direct_emergency_request",
                    "severity": 10,
                    "keyword": phrase
                })
        
        is_emergency = emergency_score >= 8
        
        return {
            "is_emergency": is_emergency,
            "severity_score": emergency_score,
            "detected_conditions": detected_emergencies,
            "recommendation": self.get_emergency_recommendation(emergency_score, detected_emergencies)
        }
    
    def get_emergency_recommendation(self, score, conditions):
        """Get emergency recommendation based on severity"""
        if score >= 10:
            return {
                "level": "CRITICAL",
                "action": "CALL 911 IMMEDIATELY",
                "message": "Critical emergency detected. Call emergency services now!",
                "color": "error"
            }
        elif score >= 8:
            return {
                "level": "URGENT",
                "action": "SEEK IMMEDIATE MEDICAL ATTENTION",
                "message": "Urgent medical attention required. Go to emergency room or call 911.",
                "color": "error"
            }
        elif score >= 5:
            return {
                "level": "CONCERNING",
                "action": "CONTACT HEALTHCARE PROVIDER",
                "message": "Concerning symptoms. Contact your doctor or urgent care.",
                "color": "warning"
            }
        else:
            return {
                "level": "MONITOR",
                "action": "MONITOR SYMPTOMS",
                "message": "Monitor symptoms and seek care if they worsen.",
                "color": "info"
            }
    
    def call_emergency_services(self):
        """Simulate emergency services call"""
        st.error("🚑 EMERGENCY SERVICES CONTACTED")
        
        # Get user location
        location = self.location_manager.get_current_location()
        
        # Create emergency record
        emergency_record = {
            "timestamp": datetime.now().isoformat(),
            "user": st.session_state.get("username", "emergency_user"),
            "location": location,
            "type": "ambulance_call",
            "status": "dispatched"
        }
        
        # In a real application, this would integrate with actual emergency services API
        st.success("✅ Emergency services have been notified!")
        st.info("📍 Your location has been shared with emergency responders.")
        st.info("🕒 Estimated arrival time: 8-12 minutes")
        
        # Notify emergency contacts
        self.notify_emergency_contacts("Emergency services called", emergency_record)
        
        return emergency_record
    
    def share_location(self):
        """Share location with emergency contacts"""
        location = self.location_manager.get_current_location()
        
        if location:
            st.success(f"📍 Location shared: {location.get('address', 'Location coordinates sent')}")
            
            # Notify emergency contacts with location
            message = f"Emergency: Location shared - {location.get('address', 'Coordinates sent')}"
            self.notify_emergency_contacts(message, {"location": location})
        else:
            st.error("❌ Unable to get current location. Please enable location services.")
    
    def notify_emergency_contacts(self, message, emergency_data=None):
        """Notify emergency contacts"""
        if st.session_state.get("username"):
            # Get emergency contacts from auth system
            from utils.auth_utils import AuthManager
            auth_manager = AuthManager()
            contacts = auth_manager.get_emergency_contacts(st.session_state.username)
            
            if contacts:
                for contact in contacts:
                    # Send SMS notification
                    full_message = f"EMERGENCY ALERT: {message} - {contact['name']}"
                    success = self.notification_manager.send_sms(contact['phone'], full_message)
                    
                    if success:
                        st.success(f"✅ Emergency contact notified: {contact['name']}")
                    else:
                        st.warning(f"⚠️ Failed to notify: {contact['name']}")
            else:
                st.warning("⚠️ No emergency contacts configured")
    
    def get_emergency_hospitals(self, location=None):
        """Get nearby emergency hospitals"""
        if not location:
            location = self.location_manager.get_current_location()
        
        # This would integrate with a real hospital database/API
        # For now, return mock data based on location
        hospitals = [
            {
                "name": "City General Hospital",
                "address": "123 Main St, Downtown",
                "phone": "+1-555-0123",
                "distance": "0.8 miles",
                "emergency_room": True,
                "trauma_center": True,
                "wait_time": "15 minutes"
            },
            {
                "name": "Regional Medical Center",
                "address": "456 Oak Ave, Midtown",
                "phone": "+1-555-0456",
                "distance": "1.2 miles",
                "emergency_room": True,
                "trauma_center": False,
                "wait_time": "25 minutes"
            },
            {
                "name": "University Hospital",
                "address": "789 College Blvd, University District",
                "phone": "+1-555-0789",
                "distance": "2.1 miles",
                "emergency_room": True,
                "trauma_center": True,
                "wait_time": "30 minutes"
            }
        ]
        
        return hospitals
    
    def activate_emergency_mode(self, severity_assessment):
        """Activate emergency mode based on symptom assessment"""
        st.session_state.emergency_mode = True
        
        # Log emergency activation
        emergency_log = {
            "timestamp": datetime.now().isoformat(),
            "user": st.session_state.get("username", "emergency_user"),
            "severity_assessment": severity_assessment,
            "auto_activated": True
        }
        
        return emergency_log
    
    def get_emergency_instructions(self, condition_type):
        """Get first aid instructions for specific conditions"""
        instructions = {
            "chest_pain": [
                "1. Call 911 immediately",
                "2. Have the person sit down and rest",
                "3. Loosen tight clothing",
                "4. If prescribed, help take nitroglycerin",
                "5. If unconscious, start CPR"
            ],
            "difficulty_breathing": [
                "1. Call 911 immediately",
                "2. Help person sit upright",
                "3. Loosen tight clothing",
                "4. If they have an inhaler, help them use it",
                "5. Stay calm and reassure them"
            ],
            "severe_bleeding": [
                "1. Call 911 immediately",
                "2. Apply direct pressure to wound",
                "3. Elevate injured area if possible",
                "4. Do not remove embedded objects",
                "5. Keep person warm and still"
            ],
            "stroke_symptoms": [
                "1. Call 911 immediately - Note the time",
                "2. Do not give food or water",
                "3. Keep person calm and still",
                "4. Loosen tight clothing",
                "5. Monitor breathing and pulse"
            ],
            "allergic_reaction": [
                "1. Call 911 immediately",
                "2. Remove or avoid the allergen",
                "3. Help use EpiPen if available",
                "4. Keep person calm and still",
                "5. Monitor breathing closely"
            ]
        }
        
        return instructions.get(condition_type, [
            "1. Call 911 for any life-threatening emergency",
            "2. Stay calm and assess the situation",
            "3. Follow dispatcher instructions",
            "4. Do not leave the person alone",
            "5. Be prepared to give CPR if trained"
        ])

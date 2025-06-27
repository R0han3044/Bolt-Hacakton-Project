import json
import hashlib
import os
from datetime import datetime

class AuthManager:
    def __init__(self):
        self.users_file = "data/users.json"
        self.ensure_data_directory()
        self.load_users()
    
    def ensure_data_directory(self):
        """Ensure data directory exists"""
        os.makedirs("data", exist_ok=True)
    
    def load_users(self):
        """Load users from JSON file"""
        try:
            with open(self.users_file, 'r') as f:
                self.users = json.load(f)
        except FileNotFoundError:
            # Create default users
            self.users = {
                "admin": {
                    "password_hash": self.hash_password("admin123"),
                    "role": "admin",
                    "created_at": datetime.now().isoformat(),
                    "emergency_contacts": []
                },
                "doctor": {
                    "password_hash": self.hash_password("doctor123"),
                    "role": "doctor",
                    "created_at": datetime.now().isoformat(),
                    "emergency_contacts": []
                },
                "patient": {
                    "password_hash": self.hash_password("patient123"),
                    "role": "patient",
                    "created_at": datetime.now().isoformat(),
                    "emergency_contacts": [
                        {"name": "Emergency Contact", "phone": "+1234567890", "relationship": "Family"}
                    ]
                }
            }
            self.save_users()
    
    def save_users(self):
        """Save users to JSON file"""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username, password):
        """Authenticate user"""
        if username in self.users:
            password_hash = self.hash_password(password)
            return self.users[username]["password_hash"] == password_hash
        return False
    
    def get_user_role(self, username):
        """Get user role"""
        if username in self.users:
            return self.users[username]["role"]
        return None
    
    def get_emergency_contacts(self, username):
        """Get emergency contacts for user"""
        if username in self.users:
            return self.users[username].get("emergency_contacts", [])
        return []
    
    def add_emergency_contact(self, username, contact):
        """Add emergency contact for user"""
        if username in self.users:
            if "emergency_contacts" not in self.users[username]:
                self.users[username]["emergency_contacts"] = []
            self.users[username]["emergency_contacts"].append(contact)
            self.save_users()
            return True
        return False
    
    def remove_emergency_contact(self, username, contact_index):
        """Remove emergency contact for user"""
        if username in self.users and "emergency_contacts" in self.users[username]:
            if 0 <= contact_index < len(self.users[username]["emergency_contacts"]):
                del self.users[username]["emergency_contacts"][contact_index]
                self.save_users()
                return True
        return False

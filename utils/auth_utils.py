import hashlib
from datetime import datetime
import json
from utils.db import SessionLocal, User, EmergencyContact
from sqlalchemy.orm import Session

class AuthManager:
    def __init__(self):
        self.db: Session = SessionLocal()
        self.ensure_default_users()

    def hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def ensure_default_users(self):
        """Ensure default users exist in the database"""
        default_users = [
            {
                "username": "admin",
                "password": "admin123",
                "role": "admin",
                "emergency_contacts": []
            },
            {
                "username": "doctor",
                "password": "doctor123",
                "role": "doctor",
                "emergency_contacts": []
            },
            {
                "username": "patient",
                "password": "patient123",
                "role": "patient",
                "emergency_contacts": [
                    {"name": "Emergency Contact", "phone": "+1234567890", "relationship": "Family"}
                ]
            }
        ]
        for user_data in default_users:
            user = self.db.query(User).filter(User.username == user_data["username"]).first()
            if not user:
                user = User(
                    username=user_data["username"],
                    password_hash=self.hash_password(user_data["password"]),
                    role=user_data["role"],
                    created_at=datetime.utcnow()
                )
                self.db.add(user)
                self.db.commit()
                self.db.refresh(user)
                for contact in user_data["emergency_contacts"]:
                    ec = EmergencyContact(
                        user_id=user.id,
                        name=contact["name"],
                        phone=contact["phone"],
                        relationship=contact.get("relationship")
                    )
                    self.db.add(ec)
                self.db.commit()

    def authenticate(self, username, password):
        """Authenticate user"""
        user = self.db.query(User).filter(User.username == username).first()
        if user:
            return user.password_hash == self.hash_password(password)
        return False

    def get_user_role(self, username):
        """Get user role"""
        user = self.db.query(User).filter(User.username == username).first()
        if user:
            return user.role
        return None

    def get_emergency_contacts(self, username):
        """Get emergency contacts for user"""
        user = self.db.query(User).filter(User.username == username).first()
        if user:
            return [
                {"name": ec.name, "phone": ec.phone, "relationship": ec.relationship}
                for ec in user.emergency_contacts
            ]
        return []

    def add_emergency_contact(self, username, contact):
        """Add emergency contact for user"""
        user = self.db.query(User).filter(User.username == username).first()
        if user:
            ec = EmergencyContact(
                user_id=user.id,
                name=contact.get("name"),
                phone=contact.get("phone"),
                relationship=contact.get("relationship")
            )
            self.db.add(ec)
            self.db.commit()
            return True
        return False

    def remove_emergency_contact(self, username, contact_index):
        """Remove emergency contact for user"""
        user = self.db.query(User).filter(User.username == username).first()
        if user and 0 <= contact_index < len(user.emergency_contacts):
            ec = user.emergency_contacts[contact_index]
            self.db.delete(ec)
            self.db.commit()
            return True
        return False

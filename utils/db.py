from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# SQLite database URL
DATABASE_URL = "sqlite:///emergency_helper.db"

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create session local class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    emergency_contacts = relationship("EmergencyContact", back_populates="user", cascade="all, delete-orphan")

class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    relation = Column(String, nullable=True)  # Renamed from 'relationship' to 'relation'
    
    user = relationship("User", back_populates="emergency_contacts")

class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, unique=True, index=True, nullable=False)
    data = Column(Text)  # JSON serialized string of patient data
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)

    health_records = relationship("HealthRecord", back_populates="patient", cascade="all, delete-orphan")

class HealthRecord(Base):
    __tablename__ = "health_records"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    record_type = Column(String, nullable=False)
    data = Column(Text)  # JSON serialized string of record data
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    patient = relationship("Patient", back_populates="health_records")

def init_db():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)

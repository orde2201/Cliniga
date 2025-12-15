from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    Date,
    Time,
    DateTime,
    ForeignKey,
    CheckConstraint,
    func
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import json

# =========================
# DATABASE CONFIG
# =========================

# Sesuaikan host, port, user, password, dan database sesuai VPS
DATABASE_URL = "postgresql+psycopg2://user:user123@localhost:5432/mydb"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# =========================
# MODELS
# =========================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(Text, nullable=False)
    role = Column(String(20), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    doctor = relationship("Doctor", back_populates="user", uselist=False)

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    specialization = Column(String(100), nullable=False)
    schedule = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor")

    def to_json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "specialization": self.specialization,
            "schedule": self.schedule,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    appointment_date = Column(Date, nullable=False)
    appointment_time = Column(Time, nullable=False)
    status = Column(String(20), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'confirmed', 'completed', 'cancelled')",
            name="appointment_status_check"
        ),
    )

    doctor = relationship("Doctor", back_populates="appointments")
    medical_record = relationship("MedicalRecord", back_populates="appointment", uselist=False)

    def to_json(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "appointment_date": self.appointment_date.isoformat(),
            "appointment_time": self.appointment_time.isoformat(),
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(Integer, primary_key=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), unique=True, nullable=False)
    diagnosis = Column(Text, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    appointment = relationship("Appointment", back_populates="medical_record")

    def to_json(self):
        return {
            "id": self.id,
            "appointment_id": self.appointment_id,
            "diagnosis": self.diagnosis,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

# =========================
# TEST / OUTPUT
# =========================

if __name__ == "__main__":
    session = SessionLocal()

    print("\n=== USERS ===")
    users = session.query(User).all()
    print(json.dumps([u.to_json() for u in users], indent=2))

    print("\n=== DOCTORS ===")
    doctors = session.query(Doctor).all()
    print(json.dumps([d.to_json() for d in doctors], indent=2))

    print("\n=== APPOINTMENTS ===")
    appointments = session.query(Appointment).all()
    print(json.dumps([a.to_json() for a in appointments], indent=2))

    print("\n=== MEDICAL RECORDS ===")
    records = session.query(MedicalRecord).all()
    print(json.dumps([m.to_json() for m in records], indent=2))

    session.close()

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    assessments = relationship("RiskAssessment", back_populates="owner")

class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    age = Column(Float, nullable=False)
    gender = Column(Integer, nullable=False)
    height = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    bmi = Column(Float, nullable=False)
    ap_hi = Column(Integer, nullable=False)
    ap_lo = Column(Integer, nullable=False)
    cholesterol = Column(Integer, nullable=False)
    gluc = Column(Integer, nullable=False)
    smoke = Column(Integer, nullable=False)
    alco = Column(Integer, nullable=False)
    active = Column(Integer, nullable=False)

    predicted_probability = Column(Float, nullable=False)
    risk_tier = Column(String, nullable=False)
    model_version = Column(String, default="logreg_v1")
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="assessments")

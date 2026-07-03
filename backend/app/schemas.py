from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class RiskInput(BaseModel):
    age: float = Field(ge=18, le=100, description="Age in years")
    gender: int = Field(ge=1, le=2, description="1=female, 2=male")
    height: float = Field(ge=120, le=220, description="Height in cm")
    weight: float = Field(ge=30, le=250, description="Weight in kg")
    ap_hi: int = Field(ge=70, le=250, description="Systolic blood pressure")
    ap_lo: int = Field(ge=40, le=180, description="Diastolic blood pressure")
    cholesterol: int = Field(ge=1, le=3, description="1=normal, 2=above, 3=well above")
    gluc: int = Field(ge=1, le=3, description="1=normal, 2=above, 3=well above")
    smoke: int = Field(ge=0, le=1)
    alco: int = Field(ge=0, le=1)
    active: int = Field(ge=0, le=1)

class RiskOutput(BaseModel):
    predicted_probability: float
    risk_percent: float
    risk_tier: str
    bmi: float
    model_version: str
    recommendation: str

class AssessmentHistoryItem(BaseModel):
    id: int
    age: float
    bmi: float
    ap_hi: int
    ap_lo: int
    predicted_probability: float
    risk_tier: str
    created_at: datetime
    class Config:
        from_attributes = True

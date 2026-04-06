from pydantic import BaseModel, EmailStr, Field, validator
from uuid import UUID
from typing import Optional, Any, Dict, List
from datetime import date, datetime
import re

class StandardResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now())

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    date_of_birth: date
    gender: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search("[A-Z]", v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search("[a-z]", v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search("[0-9]", v):
            raise ValueError('Password must contain at least one digit')
        if not re.search("[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError('Password must contain at least one special character')
        return v

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: str

    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search("[A-Z]", v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search("[a-z]", v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search("[0-9]", v):
            raise ValueError('Password must contain at least one digit')
        if not re.search("[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError('Password must contain at least one special character')
        return v

class TokenData(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    email: str

class UserProfileResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    date_of_birth: date
    gender: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    account_status: str
    email_verified: bool
    created_at: datetime
    last_login: Optional[datetime]

class UserProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    gender: Optional[str] = None

class UserSettingsResponse(BaseModel):
    user_id: str
    notifications_enabled: bool = True
    privacy_level: str = "private"
    data_sharing: bool = False
    language: str = "en"
    timezone: str = "UTC"

class UserSettingsUpdateRequest(BaseModel):
    notifications_enabled: Optional[bool] = None
    privacy_level: Optional[str] = None
    data_sharing: Optional[bool] = None
    language: Optional[str] = None
    timezone: Optional[str] = None

class HealthDataSubmissionRequest(BaseModel):
    blood_pressure_systolic: float
    blood_pressure_diastolic: float
    heart_rate: int
    chest_pain_type: Optional[str] = "typical"
    creatinine: Optional[float] = None
    urea: Optional[float] = None
    eGFR: Optional[float] = None
    urine_protein: Optional[float] = None
    fasting_glucose: Optional[float] = None
    HbA1c: Optional[float] = None
    total_cholesterol: Optional[float] = None
    ldl_cholesterol: Optional[float] = None
    hdl_cholesterol: Optional[float] = None
    triglycerides: Optional[float] = None
    bmi: Optional[float] = None
    smoking_status: Optional[str] = "never"
    physical_activity: Optional[str] = "moderate"
    family_history: Optional[str] = None
    medications: Optional[List[str]] = []
    allergies: Optional[List[str]] = []
    comorbidities: Optional[List[str]] = []

class HealthDataResponse(BaseModel):
    id: str
    user_id: str
    blood_pressure_systolic: float
    blood_pressure_diastolic: float
    heart_rate: int
    chest_pain_type: Optional[str]
    creatinine: Optional[float]
    urea: Optional[float]
    eGFR: Optional[float]
    urine_protein: Optional[float]
    fasting_glucose: Optional[float]
    HbA1c: Optional[float]
    total_cholesterol: Optional[float]
    ldl_cholesterol: Optional[float]
    hdl_cholesterol: Optional[float]
    triglycerides: Optional[float]
    bmi: Optional[float]
    smoking_status: Optional[str]
    physical_activity: Optional[str]
    family_history: Optional[str]
    medications: Optional[List[str]]
    allergies: Optional[List[str]]
    comorbidities: Optional[List[str]]
    created_at: datetime
    updated_at: datetime


class AnalysisTriggerRequest(BaseModel):
    health_data_id: UUID

class AnalysisTriggerResponse(BaseModel):
    analysis_id: UUID
    health_data_id: UUID
    user_id: UUID
    status: str
    message: str
    estimated_completion: datetime

class AnalysisResponse(BaseModel):
    id: UUID
    user_id: UUID
    health_data_id: UUID
    status: str
    cardiac_risk_level: Optional[str] = None
    cardiac_risk_score: Optional[float] = None
    cardiac_probability: Optional[float] = None
    cardiac_key_factors: Optional[List[str]] = None
    renal_risk_level: Optional[str] = None
    renal_risk_score: Optional[float] = None
    renal_probability: Optional[float] = None
    ckd_stage: Optional[int] = None
    egfr_decline_rate: Optional[str] = None
    renal_key_factors: Optional[List[str]] = None
    metabolic_risk_level: Optional[str] = None
    metabolic_risk_score: Optional[float] = None
    metabolic_probability: Optional[float] = None
    diabetes_risk: Optional[float] = None
    metabolic_syndrome_probability: Optional[float] = None
    metabolic_key_factors: Optional[List[str]] = None
    crm_patterns_identified: Optional[List[dict]] = None
    overall_risk_level: Optional[str] = None
    cardiac_recommendations: Optional[List[str]] = None
    renal_recommendations: Optional[List[str]] = None
    metabolic_recommendations: Optional[List[str]] = None
    lifestyle_recommendations: Optional[List[str]] = None
    model_version: Optional[str] = None
    confidence_score: Optional[float] = None
    created_at: datetime
    error_message: Optional[str] = None

class RiskProfileResponse(BaseModel):
    user_id: UUID
    latest_analysis_date: Optional[datetime] = None
    overall_risk_level: Optional[str] = None
    cardiac_risk_level: Optional[str] = None
    cardiac_risk_score: Optional[float] = None
    renal_risk_level: Optional[str] = None
    renal_risk_score: Optional[float] = None
    metabolic_risk_level: Optional[str] = None
    metabolic_risk_score: Optional[float] = None
    crm_patterns: Optional[List[dict]] = None
    overall_recommendations: Optional[List[str]] = None
    next_action_items: Optional[List[str]] = None

class PaginationInfo(BaseModel):
    total: int
    limit: int
    offset: int
    has_next: bool

class HealthDataListResponse(BaseModel):
    records: List[HealthDataResponse]
    pagination: PaginationInfo

class HealthDataUpdateRequest(BaseModel):
    blood_pressure_systolic: Optional[float] = None
    blood_pressure_diastolic: Optional[float] = None
    heart_rate: Optional[int] = None
    chest_pain_type: Optional[str] = None
    creatinine: Optional[float] = None
    urea: Optional[float] = None
    eGFR: Optional[float] = None
    urine_protein: Optional[float] = None
    fasting_glucose: Optional[float] = None
    HbA1c: Optional[float] = None
    total_cholesterol: Optional[float] = None
    ldl_cholesterol: Optional[float] = None
    hdl_cholesterol: Optional[float] = None
    triglycerides: Optional[float] = None
    bmi: Optional[float] = None
    smoking_status: Optional[str] = None
    physical_activity: Optional[str] = None
    family_history: Optional[str] = None
    medications: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    comorbidities: Optional[List[str]] = None

class HealthDataSummaryResponse(BaseModel):
    total_records: int
    latest_record_date: datetime
    latest_values: Dict[str, Any]
    average_values: Dict[str, float]
    trend_indicators: Dict[str, str]
    risk_flags: Dict[str, bool]

class ErrorDetail(BaseModel):
    field: Optional[str] = None
    reason: Optional[str] = None
    value: Optional[Any] = None
    valid_range: Optional[str] = None
    message: Optional[str] = None

class ErrorInfo(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorInfo
    timestamp: datetime = Field(default_factory=lambda: datetime.now())

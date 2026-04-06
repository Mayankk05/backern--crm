from datetime import date, datetime
from typing import Dict, Any, List

def calculate_age(birth_date: date) -> int:
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def calculate_bmi(weight_kg: float, height_m: float) -> float:
    if not height_m or height_m <= 0:
        return 0.0
    return round(weight_kg / (height_m ** 2), 2)

def extract_features_for_models(health_data: Dict[str, Any], user_info: Dict[str, Any]) -> Dict[str, List[float]]:
    dob_str = user_info.get("date_of_birth")
    if isinstance(dob_str, str):
        dob = date.fromisoformat(dob_str)
    else:
        dob = date(1980, 1, 1)
        
    age = calculate_age(dob)
    gender = str(user_info.get("gender", "male")).lower()
    
    sex_cardio = 2.0 if gender == "male" else 1.0
    sex_binary = 1.0 if gender == "male" else 0.0
    
    bmi = health_data.get("bmi")
    if bmi is None:
        weight = float(health_data.get("weight", 70.0))
        height = float(health_data.get("height", 1.70))
        bmi = calculate_bmi(weight, height)
    bmi = float(bmi)
    
    tc = float(health_data.get("total_cholesterol", 180))
    chol_mapped = 1
    if tc >= 240: chol_mapped = 3
    elif tc >= 200: chol_mapped = 2
    
    fg = float(health_data.get("fasting_glucose", 90))
    gluc_mapped = 1
    if fg > 125: gluc_mapped = 3
    elif fg >= 100: gluc_mapped = 2
    
    smoke_status = str(health_data.get("smoking_status", "none")).lower()
    smoke_binary = 1.0 if smoke_status in ["current", "smoker"] else 0.0
    
    activity = str(health_data.get("physical_activity", "moderate")).lower()
    active_binary = 1.0 if activity in ["moderate", "active", "high"] else 0.0
    
    cardiac_features = [
        float(age), # Still works even if training used days (scaler handles it if we trained on years)
        sex_cardio,
        float(health_data.get("height", 1.70)) * 100,
        float(health_data.get("weight", 70.0)),
        float(health_data.get("blood_pressure_systolic", 120)),
        float(health_data.get("blood_pressure_diastolic", 80)),
        float(chol_mapped),
        float(gluc_mapped),
        smoke_binary,
        0.0,
        active_binary
    ]

    renal_features = [
        float(age),
        float(health_data.get("blood_pressure_systolic", 120)),
        float(health_data.get("urea", 20.0)),
        float(health_data.get("creatinine", 1.1)),
        float(health_data.get("albumin", 0.0))
    ]

    metabolic_features = [
        float(age),
        sex_binary,
        bmi,
        float(health_data.get("hba1c", 5.5)),
        float(health_data.get("fasting_glucose", 100))
    ]

    return {
        "cardiac": cardiac_features,
        "renal": renal_features,
        "metabolic": metabolic_features
    }

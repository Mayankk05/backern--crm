from typing import Dict, Any, List, Tuple

CLINICAL_RANGES = {
    "blood_pressure_systolic": {"min": 90, "max": 180, "unit": "mmHg"},
    "blood_pressure_diastolic": {"min": 60, "max": 120, "unit": "mmHg"},
    "heart_rate": {"min": 40, "max": 200, "unit": "bpm"},
    "creatinine": {"min": 0.3, "max": 5.0, "unit": "mg/dL"},
    "urea": {"min": 7, "max": 50, "unit": "mg/dL"},
    "eGFR": {"min": 5, "max": 150, "unit": "mL/min"},
    "urine_protein": {"min": 0, "max": 3.5, "unit": "g/day"},
    "fasting_glucose": {"min": 50, "max": 400, "unit": "mg/dL"},
    "HbA1c": {"min": 4.0, "max": 12.0, "unit": "%"},
    "total_cholesterol": {"min": 50, "max": 400, "unit": "mg/dL"},
    "ldl_cholesterol": {"min": 0, "max": 300, "unit": "mg/dL"},
    "hdl_cholesterol": {"min": 10, "max": 100, "unit": "mg/dL"},
    "triglycerides": {"min": 0, "max": 1000, "unit": "mg/dL"},
    "bmi": {"min": 10, "max": 60, "unit": "kg/m²"}
}

def validate_health_data(data: Dict[str, Any]) -> Tuple[bool, List[Dict[str, Any]]]:
    errors = []
    
    for field, ranges in CLINICAL_RANGES.items():
        if field in data and data[field] is not None:
            value = data[field]
            if value < ranges["min"]:
                errors.append({
                    "field": field,
                    "value": value,
                    "valid_range": f"{ranges['min']}-{ranges['max']}",
                    "message": "Value is below minimum"
                })
            elif value > ranges["max"]:
                errors.append({
                    "field": field,
                    "value": value,
                    "valid_range": f"{ranges['min']}-{ranges['max']}",
                    "message": "Value exceeds maximum"
                })
                
    return len(errors) == 0, errors

def check_risk_flags(data: Dict[str, Any]) -> Dict[str, bool]:
    flags = {
        "high_bp": False,
        "high_glucose": False,
        "high_cholesterol": False,
        "low_hdl": False
    }
    
    if data.get("blood_pressure_systolic", 0) > 140 or data.get("blood_pressure_diastolic", 0) > 90:
        flags["high_bp"] = True
    
    if data.get("fasting_glucose", 0) > 126:
        flags["high_glucose"] = True
        
    if data.get("total_cholesterol", 0) > 240:
        flags["high_cholesterol"] = True
        
    if data.get("hdl_cholesterol", 100) < 40:
        flags["low_hdl"] = True
        
    return flags

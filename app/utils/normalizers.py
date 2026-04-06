from typing import Dict, Any, List

def normalize_health_data(data: Dict[str, Any]) -> Dict[str, Any]:
    normalized = data.copy()
    
    for key, value in normalized.items():
        if isinstance(value, float):
            normalized[key] = round(value, 2)
            
        elif isinstance(value, str):
            if key in ["smoking_status", "physical_activity", "gender", "chest_pain_type"]:
                normalized[key] = value.lower()
            
            if key in ["medications", "allergies", "comorbidities"] and "," in value:
                normalized[key] = [item.strip().lower() for item in value.split(",")]
                
    for key in ["medications", "allergies", "comorbidities"]:
        if key in normalized and isinstance(normalized[key], str):
            normalized[key] = [normalized[key].strip().lower()]
            
    return normalized

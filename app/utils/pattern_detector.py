from typing import List, Dict, Any

def detect_crm_patterns(cardiac_level: str, renal_level: str, metabolic_level: str) -> List[Dict[str, Any]]:
    patterns = []
    
    levels = ["low", "moderate", "high", "critical"]
    def is_at_least(current, target):
        return levels.index(current) >= levels.index(target)

    if is_at_least(cardiac_level, "high") and is_at_least(renal_level, "high"):
        severity = "high" if (cardiac_level == "critical" and renal_level == "critical") else "moderate"
        patterns.append({
            "pattern": "Cardio-Renal Syndrome",
            "severity": severity,
            "description": "Reduced cardiac output may be decreasing renal perfusion, accelerating kidney disease progression."
        })
    elif is_at_least(cardiac_level, "high") and renal_level == "moderate":
        patterns.append({
            "pattern": "Cardio-Renal Syndrome",
            "severity": "low",
            "description": "Elevated cardiac risk with early signs of renal involvement. Targeted monitoring of kidney function advised."
        })

    if is_at_least(metabolic_level, "high") and is_at_least(renal_level, "moderate"):
        severity = "high" if (metabolic_level in ["high", "critical"] and renal_level in ["high", "critical"]) else "moderate"
        patterns.append({
            "pattern": "Metabolic-Renal Interaction",
            "severity": severity,
            "description": "Hyperglycemia or metabolic dysfunction is likely accelerating kidney damage, increasing nephropathy risk."
        })

    if is_at_least(cardiac_level, "high") and is_at_least(metabolic_level, "high"):
        severity = "high" if (cardiac_level == "critical" and metabolic_level == "critical") else "moderate"
        patterns.append({
            "pattern": "Cardio-Metabolic Syndrome",
            "severity": severity,
            "description": "Metabolic factors (obesity, dyslipidemia) are significantly increasing cardiovascular risk profile."
        })

    if is_at_least(cardiac_level, "high") and is_at_least(renal_level, "high") and is_at_least(metabolic_level, "high"):
        patterns.append({
            "pattern": "Triple CRM Syndrome",
            "severity": "critical",
            "description": "Triple system involvement detected. Requires integrated, multi-specialist coordinated care for heart, kidneys, and metabolism."
        })

    return patterns

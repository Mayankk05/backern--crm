from typing import List, Dict

def generate_recommendations(cardiac_level: str, renal_level: str, metabolic_level: str, raw_values: Dict) -> Dict[str, List[str]]:
    recs = {
        "cardiac_recommendations": [],
        "renal_recommendations": [],
        "metabolic_recommendations": [],
        "lifestyle_recommendations": []
    }

    if cardiac_level == "critical":
        recs["cardiac_recommendations"].extend([
            "Urgent cardiologist consultation required",
            "Frequent heart rate and BP monitoring",
            "Discuss immediate pharmacological intervention with provider",
            "Emergency plan for acute chest pain or shortness of breath"
        ])
    elif cardiac_level == "high":
        recs["cardiac_recommendations"].extend([
            "Monthly specialist review",
            "Strict blood pressure target <130/80 mmHg",
            "DASH diet implementation",
            "Statins/Aspirin therapy discussion with doctor"
        ])
    elif cardiac_level == "moderate":
        recs["cardiac_recommendations"].extend([
            "Quarterly blood pressure checks",
            "Reduce saturated fat intake",
            "Baseline ECG and Stress Test recommended",
            "Regular aerobic exercise (150+ min/week)"
        ])
    else:
        recs["cardiac_recommendations"].extend([
            "Annual heart health screening",
            "Maintain current healthy cardiovascular routine",
            "Routine lipid profile check every 2 years"
        ])

    if renal_level == "critical":
        recs["renal_recommendations"].extend([
            "Immediate Nephrology consultation required",
            "Renal diet (low potassium, low phosphorus)",
            "Fluid intake monitoring as per specialist advice",
            "Review all medications for nephrotoxicity"
        ])
    elif renal_level == "high":
        recs["renal_recommendations"].extend([
            "Biannual kidney function tests (Creatinine/eGFR)",
            "Strict BP control to protect nephrons",
            "Urine albumin-to-creatinine ratio (ACR) screening",
            "Stay hydrated and avoid NSAIDs (e.g. Ibuprofen)"
        ])
    elif renal_level == "moderate":
        recs["renal_recommendations"].extend([
            "Annual renal function monitoring",
            "Moderate protein intake",
            "Screen for secondary causes of kidney decline",
            "Ensure adequate daily water intake"
        ])
    else:
        recs["renal_recommendations"].extend([
            "Routine annual kidney screening",
            "Maintain current hydration levels"
        ])

    if metabolic_level == "critical":
        recs["metabolic_recommendations"].extend([
            "Endocrinologist referral for intensive management",
            "Continuous glucose monitoring (CGM) if diabetic",
            "Immediate dietary overhaul - low glycemic index",
            "Discuss GLP-1 or Metformin optimization"
        ])
    elif metabolic_level == "high":
        recs["metabolic_recommendations"].extend([
            "Consistent weight monitoring (target 5-10% loss)",
            "HbA1c test every 3 months",
            "Replace refined carbs with high-fiber whole grains",
            "Strength training 2x per week to improve insulin sensitivity"
        ])
    elif metabolic_level == "moderate":
        recs["metabolic_recommendations"].extend([
            "Increase daily fiber to 25-30g",
            "Limit added sugars and trans fats",
            "Regular fasting glucose checks",
            "Increase daily step count to 10,000+"
        ])
    else:
        recs["metabolic_recommendations"].extend([
            "Regular metabolic panel annually",
            "Maintain current weight and activity levels"
        ])

    if raw_values.get("age", 0) > 60:
        recs["lifestyle_recommendations"].append("Age-appropriate low-impact exercises")
    
    recs["lifestyle_recommendations"].extend([
        "Aim for 7-9 hours of consistent sleep",
        "Stress management techniques (mindfulness/yoga)",
        "Hydration: Aim for 2-2.5L water daily",
        "Limit alcohol consumption"
    ])
    
    if raw_values.get("sbp", 0) > 140:
         recs["lifestyle_recommendations"].append("Reduce dietary sodium intake below 2300mg/day")

    return recs

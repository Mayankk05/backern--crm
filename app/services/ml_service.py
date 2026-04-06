import joblib
import os
import numpy as np
from typing import Dict, List, Any

class MLService:
    def __init__(self):
        self.model_dir = "ml_models"
        self.models = {}
        self.scalers = {}
        self._load_models()

    def _load_models(self):
        model_files = {
            "cardiac": "cardiac_model.pkl",
            "renal": "renal_model.pkl",
            "metabolic": "metabolic_model.pkl"
        }
        scaler_files = {
            "cardiac": "cardiac_scaler.pkl"
        }
        
        for key, filename in model_files.items():
            path = os.path.join(self.model_dir, filename)
            if os.path.exists(path):
                self.models[key] = joblib.load(path)
                print(f"Loaded {key} model")
        
        for key, filename in scaler_files.items():
            path = os.path.join(self.model_dir, filename)
            if os.path.exists(path):
                self.scalers[key] = joblib.load(path)
                print(f"Loaded {key} scaler")

    async def predict_cardiac_risk(self, features: List[float]) -> Dict[str, Any]:
        if "cardiac" not in self.models:
            return {"risk_score": 0.0, "risk_level": "Unknown", "key_factors": []}
        
        input_data = np.array(features).reshape(1, -1)
        if "cardiac" in self.scalers:
            input_data = self.scalers["cardiac"].transform(input_data)
            
        prob = self.models["cardiac"].predict_proba(input_data)[0][1]
        factors = self._identify_cardiac_factors(features)
        
        return {
            "risk_score": round(float(prob) * 100, 2),
            "risk_level": self._get_risk_level(prob),
            "key_factors": factors
        }

    async def predict_renal_risk(self, features: List[float]) -> Dict[str, Any]:
        if "renal" not in self.models:
            return {"risk_score": 0.0, "risk_level": "Unknown", "key_factors": []}
        
        prob = self.models["renal"].predict_proba(np.array(features).reshape(1, -1))[0][1]
        factors = self._identify_renal_factors(features)
        
        return {
            "risk_score": round(float(prob) * 100, 2),
            "risk_level": self._get_risk_level(prob),
            "key_factors": factors
        }

    async def predict_metabolic_risk(self, features: List[float]) -> Dict[str, Any]:
        if "metabolic" not in self.models:
            return {"risk_score": 0.0, "risk_level": "Unknown", "key_factors": []}
        
        prob = self.models["metabolic"].predict_proba(np.array(features).reshape(1, -1))[0][1]
        factors = self._identify_metabolic_factors(features)
        
        return {
            "risk_score": round(float(prob) * 100, 2),
            "risk_level": self._get_risk_level(prob),
            "key_factors": factors
        }

    def _get_risk_level(self, prob: float) -> str:
        if prob < 0.2: return "Low"
        if prob < 0.5: return "Moderate"
        if prob < 0.8: return "High"
        return "Critical"

    def _identify_cardiac_factors(self, features: List[float]) -> List[str]:
        factors = []
        if features[4] > 140 or features[5] > 90: factors.append("Elevated Blood Pressure")
        if features[6] > 1: factors.append("High Cholesterol")
        if features[8] > 0: factors.append("Smoking")
        if features[10] == 0: factors.append("Sedentary Lifestyle")
        if features[7] > 1: factors.append("Elevated Glucose")
        return factors[:3]

    def _identify_renal_factors(self, features: List[float]) -> List[str]:
        factors = []
        if features[3] > 1.2: factors.append("High Serum Creatinine")
        if features[4] > 0: factors.append("Albuminuria (Protein in Urine)")
        if features[2] > 20: factors.append("High Blood Urea")
        if features[1] > 140: factors.append("Uncontrolled Hypertension")
        return factors[:3]

    def _identify_metabolic_factors(self, features: List[float]) -> List[str]:
        factors = []
        if features[3] > 6.5: factors.append("High HbA1c (Diabetes Range)")
        if features[4] > 125: factors.append("Elevated Fasting Glucose")
        if features[2] > 30: factors.append("Obesity (High BMI)")
        return factors[:3]

ml_service = MLService()

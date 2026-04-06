import logging
from uuid import UUID
from datetime import datetime
from app.models.database import get_supabase
from app.services.ml_service import ml_service
from app.utils.ml_utils import extract_features_for_models
from app.utils.pattern_detector import detect_crm_patterns
from app.utils.recommendation_generator import generate_recommendations

logger = logging.getLogger(__name__)

async def run_risk_analysis(user_id: str, health_data_id: str, analysis_id: str):
    supabase = get_supabase()
    
    try:
        health_resp = supabase.table("health_data").select("*").eq("id", health_data_id).single().execute()
        health_data = health_resp.data
        
        user_resp = supabase.table("users").select("date_of_birth, gender").eq("user_id", user_id).single().execute()
        user_info = user_resp.data
        
        features = extract_features_for_models(health_data, user_info)
        
        cardiac_res = ml_service.predict_cardiac(features["cardiac"])
        renal_res = ml_service.predict_renal(features["renal"])
        metabolic_res = ml_service.predict_metabolic(features["metabolic"])
        
        patterns = detect_crm_patterns(
            cardiac_res["risk_level"],
            renal_res["risk_level"],
            metabolic_res["risk_level"]
        )
        
        recommendations = generate_recommendations(
            cardiac_res["risk_level"],
            renal_res["risk_level"],
            metabolic_res["risk_level"],
            features["raw_values"]
        )
        
        all_levels = [cardiac_res["risk_level"], renal_res["risk_level"], metabolic_res["risk_level"]]
        if "critical" in all_levels:
            overall_risk = "critical"
        elif all_levels.count("high") >= 2:
            overall_risk = "high"
        elif "high" in all_levels or "moderate" in all_levels:
            overall_risk = "moderate"
        else:
            overall_risk = "low"
            
        avg_confidence = (cardiac_res["confidence"] + renal_res["confidence"] + metabolic_res["confidence"]) / 3
        
        update_data = {
            "status": "completed",
            "cardiac_risk_level": cardiac_res["risk_level"],
            "cardiac_risk_score": cardiac_res["risk_score"],
            "cardiac_probability": cardiac_res["probability"],
            "cardiac_key_factors": cardiac_res["key_factors"],
            "renal_risk_level": renal_res["risk_level"],
            "renal_risk_score": renal_res["risk_score"],
            "renal_probability": renal_res["probability"],
            "ckd_stage": renal_res["ckd_stage"],
            "egfr_decline_rate": renal_res["eGFR_decline_rate"],
            "renal_key_factors": renal_res["key_factors"],
            "metabolic_risk_level": metabolic_res["risk_level"],
            "metabolic_risk_score": metabolic_res["risk_score"],
            "metabolic_probability": metabolic_res["probability"],
            "diabetes_risk": metabolic_res["diabetes_risk"],
            "metabolic_syndrome_probability": metabolic_res["metabolic_syndrome_probability"],
            "metabolic_key_factors": metabolic_res["key_factors"],
            "crm_patterns_identified": patterns,
            "overall_risk_level": overall_risk,
            "cardiac_recommendations": recommendations["cardiac_recommendations"],
            "renal_recommendations": recommendations["renal_recommendations"],
            "metabolic_recommendations": recommendations["metabolic_recommendations"],
            "lifestyle_recommendations": recommendations["lifestyle_recommendations"],
            "confidence_score": round(avg_confidence, 2),
            "model_version": "v1.0"
        }
        
        supabase.table("analysis_results").update(update_data).eq("id", analysis_id).execute()
        
        supabase.table("audit_logs").insert({
            "user_id": user_id,
            "action": "ml_analysis_completed",
            "resource": "analysis_results",
            "resource_id": analysis_id,
            "status": "success",
            "success": True
        }).execute()
        
    except Exception as e:
        logger.error(f"Analysis failed for {analysis_id}: {str(e)}")
        try:
            supabase.table("analysis_results").update({
                "status": "failed",
                "error_message": str(e)
            }).eq("id", analysis_id).execute()
            
            supabase.table("audit_logs").insert({
                "user_id": user_id,
                "action": "ml_analysis_failed",
                "resource": "analysis_results",
                "resource_id": analysis_id,
                "status": "failure",
                "success": False,
                "request_params": {"error": str(e)}
            }).execute()
        except:
            pass

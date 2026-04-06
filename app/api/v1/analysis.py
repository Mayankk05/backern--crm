from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status, Query
from uuid import UUID
from datetime import datetime, timedelta, UTC
from typing import List, Optional

from app.models.database import get_supabase
from app.models.schemas import (
    AnalysisTriggerRequest, AnalysisTriggerResponse, 
    AnalysisResponse, RiskProfileResponse
)
from app.middleware.auth import get_current_user
from app.background_tasks.analysis_tasks import run_risk_analysis

router = APIRouter(prefix="/analysis", tags=["Analysis"])

@router.post("/analyze", response_model=AnalysisTriggerResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_analysis(
    payload: AnalysisTriggerRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    supabase = get_supabase()
    user_id = current_user["sub"]
    
    res = supabase.table("health_data").select("id").eq("id", str(payload.health_data_id)).eq("user_id", user_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Health data record not found or access denied.")
        
    analysis_data = {
        "user_id": user_id,
        "health_data_id": str(payload.health_data_id),
        "status": "processing",
        "created_at": datetime.now(UTC).isoformat()
    }
    
    insert_res = supabase.table("analysis_results").insert(analysis_data).execute()
    if not insert_res.data:
        raise HTTPException(status_code=500, detail="Failed to initiate analysis.")
        
    analysis_record = insert_res.data[0]
    
    background_tasks.add_task(
        run_risk_analysis, 
        user_id, 
        str(payload.health_data_id), 
        analysis_record["id"]
    )
    
    supabase.table("audit_logs").insert({
        "user_id": user_id,
        "action": "ml_analysis_triggered",
        "resource": "analysis_results",
        "resource_id": analysis_record["id"],
        "status": "success"
    }).execute()
    
    return {
        "analysis_id": analysis_record["id"],
        "health_data_id": payload.health_data_id,
        "user_id": UUID(user_id),
        "status": "processing",
        "message": "Analysis is being processed. Results will be available shortly.",
        "estimated_completion": datetime.now(UTC) + timedelta(seconds=10)
    }

@router.get("/{id}", response_model=AnalysisResponse)
async def get_analysis(
    id: UUID,
    current_user: dict = Depends(get_current_user)
):
    supabase = get_supabase()
    user_id = current_user["sub"]
    
    res = supabase.table("analysis_results").select("*").eq("id", str(id)).eq("user_id", user_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Analysis not found or access denied.")
        
    supabase.table("audit_logs").insert({
        "user_id": user_id,
        "action": "view_analysis",
        "resource": "analysis_results",
        "resource_id": str(id),
        "status": "success"
    }).execute()
    
    return res.data[0]

@router.get("/", response_model=dict)
async def list_analyses(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    supabase = get_supabase()
    user_id = current_user["sub"]
    
    count_res = supabase.table("analysis_results").select("id", count="exact").eq("user_id", user_id).execute()
    total = count_res.count if count_res.count is not None else 0
    
    res = supabase.table("analysis_results")\
        .select("id, health_data_id, overall_risk_level, cardiac_risk_level, renal_risk_level, metabolic_risk_level, status, created_at, confidence_score")\
        .eq("user_id", user_id)\
        .order("created_at", desc=True)\
        .range(offset, offset + limit - 1)\
        .execute()
        
    return {
        "success": True,
        "data": {
            "analyses": res.data,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_next": (offset + limit) < total
            }
        },
        "message": "Analyses retrieved successfully",
        "timestamp": datetime.now(UTC).isoformat()
    }

@router.get("/risk-profile", response_model=RiskProfileResponse)
async def get_risk_profile(
    current_user: dict = Depends(get_current_user)
):
    supabase = get_supabase()
    user_id = current_user["sub"]
    
    res = supabase.table("analysis_results")\
        .select("*")\
        .eq("user_id", user_id)\
        .eq("status", "completed")\
        .order("created_at", desc=True)\
        .limit(1)\
        .execute()
        
    if not res.data:
        return {
            "user_id": UUID(user_id),
            "overall_risk_level": "none",
            "crm_patterns": [],
            "overall_recommendations": ["Submit health data to see your risk profile."],
            "next_action_items": ["Complete your first health data submission"]
        }
        
    latest = res.data[0]
    
    action_items = []
    if latest["overall_risk_level"] in ["high", "critical"]:
        action_items.append("Schedule a comprehensive clinical review with your primary care provider.")
    
    if latest["cardiac_risk_level"] in ["high", "critical"]:
        action_items.append("Consult a cardiologist for specialized heart health assessment.")
        
    if latest["renal_risk_level"] in ["high", "critical"]:
        action_items.append("Repeat renal function tests (Creatinine/eGFR) within 3 months.")
        
    if latest["metabolic_risk_level"] in ["high", "critical"]:
        action_items.append("Consult a dietitian or endocrinologist for metabolic management.")
    
    if not action_items:
        action_items.append("Follow regular annual health screening schedule.")

    all_recs = []
    if latest["cardiac_recommendations"]: all_recs.extend(latest["cardiac_recommendations"][:1])
    if latest["renal_recommendations"]: all_recs.extend(latest["renal_recommendations"][:1])
    if latest["metabolic_recommendations"]: all_recs.extend(latest["metabolic_recommendations"][:1])
    if latest["lifestyle_recommendations"]: all_recs.extend(latest["lifestyle_recommendations"][:2])

    return {
        "user_id": UUID(user_id),
        "latest_analysis_date": latest["created_at"],
        "overall_risk_level": latest["overall_risk_level"],
        "cardiac_risk_level": latest["cardiac_risk_level"],
        "cardiac_risk_score": latest["cardiac_risk_score"],
        "renal_risk_level": latest["renal_risk_level"],
        "renal_risk_score": latest["renal_risk_score"],
        "metabolic_risk_level": latest["metabolic_risk_level"],
        "metabolic_risk_score": latest["metabolic_risk_score"],
        "crm_patterns": latest["crm_patterns_identified"],
        "overall_recommendations": all_recs,
        "next_action_items": action_items
    }

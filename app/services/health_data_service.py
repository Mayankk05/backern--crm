from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from app.models.database import get_supabase
from app.utils.validators import validate_health_data, check_risk_flags
from app.utils.normalizers import normalize_health_data
from app.models.schemas import HealthDataSubmissionRequest, HealthDataUpdateRequest
from fastapi import HTTPException, status
import numpy as np
import pandas as pd

class HealthDataService:
    @staticmethod
    async def submit_data(user_id: str, data: HealthDataSubmissionRequest) -> Dict[str, Any]:
        normalized_data = normalize_health_data(data.dict())
        supabase = get_supabase()
        response = supabase.table("health_data").insert(normalized_data).execute()
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to save health data")
        record = response.data[0]
        HealthDataService._log_action(
            user_id=user_id,
            action_type="HEALTH_DATA_SUBMITTED",
            endpoint="/api/v1/health/data",
            method="POST",
            status_code=201,
            success=True
        )
        return record

    @staticmethod
    async def get_all_data(user_id: str, limit: int = 10, offset: int = 0, sort_by: str = "created_at", order: str = "desc") -> Dict[str, Any]:
        supabase = get_supabase()
        query = supabase.table("health_data").select("*", count="exact").eq("user_id", user_id)
        query = query.order(sort_by, desc=(order == "desc"))
        query = query.range(offset, offset + limit - 1)
        response = query.execute()
        total = response.count if response.count is not None else 0
        records = response.data if response.data else []
        HealthDataService._log_action(
            user_id=user_id,
            action_type="HEALTH_DATA_RETRIEVED",
            endpoint="/api/v1/health/data",
            method="GET",
            status_code=200,
            success=True
        )
        return {
            "records": records,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_next": (offset + limit) < total
            }
        }

    @staticmethod
    async def get_single_data(user_id: str, record_id: str) -> Dict[str, Any]:
        supabase = get_supabase()
        response = supabase.table("health_data").select("*").eq("id", record_id).eq("user_id", user_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Health data record not found")
        return response.data[0]

    @staticmethod
    async def update_data(user_id: str, record_id: str, data: HealthDataUpdateRequest) -> Dict[str, Any]:
        supabase = get_supabase()
        existing = await HealthDataService.get_single_data(user_id, record_id)
        update_dict = {k: v for k, v in data.dict().items() if v is not None}
        if not update_dict:
            return existing
        normalized_update = normalize_health_data(update_dict)
        is_valid, validation_errors = validate_health_data(normalized_update)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Validation Error", "invalid_fields": validation_errors}
            )
        normalized_update["updated_at"] = datetime.now().isoformat()
        response = supabase.table("health_data").update(normalized_update).eq("id", record_id).eq("user_id", user_id).execute()
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to update record")
        HealthDataService._log_action(
            user_id=user_id,
            action_type="HEALTH_DATA_UPDATED",
            endpoint=f"/api/v1/health/data/{record_id}",
            method="PUT",
            status_code=200,
            success=True
        )
        return response.data[0]

    @staticmethod
    async def delete_data(user_id: str, record_id: str) -> bool:
        supabase = get_supabase()
        await HealthDataService.get_single_data(user_id, record_id)
        response = supabase.table("health_data").delete().eq("id", record_id).eq("user_id", user_id).execute()
        HealthDataService._log_action(
            user_id=user_id,
            action_type="HEALTH_DATA_DELETED",
            endpoint=f"/api/v1/health/data/{record_id}",
            method="DELETE",
            status_code=200,
            success=True
        )
        return True

    @staticmethod
    async def get_summary(user_id: str) -> Dict[str, Any]:
        supabase = get_supabase()
        response = supabase.table("health_data").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        records = response.data if response.data else []
        total_records = len(records)
        if total_records == 0:
            raise HTTPException(status_code=404, detail="No health data found for summary")
        df = pd.DataFrame(records)
        numeric_fields = [
            "blood_pressure_systolic", "blood_pressure_diastolic", "heart_rate",
            "creatinine", "urea", "eGFR", "urine_protein", "fasting_glucose",
            "HbA1c", "total_cholesterol", "ldl_cholesterol", "hdl_cholesterol",
            "triglycerides", "bmi"
        ]
        latest_record = records[0]
        latest_values = {f: latest_record.get(f) for f in numeric_fields if latest_record.get(f) is not None}
        average_values = {f: float(df[f].mean()) for f in numeric_fields if f in df.columns and not df[f].isnull().all()}
        trends = {}
        if total_records < 3:
            trends = {f"{f.split('_')[0]}_trend": "Insufficient data" for f in ["blood_pressure", "heart_rate", "glucose", "cholesterol"]}
        else:
            trends["glucose_trend"] = HealthDataService._calculate_trend(df, "fasting_glucose")
            trends["blood_pressure_trend"] = HealthDataService._calculate_trend(df, "blood_pressure_systolic")
            trends["heart_rate_trend"] = HealthDataService._calculate_trend(df, "heart_rate")
            trends["cholesterol_trend"] = HealthDataService._calculate_trend(df, "total_cholesterol")
        risk_flags = check_risk_flags(latest_record)
        HealthDataService._log_action(
            user_id=user_id,
            action_type="HEALTH_SUMMARY_RETRIEVED",
            endpoint="/api/v1/health/summary",
            method="GET",
            status_code=200,
            success=True
        )
        return {
            "total_records": total_records,
            "latest_record_date": latest_record["created_at"],
            "latest_values": latest_values,
            "average_values": average_values,
            "trend_indicators": trends,
            "risk_flags": risk_flags
        }

    @staticmethod
    def _calculate_trend(df: pd.DataFrame, field: str) -> str:
        if field not in df.columns or df[field].isnull().all():
            return "Insufficient data"
        count = len(df)
        values = df[field].tolist()[::-1]
        if count < 3:
            return "Insufficient data"
        elif 3 <= count <= 5:
            first = values[0]
            last = values[-1]
            diff = (last - first) / first if first != 0 else 0
            if diff > 0.05: return "rising"
            if diff < -0.05: return "falling"
            return "stable"
        else:
            last_3_avg = np.mean(values[-3:])
            prev_avg = np.mean(values[:-3])
            diff = (last_3_avg - prev_avg) / prev_avg if prev_avg != 0 else 0
            if diff > 0.05: return "rising"
            if diff < -0.05: return "falling"
            return "stable"

    @staticmethod
    def _log_action(user_id: str, action_type: str, endpoint: str, method: str, status_code: int, success: bool, error_message: Optional[str] = None):
        supabase = get_supabase()
        try:
            audit_entry = {
                "user_id": user_id,
                "action": action_type,
                "endpoint": endpoint,
                "http_method": method,
                "status_code": status_code,
                "success": success,
                "error_message": error_message,
                "created_at": datetime.now().isoformat()
            }
            supabase.table("audit_logs").insert(audit_entry).execute()
        except:
            pass

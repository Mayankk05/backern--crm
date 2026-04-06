from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import (
    StandardResponse, UserProfileResponse, UserProfileUpdateRequest,
    UserSettingsResponse, UserSettingsUpdateRequest
)
from app.middleware.auth import get_current_user
from app.models.database import get_supabase
from typing import Dict, Any

router = APIRouter(prefix="/users", tags=["User Profiles"])

@router.get("/profile", response_model=StandardResponse)
async def get_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    user_id = current_user["user_id"]
    supabase = get_supabase()
    response = supabase.table("users").select("*").eq("user_id", user_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_record = response.data[0]
    user_record.pop("password_hash", None)
    
    return StandardResponse(
        success=True,
        data=user_record,
        message="Profile retrieved successfully"
    )

@router.put("/profile", response_model=StandardResponse)
async def update_profile(
    profile_data: UserProfileUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    update_dict = {k: v for k, v in profile_data.dict().items() if v is not None}
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
        
    update_dict["updated_at"] = "now()"
    
    supabase = get_supabase()
    response = supabase.table("users").update(update_dict).eq("user_id", user_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to update profile")
        
    user_record = response.data[0]
    user_record.pop("password_hash", None)
    
    return StandardResponse(
        success=True,
        data=user_record,
        message="Profile updated successfully"
    )

@router.get("/settings", response_model=StandardResponse)
async def get_settings(current_user: Dict[str, Any] = Depends(get_current_user)):
    return StandardResponse(
        success=True,
        data={
            "user_id": current_user["user_id"],
            "notifications_enabled": True,
            "privacy_level": "private",
            "data_sharing": False,
            "language": "en",
            "timezone": "UTC"
        },
        message="Settings retrieved successfully"
    )

@router.put("/settings", response_model=StandardResponse)
async def update_settings(
    settings_data: UserSettingsUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    return StandardResponse(
        success=True,
        data=settings_data.dict(),
        message="Settings updated successfully"
    )

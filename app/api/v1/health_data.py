from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.models.schemas import (
    StandardResponse, HealthDataSubmissionRequest, HealthDataResponse,
    HealthDataListResponse, HealthDataUpdateRequest, HealthDataSummaryResponse
)
from app.services.health_data_service import HealthDataService
from app.middleware.auth import get_current_user
from typing import Dict, Any, Optional

router = APIRouter(prefix="/health", tags=["Health Data"])

@router.post("/data", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
async def submit_health_data(
    data: HealthDataSubmissionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    record = await HealthDataService.submit_data(user_id, data)
    return StandardResponse(
        success=True,
        data=record,
        message="Health data submitted successfully"
    )

@router.get("/data", response_model=StandardResponse)
async def list_health_data(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("created_at"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    result = await HealthDataService.get_all_data(user_id, limit, offset, sort_by, order)
    return StandardResponse(
        success=True,
        data=result,
        message="Health data retrieved successfully"
    )

@router.get("/data/{id}", response_model=StandardResponse)
async def get_health_record(
    id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    record = await HealthDataService.get_single_data(user_id, id)
    return StandardResponse(
        success=True,
        data=record,
        message="Health data retrieved successfully"
    )

@router.put("/data/{id}", response_model=StandardResponse)
async def update_health_record(
    id: str,
    data: HealthDataUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    record = await HealthDataService.update_data(user_id, id, data)
    return StandardResponse(
        success=True,
        data=record,
        message="Health data updated successfully"
    )

@router.delete("/data/{id}", response_model=StandardResponse)
async def delete_health_record(
    id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    await HealthDataService.delete_data(user_id, id)
    return StandardResponse(
        success=True,
        data=None,
        message="Health data deleted successfully"
    )

@router.get("/summary", response_model=StandardResponse)
async def get_health_summary(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    summary = await HealthDataService.get_summary(user_id)
    return StandardResponse(
        success=True,
        data=summary,
        message="Health summary retrieved successfully"
    )

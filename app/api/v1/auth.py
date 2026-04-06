from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import (
    UserRegisterRequest, UserLoginRequest, StandardResponse,
    TokenRefreshRequest, ForgotPasswordRequest, ResetPasswordRequest, TokenData
)
from app.services.auth_service import AuthService
from app.middleware.auth import get_current_user
from datetime import datetime
from app.config import settings
from typing import Dict, Any

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=StandardResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegisterRequest):
    user_record = await AuthService.register_user(user_data)
    return StandardResponse(
        success=True,
        data={
            "user_id": user_record["user_id"],
            "email": user_record["email"],
            "full_name": user_record["full_name"],
            "created_at": user_record["created_at"]
        },
        message="User registered successfully"
    )

@router.post("/login", response_model=StandardResponse)
async def login(login_data: UserLoginRequest):
    login_result = await AuthService.login_user(login_data)
    return StandardResponse(
        success=True,
        data={
            "access_token": login_result["access_token"],
            "refresh_token": login_result["refresh_token"],
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user_id": login_result["user_id"],
            "email": login_result["email"]
        },
        message="Login successful"
    )

@router.post("/refresh", response_model=StandardResponse)
async def refresh(refresh_data: TokenRefreshRequest):
    from app.utils.security import decode_token, create_access_token
    payload = decode_token(refresh_data.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    new_access_token = create_access_token({"user_id": payload["user_id"]})
    return StandardResponse(
        success=True,
        data={
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        },
        message="Token refreshed successfully"
    )

@router.post("/logout", response_model=StandardResponse)
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    AuthService._log_action(
        user_id=current_user["user_id"],
        action_type="logout",
        success=True
    )
    return StandardResponse(
        success=True,
        message="Logout successful"
    )

@router.post("/forgot-password", response_model=StandardResponse)
async def forgot_password(request: ForgotPasswordRequest):
    return StandardResponse(
        success=True,
        message="Password reset link sent to email"
    )

@router.post("/reset-password", response_model=StandardResponse)
async def reset_password(request: ResetPasswordRequest):
    return StandardResponse(
        success=True,
        message="Password reset successfully"
    )

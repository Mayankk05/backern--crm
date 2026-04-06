from datetime import datetime
from typing import Optional, Dict, Any
from app.models.database import get_supabase
from app.utils.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.models.schemas import UserRegisterRequest, UserLoginRequest
from fastapi import HTTPException, status
import uuid

class AuthService:
    @staticmethod
    async def register_user(user_data: UserRegisterRequest) -> Dict[str, Any]:
        supabase = get_supabase()
        response = supabase.table("users").select("email").eq("email", user_data.email).execute()
        if response.data:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
        
        password_hash = hash_password(user_data.password)
        
        new_user = {
            "email": user_data.email,
            "password_hash": password_hash,
            "full_name": user_data.full_name,
            "date_of_birth": str(user_data.date_of_birth),
            "gender": user_data.gender,
            "phone": user_data.phone,
            "address": user_data.address
        }
        
        insert_response = supabase.table("users").insert(new_user).execute()
        if not insert_response.data:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user")
        
        user_record = insert_response.data[0]
        
        AuthService._log_action(
            user_id=user_record["user_id"],
            action_type="register",
            success=True
        )
        
        return user_record

    @staticmethod
    async def login_user(login_data: UserLoginRequest) -> Dict[str, Any]:
        supabase = get_supabase()
        response = supabase.table("users").select("*").eq("email", login_data.email).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        
        user_record = response.data[0]
        
        if not verify_password(login_data.password, user_record["password_hash"]):
            AuthService._log_action(
                user_id=user_record["user_id"],
                action_type="login_failed",
                success=False,
                error_message="Invalid password"
            )
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        
        if user_record["account_status"] != "active":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive or suspended")
        
        token_data = {"user_id": str(user_record["user_id"]), "email": user_record["email"]}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token({"user_id": str(user_record["user_id"])})
        
        supabase.table("users").update({"last_login": "now()"}).eq("user_id", user_record["user_id"]).execute()
        AuthService._log_action(
            user_id=user_record["user_id"],
            action_type="login",
            success=True
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_id": user_record["user_id"],
            "email": user_record["email"]
        }

    @staticmethod
    def _log_action(user_id: str, action_type: str, success: bool, error_message: Optional[str] = None):
        supabase = get_supabase()
        try:
            audit_entry = {
                "user_id": user_id,
                "action_type": action_type,
                "success": success,
                "error_message": error_message,
                "created_at": datetime.now().isoformat()
            }
            supabase.table("audit_logs").insert(audit_entry).execute()
        except:
            pass

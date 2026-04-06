from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, users, health_data, analysis
from app.services.ml_service import ml_service
from app.config import settings
from app.models.database import get_supabase
from datetime import datetime
import uvicorn

app = FastAPI(
    title="CRM Analysis Platform API",
    description="Backend API for CRM Analysis Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=settings.cors_methods_list,
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=f"/api/{settings.API_VERSION}")
app.include_router(users.router, prefix=f"/api/{settings.API_VERSION}")
app.include_router(health_data.router, prefix=f"/api/{settings.API_VERSION}")
app.include_router(analysis.router, prefix=f"/api/{settings.API_VERSION}")

@app.on_event("startup")
async def startup_event():
    pass

@app.get("/health", tags=["Utility"])
async def health_check():
    db_status = "connected"
    supabase = get_supabase()
    try:
        supabase.table("users").select("count", count="exact").limit(1).execute()
    except Exception as e:
        db_status = f"disconnected: {str(e)}"
        
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

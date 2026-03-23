from fastapi import APIRouter

from app.api.routes.bills import router as bills_router
from app.api.routes.genai import router as genai_router
from app.api.routes.health import router as health_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(genai_router, tags=["genai"])
api_router.include_router(bills_router, tags=["bills"])

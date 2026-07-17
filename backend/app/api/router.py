from fastapi import APIRouter

from app.api.routes import companies, health

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(companies.router, tags=["companies"])


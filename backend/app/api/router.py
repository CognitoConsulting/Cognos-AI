from fastapi import APIRouter

from app.api.routes import (
    auth,
    companies,
    daily_summaries,
    health,
    knowledgebase,
    reporting,
    whatsapp,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router)
api_router.include_router(companies.router, tags=["companies"])
api_router.include_router(knowledgebase.router, tags=["knowledgebase"])
api_router.include_router(reporting.router, tags=["reporting"])
api_router.include_router(whatsapp.router, tags=["whatsapp"])
api_router.include_router(daily_summaries.router, tags=["daily-summary"])


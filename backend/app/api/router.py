from fastapi import APIRouter

from app.api.routes import companies, health, knowledgebase, whatsapp

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(companies.router, tags=["companies"])
api_router.include_router(knowledgebase.router, tags=["knowledgebase"])
api_router.include_router(whatsapp.router, tags=["whatsapp"])


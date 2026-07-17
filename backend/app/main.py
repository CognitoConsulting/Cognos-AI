import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.db.session import SessionLocal
from app.services.daily_summary_scheduler import run_due_daily_summaries

logger = logging.getLogger(__name__)


@asynccontextmanager
async def app_lifespan(_app: FastAPI) -> AsyncIterator[None]:
    scheduler_task: asyncio.Task | None = None
    if settings.daily_summary_scheduler_enabled:
        scheduler_task = asyncio.create_task(_daily_summary_scheduler_loop())
        logger.info("Daily summary scheduler started.")

    try:
        yield
    finally:
        if scheduler_task:
            scheduler_task.cancel()
            try:
                await scheduler_task
            except asyncio.CancelledError:
                logger.info("Daily summary scheduler stopped.")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Backend API for Cognos AI construction reporting SaaS.",
        lifespan=app_lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    return app


app = create_app()


async def _daily_summary_scheduler_loop() -> None:
    interval_seconds = max(settings.daily_summary_scheduler_interval_seconds, 30)
    while True:
        await asyncio.to_thread(_run_daily_summary_scheduler_once)
        await asyncio.sleep(interval_seconds)


def _run_daily_summary_scheduler_once() -> None:
    db = SessionLocal()
    try:
        run_due_daily_summaries(db)
    except Exception:
        db.rollback()
        logger.exception("Daily summary scheduler run failed.")
    finally:
        db.close()


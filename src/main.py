import os
import uuid
from contextlib import asynccontextmanager
from typing import Dict
from urllib.parse import urlparse

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.middleware.rate_limit import RateLimitMiddleware
from src.api.models import StandardApiResponse
from src.api.routers import chat as chat_router
from src.services.rag.preprocessing.preprocess import (
    PROCESSED_FILE_PATH,
    process_and_save,
)
from src.utils.config import get_settings
from src.utils.helper import initialize_vector_db
from src.utils.logger import get_logger

config = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup and shutdown events."""
    logger.info("Application startup sequence initiated...")

    if not os.path.exists(PROCESSED_FILE_PATH):
        logger.info(
            f"Processed file not found at {PROCESSED_FILE_PATH}. Starting processing..."
        )
        await process_and_save()
    else:
        logger.info(f"Processed file found at {PROCESSED_FILE_PATH}.")

    await initialize_vector_db()

    yield
    logger.info("Application shutdown sequence initiated...")


app = FastAPI(
    title="RAG Assistant API",
    description="RAG Assistant",
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    RateLimitMiddleware,
    max_requests=config.RATE_LIMIT_MAX_REQUESTS,
    window_seconds=config.RATE_LIMIT_WINDOW_SECONDS,
)

logger.info("Registering API routers")
app.include_router(chat_router.router, prefix="/api", tags=["Chat"])
logger.info("All routers registered successfully")


@app.get("/", tags=["Health Check"], response_model=StandardApiResponse[Dict[str, str]])
async def health_check() -> StandardApiResponse[Dict[str, str]]:
    """Performs a health check by testing all database connections in real-time."""
    health_status = {
        "status": "ok",
        "message": "RAG Assistant API is running",
    }
    return StandardApiResponse(
        success=True,
        status_code=200,
        message="RAG Assistant API is running",
        response=health_status,
    )


@app.get(
    "/health", tags=["Health Check"], response_model=StandardApiResponse[Dict[str, str]]
)
async def health_alias() -> StandardApiResponse[Dict[str, str]]:
    """Alias for the main health check endpoint"""
    return await health_check()


if __name__ == "__main__":
    import uvicorn

    logger.info(
        f"Starting server on {config.HOST}:{config.PORT} (Debug: {config.DEBUG})"
    )
    uvicorn.run(
        "src.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        workers=config.WORKERS,
    )

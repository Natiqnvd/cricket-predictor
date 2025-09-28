from fastapi import FastAPI
from contextlib import asynccontextmanager
from loguru import logger
# from api import router as api_router
from app.core.config import settings
from app.db.session import init_engine, close_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Initializing Cricket Predictor API...")
    init_engine()
    logger.info("✅ Database engine initialized.")
    yield
    # Shutdown
    logger.info("🛑 Shutting down Cricket Predictor API...")
    await close_engine()
    logger.info("💾 Database engine closed.")


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}

# app.include_router(api_router, prefix="/api")
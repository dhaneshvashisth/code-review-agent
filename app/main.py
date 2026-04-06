from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.database import init_db
from app.api.routes import router
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    await init_db()
    logger.info("Database initialized successfully")
    yield
    logger.info("Shutting down...")

app = FastAPI(
    title="Code Review Agent",
    description="Multi-agent AI code review system",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(router, prefix="/api/v1")
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.api.schemas import ReviewRequest, ReviewResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/review", response_model= ReviewResponse)
async def create_review(request : ReviewRequest, db : AsyncSession = Depends(get_db)):
    logger.info(f"REview request received for language: {request.language}")
    return ReviewResponse(status="ok", message="review request received succesfully", review_id=None)


@router.get("/health")
async def health_check():
    return{"status" : "healthy", "version" : "0.1.0"}
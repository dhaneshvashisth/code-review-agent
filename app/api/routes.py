from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.api.schemas import ReviewRequest, ReviewResponse
from app.graph.graph import review_graph
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()



@router.post("/review", response_model=ReviewResponse)
async def create_review(request: ReviewRequest, db: AsyncSession = Depends(get_db)):
    review_id = str(uuid.uuid4())
    logger.info(f"Starting review {review_id}")

    initial_state = {
        "review_id": review_id,
        "code": request.code,
        "language": request.language,
        "bug_detection_result": None,
        "quality_check_result": None,
        "security_check_result": None,
        "final_report": None,
        "has_critical_failure": False,
        "error_message": None
    }

    result = await review_graph.ainvoke(initial_state)

    return ReviewResponse(
        status="completed",
        message="Review completed successfully",
        review_id=review_id,
        final_report=result.get("final_report")
    )


@router.get("/health")
async def health_check():
    return{"status" : "healthy", "version" : "0.1.0"}
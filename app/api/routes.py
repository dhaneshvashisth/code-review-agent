from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.api.schemas import ReviewRequest, ReviewResponse, ReviewHistoryItem
from app.db.crud import (
    hash_code, get_cached_review, create_review_request,
    save_agent_output, save_final_report, update_review_status,
    log_error, get_review_by_id, get_review_history
)
from app.graph.graph import review_graph
import logging
from app.db.models import ReviewStatus
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/review", response_model=ReviewResponse)
async def create_review(request: ReviewRequest, db: AsyncSession = Depends(get_db)):
    review_id = str(uuid.uuid4())
    code_hash = hash_code(request.code)
    logger.info(f"Starting review {review_id}")

    cached = await get_cached_review(db, code_hash)
    if cached:
        logger.info(f"Returning cached review for hash {code_hash[:16]}")
        return ReviewResponse(
            status="completed",
            message="Review retrieved from cache",
            review_id=cached["review_id"],
            final_report=cached["final_report"],
            cached=True
        )

    await create_review_request(db, review_id, request.code, code_hash, request.language)

    try:

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
        final_report=result.get("final_report")
        for agent_name, result_key in [
                ("bug_detector", "bug_detection_result"),
                ("quality_checker", "quality_check_result"),
                ("security_checker", "security_check_result")
            ]:
                agent_result = result.get(result_key)
                if agent_result:
                    await save_agent_output(
                        db, review_id, agent_name,
                        agent_result, agent_result["status"],
                        agent_result.get("error")
                    )

        await save_final_report(db, review_id, final_report)
        await update_review_status(db, review_id, ReviewStatus.COMPLETED)



        return ReviewResponse(
            status="completed",
            message="Review completed successfully",
            review_id=review_id,
            final_report= final_report,
            cached = False
            
        )

    except Exception as e:
        logger.error(f"Review {review_id} failed: {e}")
        await update_review_status(db, review_id, ReviewStatus.FAILED)
        await log_error(db, "review_failed", str(e), review_id)
        raise HTTPException(status_code=500, detail="Review processing failed")


@router.get("/review/{review_id}")
async def get_review(review_id: str, db: AsyncSession = Depends(get_db)):
     review = await get_review_by_id(db, review_id)
     if not review:
          raise HTTPException(status_code=404, detail="Review not found")
     return review

@router.get("/history")
async def get_history(
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    reviews = await get_review_history(db, limit, offset)
    return {"reviews": reviews, "limit": limit, "offset": offset}


@router.get("/health")
async def health_check():
    return{"status" : "healthy", "version" : "0.1.0"}
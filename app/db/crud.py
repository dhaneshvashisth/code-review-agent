import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import ReviewRequest, AgentOutputs, FinalReports, ErrorLogs
from app.db.models import ReviewStatus, AgentStatus
import uuid
import logging

logger = logging.getLogger(__name__)

def hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()

async def get_cached_review(db: AsyncSession, code_hash: str) -> dict | None:
    try:
        stmt = (
            select(ReviewRequest, FinalReports)
            .join(FinalReports, FinalReports.review_id == ReviewRequest.id)
            .where(ReviewRequest.code_hash == code_hash)
            .where(ReviewRequest.status == ReviewStatus.COMPLETED)
            .order_by(ReviewRequest.created_at.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        row = result.first()
        if row:
            review, report = row
            logger.info(f"Cache hit for hash {code_hash[:16]}...")
            return {
                "review_id": str(review.id),
                "final_report": report.report_json,
                "cached": True
            }
        return None
    except Exception as e:
        logger.error(f"Cache check failed: {e}")
        return None

async def create_review_request(
    db: AsyncSession,
    review_id: str,
    code: str,
    code_hash: str,
    language: str | None
) -> ReviewRequest:
    review = ReviewRequest(
        id=uuid.UUID(review_id),
        code_text=code,
        code_hash=code_hash,
        language=language,
        status=ReviewStatus.PENDING
    )
    db.add(review)
    await db.flush()
    return review

async def save_agent_output(
    db: AsyncSession,
    review_id: str,
    agent_name: str,
    output: dict,
    status: str,
    error_message: str | None = None
):
    agent_output = AgentOutputs(
        id=uuid.uuid4(),
        review_id=uuid.UUID(review_id),
        agent_name=agent_name,
        output=output,
        status=AgentStatus.SUCCESS if status == "success" else AgentStatus.FAILED,
        error_message=error_message
    )
    db.add(agent_output)
    await db.flush()

async def save_final_report(
    db: AsyncSession,
    review_id: str,
    report: dict
):
    final = FinalReports(
        id=uuid.uuid4(),
        review_id=uuid.UUID(review_id),
        overall_score=report.get("overall_score", 0),
        summary=report.get("summary", ""),
        critical_issues=report.get("critical_issues", 0),
        warnings=report.get("warnings", 0),
        report_json=report
    )
    db.add(final)
    await db.flush()

async def update_review_status(
    db: AsyncSession,
    review_id: str,
    status: ReviewStatus
):
    stmt = select(ReviewRequest).where(ReviewRequest.id == uuid.UUID(review_id))
    result = await db.execute(stmt)
    review = result.scalar_one_or_none()
    if review:
        review.status = status
        await db.flush()

async def log_error(
    db: AsyncSession,
    error_type: str,
    error_message: str,
    review_id: str | None = None,
    agent_name: str | None = None
):
    error = ErrorLogs(
        id=uuid.uuid4(),
        review_id=uuid.UUID(review_id) if review_id else None,
        agent_name=agent_name,
        error_type=error_type,
        error_message=error_message
    )
    db.add(error)
    await db.flush()

async def get_review_by_id(db: AsyncSession, review_id: str) -> dict | None:
    try:
        stmt = (
            select(ReviewRequest, FinalReports)
            .join(FinalReports, FinalReports.review_id == ReviewRequest.id)
            .where(ReviewRequest.id == uuid.UUID(review_id))
        )
        result = await db.execute(stmt)
        row = result.first()
        if not row:
            return None
        review, report = row
        return {
            "review_id": str(review.id),
            "language": review.language,
            "status": review.status.value,
            "created_at": review.created_at.isoformat(),
            "final_report": report.report_json
        }
    except Exception as e:
        logger.error(f"Failed to fetch review {review_id}: {e}")
        return None

async def get_review_history(
    db: AsyncSession,
    limit: int = 10,
    offset: int = 0
) -> list:
    try:
        stmt = (
            select(ReviewRequest, FinalReports)
            .join(FinalReports, FinalReports.review_id == ReviewRequest.id)
            .where(ReviewRequest.status == ReviewStatus.COMPLETED)
            .order_by(ReviewRequest.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await db.execute(stmt)
        rows = result.all()
        return [
            {
                "review_id": str(review.id),
                "language": review.language,
                "overall_score": report.overall_score,
                "critical_issues": report.critical_issues,
                "created_at": review.created_at.isoformat()
            }
            for review, report in rows
        ]
    except Exception as e:
        logger.error(f"Failed to fetch history: {e}")
        return []
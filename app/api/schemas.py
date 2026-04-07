from pydantic import BaseModel
from typing import Optional, Any

class ReviewRequest(BaseModel):
    code : str
    language : Optional[str] = None

class ReviewResponse(BaseModel):
    status : str
    message : str
    review_id : Optional[str] = None
    final_report: Optional[dict[str, Any]] = None
    cached : bool = False

class ReviewHistoryItem(BaseModel):
    review_id: str
    language: Optional[str]
    overall_score: int
    critical_issues: int
    created_at: str
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

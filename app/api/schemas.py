from pydantic import BaseModel
from typing import Optional

class ReviewRequest(BaseModel):
    code : str
    language : Optional[str] = None

class ReviewResponse(BaseModel):
    status : str
    message : str
    review_id : Optional[str] = None
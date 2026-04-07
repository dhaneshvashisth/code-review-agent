from pydantic import BaseModel, field_validator
from typing import Optional, Any, TypeVar, Generic

T = TypeVar("T")

SUPPORTED_LANGUAGES = [
    "python", "javascript", "typescript", "java", "go",
    "rust", "cpp", "c", "csharp", "ruby", "php", "swift"
]


class APIResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
    error: Optional[str] = None

class ReviewRequest(BaseModel):
    code : str
    language : Optional[str] = None

    @field_validator("code")
    @classmethod
    def code_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Code cannot be empty")
        if len(v) > 10000:
            raise ValueError("Code exceeds maximum length of 10000 characters")
        return v

    @field_validator("language")
    @classmethod
    def language_must_be_valid(cls, v):
        if v and v.lower() not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language. Supported: {', '.join(SUPPORTED_LANGUAGES)}")
        return v.lower() if v else v

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


class HistoryResponse(BaseModel):
    reviews: list[ReviewHistoryItem]
    total: int
    limit: int
    offset: int
    has_more: bool
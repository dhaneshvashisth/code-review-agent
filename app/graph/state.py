from typing import Optional, Any
from typing import TypedDict

class AgentResult(TypedDict):
    status: str
    findings: list[dict[str, Any]]
    error: Optional[str]

class ReviewState(TypedDict):
    review_id: str
    code: str
    language: Optional[str]
    bug_detection_result: Optional[AgentResult]
    quality_check_result: Optional[AgentResult]
    security_check_result: Optional[AgentResult]
    final_report: Optional[dict[str, Any]]
    has_critical_failure: bool
    error_message: Optional[str]
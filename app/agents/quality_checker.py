from app.graph.state import ReviewState
import logging

logger = logging.getLogger(__name__)

def quality_check_node(state: ReviewState) -> dict:
    logger.info(f"Quality checker running for review_id: {state['review_id']}")
    try:
        result = {
            "status": "success",
            "findings": [
                {
                    "type": "quality",
                    "severity": "critical",
                    "message": "Quality Checker finding — LLM not connected yet",
                    "line": None
                }
            ],
            "error": None
        }
        return { "quality_check_result": result}
    except Exception as e:
        logger.error(f"Quality check failed: {e}")
        return {
            
            "quality_check_result": {
                "status": "failed",
                "findings": [],
                "error": str(e)
            }
        }
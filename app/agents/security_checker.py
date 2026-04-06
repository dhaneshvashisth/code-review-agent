from app.graph.state import ReviewState
import logging

logger = logging.getLogger(__name__)

def security_check_node(state: ReviewState) -> dict:
    logger.info(f"Security checker running for review_id: {state['review_id']}")
    try:
        result = {
            "status": "success",
            "findings": [
                {
                    "type": "security",
                    "severity": "warning",
                    "message": "Security Checker finding — SQL connection vulnerablity",
                    "line": None
                }
            ],
            "error": None
        }
        return { "security_check_result": result}
    except Exception as e:
        logger.error(f"Security check failed: {e}")
        return {
            
            "security_check_result": {
                "status": "failed",
                "findings": [],
                "error": str(e)
            }
        }
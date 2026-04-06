from app.graph.state import ReviewState
import logging

logger = logging.getLogger(__name__)

def bug_detection_node(state: ReviewState) -> dict:
    logger.info(f"Bug detector running for review_id: {state['review_id']}")
    try:
        result = {
            "status": "success",
            "findings": [
                {
                    "type": "bug",
                    "severity": "warning",
                    "message": "Dummy bug finding — LLM not connected yet",
                    "line": None
                }
            ],
            "error": None
        }
        return { "bug_detection_result": result}
    except Exception as e:
        logger.error(f"Bug detector failed: {e}")
        return {
            
            "bug_detection_result": {
                "status": "failed",
                "findings": [],
                "error": str(e)
            }
        }
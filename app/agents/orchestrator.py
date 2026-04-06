import hashlib
from app.graph.state import ReviewState
import logging

logger = logging.getLogger(__name__)

def orchestrator_node(state: ReviewState) -> dict:
    logger.info(f"Orchestrator running for review_id: {state['review_id']}")

    code = state.get("code", "")

    if not code or not code.strip():
        return {
            "has_critical_failure": True,
            "error_message": "Empty code submitted"
        }

    code_hash = hashlib.sha256(code.encode()).hexdigest()
    logger.info(f"Code hash: {code_hash}")

    return {}
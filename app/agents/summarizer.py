from app.graph.state import ReviewState
import logging

logger = logging.getLogger(__name__)

def summarizer_node(state: ReviewState) -> dict:
    logger.info(f"Summarizer running for review_id: {state['review_id']}")

    bug_result = state.get("bug_detection_result")
    quality_result = state.get("quality_check_result")
    security_result = state.get("security_check_result")

    failed_agents = [
        name for name, result in [
            ("bug_detector", bug_result),
            ("quality_checker", quality_result),
            ("security_checker", security_result)
        ]
        if result and result.get("status") == "failed"
    ]

    all_findings = []
    for result in [bug_result, quality_result, security_result]:
        if result and result.get("findings"):
            all_findings.extend(result["findings"])

    final_report = {
        "overall_score": 75,
        "total_findings": len(all_findings),
        "findings": all_findings,
        "failed_agents": failed_agents,
        "summary": "Dummy summary — LLM not connected yet",
        "partial_review": len(failed_agents) > 0
    }

    return { "final_report": final_report}
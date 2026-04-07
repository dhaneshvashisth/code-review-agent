from app.graph.state import ReviewState
import logging
from app.core.llm import llm
import json
from langchain_core.messages import HumanMessage, SystemMessage
from tenacity import retry, stop_after_attempt, wait_exponential

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are a senior code reviewer writing an executive summary.
You will receive findings from three specialized agents: bug detector, 
quality checker, and security checker.
Write a concise 2-3 sentence summary of the overall code quality.

You MUST respond with ONLY valid JSON. No explanation, no markdown, no extra text.
Respond in exactly this format:
{
    "summary": "2-3 sentence overall assessment of the code quality"
}"""

def _calculate_score(all_findings: list) -> int:
    score = 100
    for finding in all_findings:
        severity = finding.get("severity", "info")
        if severity == "critical":
            score -= 15
        elif severity == "warning":
            score -= 5
        elif severity == "info":
            score -= 1
    return max(0, score)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def _call_llm(all_findings: list) -> dict:
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Findings:\n{json.dumps(all_findings, indent=2)}")
    ]
    response = llm.invoke(messages)
    raw = response.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())



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

    critical_count = sum(1 for f in all_findings if f.get("severity") == "critical")
    warning_count = sum(1 for f in all_findings if f.get("severity") == "warning")
    score = _calculate_score(all_findings)

    try:
        llm_result = _call_llm(all_findings)
        summary = llm_result.get("summary", "Review completed.")
    except Exception as e:
        logger.error(f"Summarizer LLM failed: {e}")
        summary = f"Review completed with {len(all_findings)} findings. Summary generation failed."



    final_report = {
        "overall_score": score,
        "critical_issues": critical_count,
        "warnings": warning_count, 
        "total_findings": len(all_findings),
        "findings": all_findings,
        "failed_agents": failed_agents,
        "summary": summary,
        "partial_review": len(failed_agents) > 0
    }

    logger.info(f"Review complete. Score: {score}, Findings: {len(all_findings)}")

    return { "final_report": final_report}
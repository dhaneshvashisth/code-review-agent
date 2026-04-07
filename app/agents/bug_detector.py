from app.graph.state import ReviewState
from app.core.llm import llm
from tenacity import retry, stop_after_attempt, wait_exponential
from langchain_core.messages import HumanMessage, SystemMessage
import json

import logging

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are an expert code reviewer specializing in bug detection.
                Analyze the provided code and identify bugs, logical errors, unhandled exceptions,
                edge cases, and potential runtime failures.

                You MUST respond with ONLY valid JSON. No explanation, no markdown, no extra text.
                Respond in exactly this format:
                {
                    "findings": [
                        {
                            "type": "bug",
                            "severity": "critical",
                            "message": "description of the bug",
                            "line": null
                        }
                    ]
                }

                Severity levels: critical, warning, info
                If no bugs found, return: {"findings": []}"""


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)


def _call_llm(code: str, language: str) -> dict:
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Language: {language or 'unknown'}\n\nCode:\n{code}")
    ]
    response = llm.invoke(messages)
    raw = response.content.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)


def bug_detection_node(state: ReviewState) -> dict:
    logger.info(f"Bug detector running for review_id: {state['review_id']}")
    try:
        result = _call_llm(state["code"], state.get("language"))
        findings = result.get("findings", [])
        logger.info(f"Bug detector found {len(findings)} issues")
        return {
            "bug_detection_result" : {
                "status" : "success",
                "findings" : findings,
                "error" : None
            }
        }
       
    except Exception as e:
        logger.error(f"Bug detector failed: {e}")
        return {
            
            "bug_detection_result": {
                "status": "failed",
                "findings": [],
                "error": str(e)
            }
        }
from app.graph.state import ReviewState
from app.core.llm import llm
import json
from langchain_core.messages import HumanMessage, SystemMessage
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are an expert code reviewer specializing in code quality.
            Analyze the provided code for readability, maintainability, and best practices.
            Check for: poor naming conventions, overly complex functions, code duplication,
            missing docstrings, magic numbers, and violation of clean code principles.

            You MUST respond with ONLY valid JSON. No explanation, no markdown, no extra text.
            Respond in exactly this format:
            {
                "findings": [
                    {
                        "type": "quality",
                        "severity": "warning",
                        "message": "description of the quality issue",
                        "line": null
                    }
                ]
            }

            Severity levels: critical, warning, info
            If no issues found, return: {"findings": []}"""



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




def quality_check_node(state: ReviewState) -> dict:
    logger.info(f"Quality checker running for review_id: {state['review_id']}")
    try:
        result = _call_llm(state["code"], state.get("language"))
        findings = result.get("findings", [])
        logger.info(f"Quality Checker found {len(findings)} issues")
        return {
            "quality_check_result": {
                "status" : "success",
                "findings" : findings,
                "error" : None

            }

        }
            
    except Exception as e:
        logger.error(f"Quality check failed: {e}")
        return {
            
            "quality_check_result": {
                "status": "failed",
                "findings": [],
                "error": str(e)
            }
        }
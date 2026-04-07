from app.graph.state import ReviewState
import logging
from app.core.llm import llm
import json
from langchain_core.messages import HumanMessage, SystemMessage
from tenacity import retry, stop_after_attempt, wait_exponential

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are an expert code reviewer specializing in security analysis.
            Analyze the provided code for security vulnerabilities.
            Check for: hardcoded passwords or API keys, SQL injection vulnerabilities,
            command injection risks, unsafe use of eval(), exposed sensitive data,
            insecure deserialization, and missing input validation.

            You MUST respond with ONLY valid JSON. No explanation, no markdown, no extra text.
            Respond in exactly this format:
            {
                "findings": [
                    {
                        "type": "security",
                        "severity": "critical",
                        "message": "description of the security issue",
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





def security_check_node(state: ReviewState) -> dict:
    logger.info(f"Security checker running for review_id: {state['review_id']}")
    try:
        result = _call_llm(state["code"], state.get("language"))
        findings = result.get("findings")
        logger.info(f"Security Checker found {len(findings)} issues")
        return { "security_check_result": {
            "status": "success",
            "findings": findings,
            "error": None
            }
                
        }

        
    except Exception as e:
        logger.error(f"Security check failed: {e}")
        return {
            
            "security_check_result": {
                "status": "failed",
                "findings": [],
                "error": str(e)
            }
        }
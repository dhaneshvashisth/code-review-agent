from langchain_openai import ChatOpenAI
from app.core.config import settings
from langchain_core.messages import HumanMessage, SystemMessage
import json, logging
from app.core.exceptions import LLMException
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)


llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=settings.OPENAI_API_KEY,
    request_timeout=30,
    max_retries=0,
)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((Exception,)),
    reraise=True
)
def call_llm_with_retry(system_prompt: str, user_content: str, agent_name: str) -> dict:
    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content)
        ]
        response = llm.invoke(messages)
        raw = response.content.strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        parsed = json.loads(raw)
        return parsed

    except json.JSONDecodeError as e:
        logger.error(f"{agent_name} returned invalid JSON: {e}")
        raise LLMException(f"Invalid JSON response: {e}", agent_name)
    except Exception as e:
        logger.error(f"{agent_name} LLM call failed: {e}")
        raise LLMException(f"LLM call failed: {e}", agent_name)
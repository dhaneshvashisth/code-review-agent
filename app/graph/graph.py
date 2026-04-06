from langgraph.graph import StateGraph, END
from app.graph.state import ReviewState
from app.agents.orchestrator import orchestrator_node
from app.agents.bug_detector import bug_detection_node
from app.agents.quality_checker import quality_check_node
from app.agents.security_checker import security_check_node
from app.agents.summarizer import summarizer_node
import logging

logger = logging.getLogger(__name__)

def should_continue(state: ReviewState) -> str:
    if state.get("has_critical_failure"):
        logger.warning("Critical failure detected — skipping to end")
        return "end"
    return "continue"

def build_graph():
    graph = StateGraph(ReviewState)

    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("bug_detector", bug_detection_node)
    graph.add_node("quality_checker", quality_check_node)
    graph.add_node("security_checker", security_check_node)
    graph.add_node("summarizer", summarizer_node)

    graph.set_entry_point("orchestrator")

    graph.add_conditional_edges(
    "orchestrator",
    should_continue,
    {
        "continue": "bug_detector",
        "end": END
    }
)

    graph.add_edge("orchestrator", "quality_checker")
    graph.add_edge("orchestrator", "security_checker")

    graph.add_edge("bug_detector", "summarizer")
    graph.add_edge("quality_checker", "summarizer")
    graph.add_edge("security_checker", "summarizer")
    graph.add_edge("summarizer", END)

    return graph.compile()

review_graph = build_graph()
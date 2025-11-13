# graphs/m4_evolucion/graph.py

import logging
from typing import TypedDict, List, Optional, Dict, Any

from langgraph.graph import StateGraph, END

from core.utils import timed_node

from .nodes.extract_course_data import extract_course_data_node
from .nodes.analyze_prompts import analyze_prompts_node
from .nodes.detect_success_patterns import detect_success_patterns_node
from .nodes.register_metrics import register_metrics_node
from .nodes.generate_rules import generate_rules_node
from .nodes.update_knowledge_base import update_knowledge_base_node
from .nodes.detect_gaps import detect_gaps_node
from .nodes.generate_additional_content import generate_additional_content_node
from .nodes.validate_content import validate_content_node
from .nodes.update_content import update_content_node

logger = logging.getLogger(__name__)


class M4State(TypedDict, total=False):
    prompt_raw: str
    course_data: Dict[str, Any]
    prompts_analysis: Dict[str, Any]

    success_patterns: Optional[Dict[str, Any]]
    metrics: Optional[Dict[str, Any]]
    rules: Optional[List[Dict[str, Any]]]

    gaps_detected: Optional[bool]
    gap_details: Optional[List[Dict[str, Any]]]

    generated_content: Optional[str]
    content_validated: Optional[bool]

    updated_content: Optional[str]
    report: Optional[str]


def gaps_router(state: M4State):
    return "GENERATE_CONTENT" if state.get("gaps_detected") else "END"


def validate_router(state: M4State):
    return "UPDATE_CONTENT" if state.get("content_validated") else "GENERATE_CONTENT"


def build_m4_graph():
    graph = StateGraph(M4State)

    graph.add_node("EXTRACT_COURSE_DATA", timed_node(extract_course_data_node))
    graph.add_node("ANALYZE_PROMPTS", timed_node(analyze_prompts_node))
    graph.add_node("DETECT_SUCCESS_PATTERNS", timed_node(detect_success_patterns_node))
    graph.add_node("REGISTER_METRICS", timed_node(register_metrics_node))
    graph.add_node("GENERATE_RULES", timed_node(generate_rules_node))
    graph.add_node("UPDATE_KB", timed_node(update_knowledge_base_node))
    graph.add_node("DETECT_GAPS", timed_node(detect_gaps_node))
    graph.add_node("GENERATE_CONTENT", timed_node(generate_additional_content_node))
    graph.add_node("VALIDATE_CONTENT", timed_node(validate_content_node))
    graph.add_node("UPDATE_CONTENT", timed_node(update_content_node))

    graph.set_entry_point("EXTRACT_COURSE_DATA")

    graph.add_edge("EXTRACT_COURSE_DATA", "ANALYZE_PROMPTS")
    graph.add_edge("ANALYZE_PROMPTS", "DETECT_SUCCESS_PATTERNS")
    graph.add_edge("DETECT_SUCCESS_PATTERNS", "REGISTER_METRICS")
    graph.add_edge("REGISTER_METRICS", "GENERATE_RULES")
    graph.add_edge("GENERATE_RULES", "UPDATE_KB")
    graph.add_edge("UPDATE_KB", "DETECT_GAPS")

    graph.add_conditional_edges(
        "DETECT_GAPS",
        gaps_router,
        {
            "GENERATE_CONTENT": "GENERATE_CONTENT",
            "END": END,
        }
    )

    graph.add_edge("GENERATE_CONTENT", "VALIDATE_CONTENT")

    graph.add_conditional_edges(
        "VALIDATE_CONTENT",
        validate_router,
        {
            "UPDATE_CONTENT": "UPDATE_CONTENT",
            "GENERATE_CONTENT": "GENERATE_CONTENT",
        }
    )

    graph.add_edge("UPDATE_CONTENT", END)

    logger.info("[GRAPH] Grafo M4 construido exitosamente")

    # SIN CHECKPOINTER
    return graph.compile()


m4_app = build_m4_graph()

# graphs/m4_evolucion/graph.py

from typing import TypedDict, List, Optional, Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from core.config import GRAPH_DB_PATH
from core.utils import timed_node

# Importa tus nodos del M4
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

# ---------------------------
# 1. DEFINICIÓN DEL ESTADO
# ---------------------------

class M4State(TypedDict, total=False):
    # Entradas
    prompt_raw: str
    course_data: Dict[str, Any]
    prompts_analysis: Dict[str, Any]

    # PATRONES EXITOSOS
    success_patterns: Optional[Dict[str, Any]]
    metrics: Optional[Dict[str, Any]]
    rules: Optional[List[Dict[str, Any]]]

    # DETECCIÓN DE BRECHAS
    gaps_detected: Optional[bool]
    gap_details: Optional[List[Dict[str, Any]]]

    # GENERACIÓN DE CONTENIDO
    generated_content: Optional[str]
    content_validated: Optional[bool]

    # SALIDAS
    updated_content: Optional[str]
    report: Optional[str]

# ---------------------------
# 2. FUNCIÓN PARA DECISIÓN
# ---------------------------

def gaps_router(state: M4State):
    """Define si se detectaron brechas o no."""
    if state.get("gaps_detected"):
        return "GENERATE_CONTENT"
    return "END"

def validate_router(state: M4State):
    """Define si el contenido está validado o debe regenerarse."""
    if state.get("content_validated"):
        return "UPDATE_CONTENT"
    return "GENERATE_CONTENT"

# ---------------------------
# 3. ENSAMBLADO DEL GRAPH
# ---------------------------

def build_graph():
    workflow = StateGraph(M4State)

    # NODOS SEGÚN TU BPMN
    workflow.add_node("EXTRACT_COURSE_DATA", timed_node(extract_course_data_node))
    workflow.add_node("ANALYZE_PROMPTS", timed_node(analyze_prompts_node))
    workflow.add_node("DETECT_SUCCESS_PATTERNS", timed_node(detect_success_patterns_node))
    workflow.add_node("REGISTER_METRICS", timed_node(register_metrics_node))
    workflow.add_node("GENERATE_RULES", timed_node(generate_rules_node))
    workflow.add_node("UPDATE_KB", timed_node(update_knowledge_base_node))
    workflow.add_node("DETECT_GAPS", timed_node(detect_gaps_node))
    workflow.add_node("GENERATE_CONTENT", timed_node(generate_additional_content_node))
    workflow.add_node("VALIDATE_CONTENT", timed_node(validate_content_node))
    workflow.add_node("UPDATE_CONTENT", timed_node(update_content_node))

    # ---------------------------
    # 4. DEFINICIÓN DEL FLUJO BPMN
    # ---------------------------

    workflow.set_entry_point("EXTRACT_COURSE_DATA")

    workflow.add_edge("EXTRACT_COURSE_DATA", "ANALYZE_PROMPTS")
    workflow.add_edge("ANALYZE_PROMPTS", "DETECT_SUCCESS_PATTERNS")
    workflow.add_edge("DETECT_SUCCESS_PATTERNS", "REGISTER_METRICS")
    workflow.add_edge("REGISTER_METRICS", "GENERATE_RULES")
    workflow.add_edge("GENERATE_RULES", "UPDATE_KB")
    workflow.add_edge("UPDATE_KB", "DETECT_GAPS")

    # Condición: ¿hay brechas?
    workflow.add_conditional_edges("DETECT_GAPS", gaps_router, {
        "GENERATE_CONTENT": "GENERATE_CONTENT",
        "END": END
    })

    # Si se genera contenido, validarlo
    workflow.add_edge("GENERATE_CONTENT", "VALIDATE_CONTENT")

    # Validación → ¿está bien o falta mejorar?
    workflow.add_conditional_edges("VALIDATE_CONTENT", validate_router, {
        "UPDATE_CONTENT": "UPDATE_CONTENT",
        "GENERATE_CONTENT": "GENERATE_CONTENT"
    })

    # FIN
    workflow.add_edge("UPDATE_CONTENT", END)

    # ---------------------------
    # 5. CHECKPOINTS (igual que M1)
    # ---------------------------

    memory = SqliteSaver.from_file(GRAPH_DB_PATH)
    return workflow.compile(checkpointer=memory)

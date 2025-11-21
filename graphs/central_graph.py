# graphs/central_graph.py
#m1
from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from graphs.m1_interaccion.nodes.nlp import nlp_node
from graphs.m1_interaccion.nodes.clarify import clarify_decide, ask_node
from graphs.m1_interaccion.nodes.mapping import map_node
from graphs.m1_interaccion.nodes.syllabus import syllabus_node
from graphs.m1_interaccion.nodes.pricing import pricing_node
from graphs.m1_interaccion.nodes.proposal import proposal_node, approval_router
#m4
from graphs.m4_evolucion.nodes.extract_course_data import extract_course_data
from graphs.m4_evolucion.nodes.analyze_prompts import analyze_prompts
from graphs.m4_evolucion.nodes.detect_success_patterns import detect_success_patterns
from graphs.m4_evolucion.nodes.register_metrics import register_metrics
from graphs.m4_evolucion.nodes.generate_rules import generate_rules
from graphs.m4_evolucion.nodes.detect_gaps import detect_gaps
from graphs.m4_evolucion.nodes.generate_additional_content import generate_additional_content
from graphs.m4_evolucion.nodes.validate_content import validate_content
from graphs.m4_evolucion.nodes.update_content import update_content
from graphs.m4_evolucion.nodes.update_knowledge_base import update_knowledge_base
from core.shared_memory_manager import SharedMemoryManager

# --- Importar M2 ---
from graphs.m2_creacion.graph import build_graph as build_m2_graph           # grafo de M2 :contentReference[oaicite:1]{index=1}
from graphs.m2_creacion.adapter import m1_to_m2_input                        # adaptador M1→M2 :contentReference[oaicite:2]{index=2}

# Compilamos el grafo de M2 una sola vez
M2_APP = build_m2_graph()



# Definimos el estado para el macroproceso 1
class M1State(Dict[str, Any]):
    prompt_raw: str
    entidades: Dict[str, Any]
    confianza_nlp: float
    requiere_clarificacion: bool
    preguntas: List[str]
    respuestas: List[str]
    mapping: Dict[str, Any]
    syllabus: Dict[str, Any]
    precio: Dict[str, Any]
    propuesta_html: str
    decision: Optional[str]
    metricas: Dict[str, Any]
    historial: List[Dict[str, Any]]


# Modificar el nodo NLP para usar memoria compartida
def nlp_node_with_shared_memory(state, config):
    # Crear un objeto de memoria compartida
    shm_manager = SharedMemoryManager(size=1024)  # Ajusta el tamaño según el estado
    # Guardar el estado inicial en memoria compartida
    shm_manager.write(state)

    # Aquí se procesan los datos del nodo (ejemplo de procesamiento)
    state['prompt_raw'] = "Texto procesado en NLP"
    state['confianza_nlp'] = 0.98

    # Guardar el nuevo estado en la memoria compartida
    shm_manager.write(state)

    return state

def build_graph():
    g = StateGraph(M1State)

    # Agregar nodos
    g.add_node("NLP", nlp_node)
    g.add_node("ASK", ask_node)
    g.add_node("MAP", map_node)
    g.add_node("SYLLABUS", syllabus_node)
    g.add_node("PRICING", pricing_node)
    g.add_node("PROPOSAL", proposal_node)

    # Definir punto de entrada
    g.set_entry_point("NLP")

    # Flujos entre nodos
    g.add_conditional_edges("NLP", clarify_decide, {"ASK": "ASK", "MAP": "MAP"})
    g.add_edge("ASK", END)  # Sin bucles
    g.add_edge("MAP", "SYLLABUS")
    g.add_edge("SYLLABUS", "PRICING")
    g.add_edge("PRICING", "PROPOSAL")
    g.add_conditional_edges("PROPOSAL", approval_router, {"WAIT": END, "ASK": END, "END": END})

    # Compilamos el grafo sin el checkpoint
    return g.compile()



# Aquí enganchamos M2:
    # - WAIT  → termina
    # - ASK   → vuelve a ASK (para mantener tu flujo de aclaración)
    # - M2    → ejecuta el grafo del Macroproceso 2
    g.add_conditional_edges(
        "PROPOSAL",
        approval_router_ext,
        {
            "WAIT": END,
            "ASK": "ASK",
            "M2": "M2",
        },
    )

    # Después de ejecutar M2, terminamos (puedes cambiar esto luego si quieres seguir a M3/M4)
    g.add_edge("M2", END)

    return g.compile()


#MACROPROCESO 4
class M4State(Dict[str, Any]):
    """
    Estado para el Macroproceso 4 – Evolución de Contenido.
    Este estado incluye tanto los campos "principales"
    como los campos intermedios que escriben los nodos.
    """

    # Campos principales del curso y flujo
    course_id: Optional[str]
    course_data: Dict[str, Any]
    prompts_history: List[Dict[str, Any]]
    metrics: Dict[str, Any]
    success_patterns: Dict[str, Any]
    rules: List[Dict[str, Any]]
    gaps: List[Dict[str, Any]]
    additional_content: List[Dict[str, Any]]
    validation_result: Dict[str, Any]
    updated_content: Dict[str, Any]
    knowledge_base_updates: List[Dict[str, Any]]

    # Campos que realmente escriben tus nodos (intermedios)
    prompts_analysis: Dict[str, Any]
    gaps_detected: bool
    gap_details: List[Dict[str, Any]]
    generated_content: str
    content_validated: bool
    validation_score: float
    message: str
    report: str


def build_m4_graph():
    g = StateGraph(M4State)

    # Orden lineal de tus nodos del M4
    g.add_node("EXTRACT_COURSE_DATA", extract_course_data)
    g.add_node("ANALYZE_PROMPTS", analyze_prompts)
    g.add_node("DETECT_SUCCESS_PATTERNS", detect_success_patterns)
    g.add_node("REGISTER_METRICS", register_metrics)
    g.add_node("GENERATE_RULES", generate_rules)
    g.add_node("DETECT_GAPS", detect_gaps)
    g.add_node("GENERATE_ADDITIONAL_CONTENT", generate_additional_content)
    g.add_node("VALIDATE_CONTENT", validate_content)
    g.add_node("UPDATE_CONTENT", update_content)
    g.add_node("UPDATE_KNOWLEDGE_BASE", update_knowledge_base)

    # Punto de entrada del M4
    g.set_entry_point("EXTRACT_COURSE_DATA")

    # Flujo completo tal como lo tenías en tu proyecto anterior
    g.add_edge("EXTRACT_COURSE_DATA", "ANALYZE_PROMPTS")
    g.add_edge("ANALYZE_PROMPTS", "DETECT_SUCCESS_PATTERNS")
    g.add_edge("DETECT_SUCCESS_PATTERNS", "REGISTER_METRICS")
    g.add_edge("REGISTER_METRICS", "GENERATE_RULES")
    g.add_edge("GENERATE_RULES", "DETECT_GAPS")
    g.add_edge("DETECT_GAPS", "GENERATE_ADDITIONAL_CONTENT")
    g.add_edge("GENERATE_ADDITIONAL_CONTENT", "VALIDATE_CONTENT")
    g.add_edge("VALIDATE_CONTENT", "UPDATE_CONTENT")
    g.add_edge("UPDATE_CONTENT", "UPDATE_KNOWLEDGE_BASE")
    g.add_edge("UPDATE_KNOWLEDGE_BASE", END)

    return g.compile()

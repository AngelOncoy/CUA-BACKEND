# graphs/central_graph.py

from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END

# ============================
#           M1
# ============================
from graphs.m1_interaccion.nodes.nlp import nlp_node
from graphs.m1_interaccion.nodes.clarify import clarify_decide, ask_node
from graphs.m1_interaccion.nodes.mapping import map_node
from graphs.m1_interaccion.nodes.syllabus import syllabus_node
from graphs.m1_interaccion.nodes.pricing import pricing_node
from graphs.m1_interaccion.nodes.proposal import proposal_node, approval_router

# ============================
#           M2
# ============================
from graphs.m2_creacion.graph import build_graph as build_m2_graph
from graphs.m2_creacion.adapter import m1_to_m2_input
M2_APP = build_m2_graph()

# ============================
#           M3
# ============================
from graphs.m3_entrega.nodes.publicacion import publicar_en_lms
from graphs.m3_entrega.nodes.notificacion import enviar_notificaciones
from graphs.m3_entrega.nodes.asignacion import asignar_empleados
from graphs.m3_entrega.nodes.gamificacion import preparar_gamificacion
from graphs.m3_entrega.nodes.monitoreo import generar_analytics
from graphs.m3_entrega.nodes.certificacion import generar_certificados
from graphs.m3_entrega.nodes.utils import inicializar_estado as m3_inicializar

# ============================
#           M4
# ============================
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


# ============================
#      ESTADO GLOBAL
# ============================
class M1State(Dict[str, Any]):
    # M1 Core
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

    # M3 fields
    m3_publicado: bool
    certificados: List[Dict[str, Any]]
    gamificacion: Dict[str, Any]
    analytics: Dict[str, Any]

    # M4 fields
    course_data: Dict[str, Any]
    prompts_analysis: Dict[str, Any]
    success_patterns: Dict[str, Any]
    gaps: List[Dict[str, Any]]
    additional_content: List[Dict[str, Any]]
    updated_content: Dict[str, Any]


# ============================
#       GRAFO PRINCIPAL
# ============================
def build_graph():
    g = StateGraph(M1State)

    # -------------------------
    #          M1
    # -------------------------
    g.add_node("NLP", nlp_node)
    g.add_node("ASK", ask_node)
    g.add_node("MAP", map_node)
    g.add_node("SYLLABUS", syllabus_node)
    g.add_node("PRICING", pricing_node)
    g.add_node("PROPOSAL", proposal_node)

    g.set_entry_point("NLP")

    g.add_conditional_edges("NLP", clarify_decide, {
        "ASK": "ASK",
        "MAP": "MAP"
    })

    g.add_edge("ASK", END)
    g.add_edge("MAP", "SYLLABUS")
    g.add_edge("SYLLABUS", "PRICING")
    g.add_edge("PRICING", "PROPOSAL")

    g.add_conditional_edges("PROPOSAL", approval_router, {
        "WAIT": END,
        "ASK": "ASK",
        "END": END,
        "M2": "M2"
    })

    # -------------------------
    #          M2
    # -------------------------
    g.add_node("M2", M2_APP)
    g.add_edge("M2", "M3_INICIALIZAR")

    # -------------------------
    #          M3
    # -------------------------
    g.add_node("M3_INICIALIZAR", m3_inicializar)
    g.add_node("M3_PUBLICAR", publicar_en_lms)
    g.add_node("M3_NOTIFICAR", enviar_notificaciones)
    g.add_node("M3_ASIGNAR", asignar_empleados)
    g.add_node("M3_GAMIFICAR", preparar_gamificacion)
    g.add_node("M3_MONITOREAR", generar_analytics)
    g.add_node("M3_CERTIFICAR", generar_certificados)

    g.add_edge("M3_INICIALIZAR", "M3_PUBLICAR")
    g.add_edge("M3_PUBLICAR", "M3_NOTIFICAR")
    g.add_edge("M3_NOTIFICAR", "M3_ASIGNAR")
    g.add_edge("M3_ASIGNAR", "M3_GAMIFICAR")
    g.add_edge("M3_GAMIFICAR", "M3_MONITOREAR")
    g.add_edge("M3_MONITOREAR", "M3_CERTIFICAR")

    # -------------------------
    #          M4
    # -------------------------
    g.add_node("M4_EXTRACT", extract_course_data)
    g.add_node("M4_ANALYZE", analyze_prompts)
    g.add_node("M4_SUCCESS", detect_success_patterns)
    g.add_node("M4_METRICS", register_metrics)
    g.add_node("M4_RULES", generate_rules)
    g.add_node("M4_GAPS", detect_gaps)
    g.add_node("M4_ADDITIONAL", generate_additional_content)
    g.add_node("M4_VALIDATE", validate_content)
    g.add_node("M4_UPDATE_CONTENT", update_content)
    g.add_node("M4_KB", update_knowledge_base)

    g.add_edge("M3_CERTIFICAR", "M4_EXTRACT")
    g.add_edge("M4_EXTRACT", "M4_ANALYZE")
    g.add_edge("M4_ANALYZE", "M4_SUCCESS")
    g.add_edge("M4_SUCCESS", "M4_METRICS")
    g.add_edge("M4_METRICS", "M4_RULES")
    g.add_edge("M4_RULES", "M4_GAPS")
    g.add_edge("M4_GAPS", "M4_ADDITIONAL")
    g.add_edge("M4_ADDITIONAL", "M4_VALIDATE")
    g.add_edge("M4_VALIDATE", "M4_UPDATE_CONTENT")
    g.add_edge("M4_UPDATE_CONTENT", "M4_KB")
    g.add_edge("M4_KB", END)

    # -------------------------
    #         COMPILAR
    # -------------------------
    return g.compile()

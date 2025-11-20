# graphs/central_graph.py
from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from graphs.m1_interaccion.nodes.nlp import nlp_node
from graphs.m1_interaccion.nodes.clarify import clarify_decide, ask_node
from graphs.m1_interaccion.nodes.mapping import map_node
from graphs.m1_interaccion.nodes.syllabus import syllabus_node
from graphs.m1_interaccion.nodes.pricing import pricing_node
from graphs.m1_interaccion.nodes.proposal import proposal_node, approval_router

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

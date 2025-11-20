# graphs/central_graph,py

from typing import TypedDict, Optional, List, Dict, Any
from langgraph.graph import StateGraph, END
from graphs.m1_interaccion.nodes.nlp import nlp_node
from graphs.m1_interaccion.nodes.clarify import clarify_decide, ask_node
from graphs.m1_interaccion.nodes.mapping import map_node
from graphs.m1_interaccion.nodes.syllabus import syllabus_node
from graphs.m1_interaccion.nodes.pricing import pricing_node
from graphs.m1_interaccion.nodes.proposal import proposal_node, approval_router
from core.config import GRAPH_DB_PATH
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

# Definimos el estado para el macroproceso 1
class M1State(TypedDict, total=False):
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
    # Inicializamos el grafo con el estado M1State
    g = StateGraph(M1State)

    # Agregar los nodos del Macroproceso 1
    g.add_node("NLP", nlp_node)
    g.add_node("ASK", ask_node)
    g.add_node("MAP", map_node)
    g.add_node("SYLLABUS", syllabus_node)
    g.add_node("PRICING", pricing_node)
    g.add_node("PROPOSAL", proposal_node)

    # Definir el punto de entrada del grafo
    g.set_entry_point("NLP")

    # Definir el flujo entre los nodos
    g.add_conditional_edges("NLP", clarify_decide, {"ASK": "ASK", "MAP": "MAP"})
    g.add_edge("ASK", END)             # Devuelve preguntas → sin bucle
    g.add_edge("MAP", "SYLLABUS")
    g.add_edge("SYLLABUS", "PRICING")
    g.add_edge("PRICING", "PROPOSAL")
    g.add_conditional_edges("PROPOSAL", approval_router, {"WAIT": END, "ASK": END, "END": END})

    # Conexión con la base de datos para persistencia del estado
    conn = sqlite3.connect(GRAPH_DB_PATH, check_same_thread=False)
    checkpointer = SqliteSaver(conn)

    # Compilamos el grafo con el punto de control
    return g.compile(checkpointer=checkpointer)

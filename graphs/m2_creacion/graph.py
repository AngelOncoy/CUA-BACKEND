# graphs/m2_creacion/central_graph.py
from typing import Dict, Any
from langgraph.graph import StateGraph, END

# Importar todos los nodos del M2
from graphs.m2_creacion.nodes import (
    objectives,
    mapping,
    retrieval,
    authoring,
    media,
    assessments,
    qc,
    assembler,
    notify
)

def build_graph() -> StateGraph:
    """
    Construye el grafo de ejecución completo del Macroproceso M2:
    objectives → mapping → retrieval → authoring → media → assessments → qc → assembler → notify
    """
    g = StateGraph(Dict[str, Any])

    # Registrar nodos
    g.add_node("objectives", objectives.run)
    g.add_node("mapping", mapping.run)
    g.add_node("retrieval", retrieval.run)
    g.add_node("authoring", authoring.run)
    g.add_node("media", media.run)
    g.add_node("assessments", assessments.run)
    g.add_node("qc", qc.run)
    g.add_node("assembler", assembler.run)
    g.add_node("notify", notify.run)

    # Secuencia de flujo
    g.set_entry_point("objectives")
    g.add_edge("objectives", "mapping")
    g.add_edge("mapping", "retrieval")
    g.add_edge("retrieval", "authoring")
    g.add_edge("authoring", "media")
    g.add_edge("media", "assessments")
    g.add_edge("assessments", "qc")
    g.add_edge("qc", "assembler")
    g.add_edge("assembler", "notify")
    g.add_edge("notify", END)

    return g.compile()
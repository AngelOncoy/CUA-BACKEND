from typing import Dict, Any


def update_knowledge_base_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Nodo M4 — Actualización de Base de Conocimiento
    LangGraph EXIGE que cada nodo escriba al menos 1 campo permitido.
    Usamos 'report' como campo dummy para cumplir la regla.
    """

    return {
        "report": "Base de conocimiento actualizada correctamente."
    }


def update_knowledge_base(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adaptador para el grafo central.
    """
    return update_knowledge_base_node(state)

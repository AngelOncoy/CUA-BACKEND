from typing import Dict, Any


def register_metrics_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    NODO M4 — REGISTRAR MÉTRICAS
    """
    metrics = {
        "kpi_participacion": 0.92,
        "kpi_satisfaccion": 0.95,
        "kpi_aprendizaje": 0.88
    }

    return {"metrics": metrics}


def register_metrics(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adaptador para el grafo central.
    """
    return register_metrics_node(state)

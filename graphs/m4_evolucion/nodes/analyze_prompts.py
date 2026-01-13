from typing import Dict, Any


def analyze_prompts_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    NODO M4 — ANALIZAR PROMPTS
    Datos simulados para caracterizar el uso de prompts.
    """
    analysis = {
        "errores_comunes": [
            "prompts demasiado generales",
            "falta de ejemplos concretos"
        ],
        "prompts_mas_usados": [
            "resume",
            "explica como si tuviera 10 años",
            "genera ejemplos"
        ],
        "nivel": "intermedio",
        "recomendaciones": [
            "incluir prompts avanzados",
            "reforzar la técnica de contexto"
        ]
    }

    return {"prompts_analysis": analysis}


def analyze_prompts(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adaptador para el grafo central.
    """
    return analyze_prompts_node(state)

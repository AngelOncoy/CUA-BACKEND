from typing import Dict, Any


def detect_success_patterns_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    NODO M4 — DETECTAR COMBINACIONES EXITOSAS
    """
    patterns = {
        "modulos_exitosos": ["Módulo 1: IA Aplicada", "Módulo 3: Taller Práctico"],
        "factores_exito": ["participación", "ejercicios prácticos"],
        "competencias_destacadas": ["creación de prompts", "razonamiento crítico"]
    }

    return {"success_patterns": patterns}


def detect_success_patterns(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adaptador para el grafo central.
    """
    return detect_success_patterns_node(state)

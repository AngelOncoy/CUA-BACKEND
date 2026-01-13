from typing import Dict, Any, List


def generate_rules_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    NODO M4 — GENERAR REGLAS
    """
    rules: List[Dict[str, str]] = [
        {"si": "participación alta", "entonces": "promover ejercicios colaborativos"},
        {"si": "evaluaciones bajas", "entonces": "reforzar teoría con ejemplos"},
        {"si": "poca práctica", "entonces": "agregar módulo de prompts avanzados"}
    ]

    return {"rules": rules}


def generate_rules(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adaptador para el grafo central.
    """
    return generate_rules_node(state)

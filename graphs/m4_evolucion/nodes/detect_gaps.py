from typing import Dict, Any


def detect_gaps_node(state: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "gaps_detected": True,
        "gap_details": [
            {
                "motivo": "Prueba controlada",
                "accion": "Generar contenido adicional"
            }
        ]
    }


def detect_gaps(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adaptador para el grafo central.
    """
    return detect_gaps_node(state)

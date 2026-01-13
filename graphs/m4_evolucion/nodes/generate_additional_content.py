from typing import Dict, Any


def generate_additional_content_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    NODO M4 — GENERAR CONTENIDO ADICIONAL
    Aquí no asumimos que gap_details tenga 'tema'.
    Generamos contenido basado en el motivo de la brecha.
    """

    gaps = state.get("gap_details", [])

    if not gaps:
        # Igual debemos escribir algo
        return {"generated_content": "No se encontraron brechas."}

    # Tomamos la primera brecha
    gap = gaps[0]

    motivo = gap.get("motivo", "tema desconocido")
    accion = gap.get("accion", "generar contenido")

    contenido = (
        f"Se ha detectado una brecha: {motivo}. "
        f"Por ello, se procede a {accion}. "
        "Aquí tienes un contenido introductorio generado automáticamente."
    )

    # SIEMPRE devolver una clave válida
    return {
        "generated_content": contenido
    }


def generate_additional_content(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adaptador para el grafo central.
    """
    return generate_additional_content_node(state)

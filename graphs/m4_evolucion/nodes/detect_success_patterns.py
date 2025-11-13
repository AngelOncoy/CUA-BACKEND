def detect_success_patterns_node(state):
    """
    NODO M4 — DETECTAR COMBINACIONES EXITOSAS
    """
    patterns = {
        "modulos_exitosos": ["Módulo 1: IA Aplicada", "Módulo 3: Taller Práctico"],
        "factores_exito": ["participación", "ejercicios prácticos"],
        "competencias_destacadas": ["creación de prompts", "razonamiento crítico"]
    }

    return {"success_patterns": patterns}

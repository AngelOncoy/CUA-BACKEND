def generate_rules_node(state):
    """
    NODO M4 — GENERAR REGLAS
    """
    rules = [
        {"si": "participación alta", "entonces": "promover ejercicios colaborativos"},
        {"si": "evaluaciones bajas", "entonces": "reforzar teoría con ejemplos"},
        {"si": "poca práctica", "entonces": "agregar módulo de prompts avanzados"}
    ]

    return {"rules": rules}

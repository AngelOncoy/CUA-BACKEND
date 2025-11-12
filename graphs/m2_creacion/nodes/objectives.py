from typing import Dict, Any, List

# Mapeo simple de nivel -> escalas Bloom sugeridas
BLOOM_BY_NIVEL = {
    "Basico": ["Recordar", "Comprender", "Aplicar"],
    "Básico": ["Recordar", "Comprender", "Aplicar"],
    "Intermedio": ["Aplicar", "Analizar", "Evaluar"],
    "Avanzado": ["Analizar", "Evaluar", "Crear"],
}

def _bloom_levels(nivel: str) -> List[str]:
    """Devuelve 3 niveles Bloom sugeridos según 'nivel'."""
    for k, v in BLOOM_BY_NIVEL.items():
        if k.lower() in (nivel or "").lower():
            return v
    # Por defecto
    return ["Comprender", "Aplicar", "Analizar"]

def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deriva objetivos para el curso y para cada módulo.
    Entradas esperadas:
      - state['entidades'] (dict)
      - state['input']['mapping']['modulos'] (list[dict])
    Salidas:
      - state['objetivos_aprendizaje'] (list[dict])
    """
    entidades = state.get("entidades", {})
    nivel = entidades.get("nivel", "Intermedio")
    competencias = entidades.get("competencias", [])

    # Módulos provenientes del adapter M1->M2
    modulos = (state.get("input", {}).get("mapping") or {}).get("modulos") or []

    blooms = _bloom_levels(nivel)
    objetivos: List[Dict[str, Any]] = []

    # ---- Objetivos globales del curso
    titulo_curso = (competencias[0] if competencias else "el curso")
    objetivos.append({
        "scope": "curso",
        "nivel_bloom": blooms[0],
        "descripcion": f"{blooms[0]} los fundamentos, el alcance y el contexto de {titulo_curso}."
    })
    objetivos.append({
        "scope": "curso",
        "nivel_bloom": blooms[1],
        "descripcion": f"{blooms[1]} escenarios y criterios técnicos para seleccionar enfoques adecuados en {titulo_curso}."
    })
    objetivos.append({
        "scope": "curso",
        "nivel_bloom": blooms[2],
        "descripcion": f"{blooms[2]} soluciones robustas, escalables y trazables que sigan buenas prácticas en {titulo_curso}."
    })

    # ---- Objetivos por módulo
    for m in modulos:
        titulo_mod = m.get("titulo", "Módulo")
        objetivos.append({
            "scope": "modulo",
            "modulo": titulo_mod,
            "nivel_bloom": blooms[0],
            "descripcion": f"{blooms[0]} conceptos clave y terminología del {titulo_mod}."
        })
        objetivos.append({
            "scope": "modulo",
            "modulo": titulo_mod,
            "nivel_bloom": blooms[1],
            "descripcion": f"{blooms[1]} casos de uso y riesgos habituales del {titulo_mod}."
        })

    state["objetivos_aprendizaje"] = objetivos
    return state
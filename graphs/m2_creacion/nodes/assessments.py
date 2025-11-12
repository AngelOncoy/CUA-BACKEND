from typing import Dict, Any, List
import re

# ---------------------------
# Helpers
# ---------------------------
def _norm(s: str) -> str:
    return (s or "").strip()

def _sentences(s: str) -> List[str]:
    if not s:
        return []
    parts = re.split(r'(?<=[.!?])\s+', s.strip())
    return [p for p in parts if p]

def _choose(lst: List[Any], n: int) -> List[Any]:
    if not lst:
        return []
    if len(lst) <= n:
        return lst[:]
    # selección determinística: saltos uniformes
    step = max(1, len(lst)//n)
    out = []
    i = 0
    while len(out) < n and i < len(lst):
        out.append(lst[i])
        i += step
    # completar si faltan
    j = 1
    while len(out) < n and j < len(lst):
        if lst[j] not in out:
            out.append(lst[j])
        j += 1
    return out[:n]

def _first_words(s: str, n_words: int = 10) -> str:
    words = _norm(s).split()
    return " ".join(words[:n_words])

def _fallback_objs_modulo(state, mod_title: str) -> List[str]:
    """Si no existe objetivos_m2, genera 3 genéricos."""
    base = mod_title.lower()
    return [
        f"Explicar conceptos clave de {base}.",
        f"Diseñar un artefacto o flujo aplicando buenas prácticas en {base}.",
        f"Evaluar riesgos habituales y criterios de calidad en {base}."
    ]

def _get_objetivos_modulo(state, mod_title: str) -> List[str]:
    objs = (state.get("objetivos_m2") or {}).get("modulos") or []
    for m in objs:
        if _norm(m.get("modulo")) == _norm(mod_title):
            out = [o for o in (m.get("objetivos") or []) if _norm(o)]
            return out if out else _fallback_objs_modulo(state, mod_title)
    return _fallback_objs_modulo(state, mod_title)

# ---------------------------
# Generadores de preguntas
# ---------------------------
def _mk_truefalse_from_point(texto: str, make_false: bool = False) -> Dict[str, Any]:
    stem = _first_words(texto, 20).rstrip(".") + "."
    if make_false:
        stem = stem.replace(" siempre ", " ").replace(" nunca ", " ")
        stem = stem + " (Afirmación: siempre aplica sin excepciones.)"
    return {"tipo": "vf", "enunciado": stem, "respuesta": (not make_false)}

def _mk_mcq_from_point(texto: str) -> Dict[str, Any]:
    core = _first_words(texto, 16)
    stem = f"¿Cuál de las siguientes opciones describe mejor: “{core}…”?"
    correct = f"{core} (correcto)"
    distractors = [
        f"{core} (incompleto)",
        f"{core} (caso específico)",
        f"No relacionado con {core}"
    ]
    opciones = [correct] + distractors
    # determinístico: no aleatorizar
    return {"tipo": "mcq", "enunciado": stem, "opciones": opciones, "correcta": 0}

def _mk_items_from_sources(key_points: List[str],
                           procedures: List[Dict[str, Any]],
                           pitfalls: List[str],
                           target_n: int = 10) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []

    # 1) VF desde key_points (dos verdaderas y una falsa si hay material)
    for kp in _choose(key_points, 3):
        items.append(_mk_truefalse_from_point(kp, make_false=False))
    if key_points:
        items.append(_mk_truefalse_from_point(key_points[0], make_false=True))

    # 2) MCQ desde key_points (2)
    for kp in _choose(key_points, 2):
        items.append(_mk_mcq_from_point(kp))

    # 3) MCQ desde procedimientos (títulos)
    for p in _choose(procedures, 2):
        title = _norm(p.get("title") or p.get("titulo") or "Procedimiento")
        items.append(_mk_mcq_from_point(title))

    # 4) VF desde errores/pitfalls (2)
    for pit in _choose(pitfalls, 2):
        items.append(_mk_truefalse_from_point(pit, make_false=False))

    # recorte/ajuste a target_n
    return items[:target_n]

# ---------------------------
# Rúbrica y proyecto
# ---------------------------
def _mk_rubric_and_project(mod_title: str, objetivos_mod: List[str]) -> Dict[str, Any]:
    criterios = [
        {"criterio": "Alineación a objetivos del módulo", "peso": 25, "descripcion": "El entregable aborda los objetivos declarados y evidencia su cumplimiento."},
        {"criterio": "Corrección técnica", "peso": 25, "descripcion": "Decisiones justificadas; flujo/artefacto funciona según requerimientos."},
        {"criterio": "Buenas prácticas y trazabilidad", "peso": 20, "descripcion": "Uso de convenciones, documentación breve y trazabilidad básica."},
        {"criterio": "Pruebas y validación", "peso": 15, "descripcion": "Evidencia de pruebas (casos, datos, resultados) y criterios de aceptación."},
        {"criterio": "Presentación y claridad", "peso": 15, "descripcion": "Entregables ordenados, nomenclatura, lectura y comunicación efectiva."}
    ]
    total = sum(c["peso"] for c in criterios)
    if total != 100:
        # Normaliza si se edita la rúbrica
        factor = 100 / total
        for c in criterios:
            c["peso"] = round(c["peso"] * factor)

    proyecto = {
        "titulo": f"Mini-proyecto del {mod_title}",
        "enunciado": (
            f"Desarrolla un artefacto o flujo relacionado con {mod_title.lower()}, "
            f"alineado a los objetivos del módulo. Incluye breve documentación, decisiones técnicas y al menos un caso de prueba."
        ),
        "entregables": [
            "Artefacto/flujo funcional (archivos o capturas).",
            "Documento breve (1-2 páginas) con decisiones y justificación.",
            "Evidencias de prueba: datos de entrada/salida y criterios de aceptación."
        ],
        "criterios_rubrica": criterios
    }
    return {"rubrica": criterios, "proyecto": proyecto}

# ---------------------------
# Nodo principal
# ---------------------------
def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Genera evaluaciones sumativas por módulo:
    - Quiz (VF + MCQ)
    - Mini-proyecto
    - Rúbrica
    - Alineación objetivos → ítems → criterios
    Lee: state['curso_m2_multimedia'] (o 'curso_m2'), state['objetivos_m2'] (opcional)
    Escribe: state['evaluaciones_m2']
    """
    curso = state.get("curso_m2_multimedia") or state.get("curso_m2")
    if not curso:
        raise ValueError("Falta curso_m2 o curso_m2_multimedia en el estado. Ejecuta authoring/media antes.")

    evaluaciones = {"modulos": []}

    for m in (curso.get("modulos") or []):
        mod_title = _norm(m.get("titulo") or "Módulo")
        objetivos_mod = _get_objetivos_modulo(state, mod_title)

        # Unir fuentes para generar ítems
        # Tomamos de la primera lección (representativa) y luego fallback
        lecciones = m.get("lecciones") or []
        key_points, procedures, pitfalls = [], [], []
        for l in lecciones:
            cc = l.get("contenido") or {}
            key_points.extend(cc.get("conceptos_clave") or [])
            procedures.extend(cc.get("procedimientos") or [])
            pitfalls.extend(cc.get("errores_comunes") or [])

        key_points = [_norm(k) for k in key_points if _norm(k)]
        procedures = [p for p in procedures if isinstance(p, dict)]
        pitfalls = [_norm(p) for p in pitfalls if _norm(p)]

        quiz_items = _mk_items_from_sources(key_points, procedures, pitfalls, target_n=10)
        alinh = {
            "objetivos": objetivos_mod,
            "quiz_map": [{"item_idx": i, "relacion": "cubre conceptos/skills generales del módulo"} for i in range(len(quiz_items))],
        }

        rubric_proj = _mk_rubric_and_project(mod_title, objetivos_mod)

        evaluaciones["modulos"].append({
            "modulo": mod_title,
            "objetivos": objetivos_mod,
            "quiz": {"items": quiz_items},
            "proyecto": rubric_proj["proyecto"],
            "rubrica": rubric_proj["rubrica"],
            "alineacion": alinh
        })

    state["evaluaciones_m2"] = evaluaciones
    return state
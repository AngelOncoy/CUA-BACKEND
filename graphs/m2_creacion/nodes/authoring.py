from typing import Dict, Any, List
import math
import re

def _norm_txt(s: str) -> str:
    return (s or "").strip()

def _sentences(s: str) -> List[str]:
    s = _norm_txt(s)
    if not s:
        return []
    # split suave por puntos
    parts = re.split(r'(?<=[.!?])\s+', s)
    return [p.strip() for p in parts if p.strip()]

def _choose_n(lst: List[Any], n: int) -> List[Any]:
    if not lst:
        return []
    if len(lst) <= n:
        return lst
    # reparto simple sin aleatoriedad: tomar cada k-ésimo
    k = max(1, len(lst) // n)
    out, i = [], 0
    while len(out) < n and i < len(lst):
        out.append(lst[i])
        i += k
    # si faltan por redondeo, completar
    idx = 1
    while len(out) < n and idx < len(lst):
        if lst[idx] not in out:
            out.append(lst[idx])
        idx += 1
    return out[:n]

def _heuristic_lessons(horas: int) -> int:
    """1 lección/6h aprox; mínimo 2, máximo 6."""
    if horas is None:
        return 2
    try:
        h = int(horas)
    except Exception:
        h = 8
    n = max(2, math.ceil(h / 6))
    return min(n, 6)

def _bloom_objective(mod_title: str, focus: str) -> str:
    return f"Al finalizar, el estudiante será capaz de {focus} dentro de {mod_title.lower()}."

def _mk_objectives(mod_title: str, key_points: List[str]) -> List[str]:
    # 3 objetivos genéricos apoyados en bullets
    verbs = ["analizar", "aplicar", "evaluar", "diseñar", "optimizar", "documentar"]
    obj = []
    if key_points:
        obj.append(_bloom_objective(mod_title, f"explicar {key_points[0].lower()}"))
    obj.append(_bloom_objective(mod_title, "diseñar un flujo/artefacto siguiendo buenas prácticas"))
    if len(key_points) > 1:
        obj.append(_bloom_objective(mod_title, f"evaluar riesgos asociados a {key_points[1].lower()}"))
    if len(obj) < 3:
        obj.append(_bloom_objective(mod_title, f"{verbs[len(key_points)%len(verbs)]} un caso práctico"))
    return obj[:3]

def _mk_tf_from_point(point: str) -> Dict[str, Any]:
    # statement VF sencillo: afirmación positiva
    stmt = f"{point.rstrip('.')}."
    # Regla: 2 verdaderas, 1 falsa por lección (se controlará afuera)
    return {"tipo": "vf", "enunciado": stmt, "respuesta": True}

def _mk_false_from_point(point: str) -> Dict[str, Any]:
    # niega suavemente con un “siempre”/“nunca” para hacerla falsa
    base = point.rstrip(".")
    stmt = f"{base} siempre se aplica sin excepciones."
    return {"tipo": "vf", "enunciado": stmt, "respuesta": False}

def _chunk_for_lessons(items: List[Any], n_lessons: int) -> List[List[Any]]:
    """Particiona items en n listas consecutivas de tamaño equilibrado."""
    chunks = [[] for _ in range(n_lessons)]
    if not items:
        return chunks
    for i, it in enumerate(items):
        chunks[i % n_lessons].append(it)
    return chunks

def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Authoring determinístico (sin LLM):
    - Lee: state['syllabus_detallado'] (modulos con 'horas'), state['assets'] (synthesis, referencias)
    - Escribe: state['curso_m2'] con estructura de curso para publicación
    """
    syllabus = state.get("syllabus_detallado", {}) or {}
    assets = state.get("assets", []) or []

    # Mapear horas por módulo para autoría
    horas_por_mod = {}
    for m in syllabus.get("modulos", []):
        horas_por_mod[_norm_txt(m.get("titulo",""))] = m.get("horas")

    curso_out = {
        "titulo": syllabus.get("curso") or "Curso generado",
        "nivel": syllabus.get("nivel") or "Avanzado",
        "modulos": []
    }

    for asset in assets:
        mod_title = _norm_txt(asset.get("modulo","Módulo"))
        syn = asset.get("synthesis", {}) or {}
        refs = asset.get("referencias", []) or []

        overview = _norm_txt(syn.get("overview",""))
        key_points = [k for k in (syn.get("key_points") or []) if _norm_txt(k)]
        procedures = [p for p in (syn.get("procedures") or []) if isinstance(p, dict)]
        pitfalls = [p for p in (syn.get("pitfalls") or []) if _norm_txt(p)]
        examples = [e for e in (syn.get("examples") or []) if isinstance(e, dict)]
        glossary = [g for g in (syn.get("glossary") or []) if isinstance(g, dict)]
        faq = [q for q in (syn.get("faq") or []) if isinstance(q, dict)]

        n_lessons = _heuristic_lessons(horas_por_mod.get(mod_title))
        # Distribuir contenidos en lecciones
        kp_chunks = _chunk_for_lessons(key_points, n_lessons) if key_points else [[] for _ in range(n_lessons)]
        proc_chunks = _chunk_for_lessons(procedures, n_lessons) if procedures else [[] for _ in range(n_lessons)]
        pit_chunks = _chunk_for_lessons(pitfalls, n_lessons) if pitfalls else [[] for _ in range(n_lessons)]
        ex_chunks = _chunk_for_lessons(examples, n_lessons) if examples else [[] for _ in range(n_lessons)]

        # Glosario único por módulo (se adjunta completo en cada lección para simplicidad)
        gl_terms = [{"term": _norm_txt(g.get("term")), "definition": _norm_txt(g.get("definition"))} for g in glossary if _norm_txt(g.get("term"))]

        # Armar lecciones
        lecciones = []
        for i in range(n_lessons):
            lp = kp_chunks[i]
            lproc = proc_chunks[i]
            lpit = pit_chunks[i]
            lex = ex_chunks[i]

            # Título de lección
            title_bits = []
            if lp:
                title_bits.append(lp[0])
            elif lproc:
                title_bits.append(_norm_txt(lproc[0].get("title","Procedimiento")))
            elif lpit:
                title_bits.append(f"Errores frecuentes #{i+1}")
            else:
                title_bits.append(f"Lección {i+1}")
            lesson_title = f"{mod_title} — {title_bits[0][:80]}"

            # Objetivos (Bloom-lite)
            objetivos = _mk_objectives(mod_title, lp or key_points)

            # Contenido
            introduccion = overview if i == 0 else ""
            conceptos = lp if lp else _choose_n(key_points, 3)
            procedimientos = []
            for p in lproc if lproc else _choose_n(procedures, min(2, len(procedures))):
                procedimientos.append({
                    "titulo": _norm_txt(p.get("title","Procedimiento")),
                    "pasos": [s for s in (p.get("steps") or []) if _norm_txt(s)] or ["Paso 1","Paso 2","Paso 3"]
                })
            ejemplos = []
            for e in lex if lex else _choose_n(examples, min(2, len(examples))):
                ejemplos.append({
                    "titulo": _norm_txt(e.get("title","Ejemplo")),
                    "descripcion": _norm_txt(e.get("description","Descripción breve"))
                })
            errores = lpit if lpit else _choose_n(pitfalls, min(3, len(pitfalls)))

            # Actividad práctica
            actividad = "Desarrolla un mini-flujo o artefacto que aplique los conceptos clave de esta lección. Documenta decisiones y prueba al menos un caso."

            # Evaluación formativa (3 V/F: 2 verdaderas + 1 falsa)
            eval_items = []
            base_points = conceptos if conceptos else (key_points[:3] if key_points else [])
            for idx, pt in enumerate(_choose_n(base_points, 3)):
                if idx == 2:
                    eval_items.append(_mk_false_from_point(pt))
                else:
                    eval_items.append(_mk_tf_from_point(pt))

            # Lecturas sugeridas (solo título+url si hay)
            lecturas = []
            for r in refs[:5]:
                if r.get("url"):
                    lecturas.append({"titulo": _norm_txt(r.get("titulo") or r.get("fuente") or "Lectura sugerida"),
                                     "url": r["url"]})

            lecciones.append({
                "titulo": lesson_title,
                "objetivos": objetivos,
                "contenido": {
                    "introduccion": introduccion,
                    "conceptos_clave": conceptos,
                    "procedimientos": procedimientos,
                    "ejemplos": ejemplos,
                    "errores_comunes": errores,
                    "glosario": gl_terms
                },
                "actividad_practica": actividad,
                "evaluacion_formativa": eval_items,
                "lecturas_sugeridas": lecturas
            })

        # FAQ del módulo
        faqs = [{"q": _norm_txt(q.get("q","Pregunta frecuente")), "a": _norm_txt(q.get("a","Respuesta breve"))} for q in faq if _norm_txt(q.get("q"))]

        curso_out["modulos"].append({
            "titulo": mod_title,
            "horas": horas_por_mod.get(mod_title),
            "resumen": overview,
            "lecciones": lecciones,
            "faq": faqs
        })

    # Guardar en el estado
    state["curso_m2"] = curso_out
    return state
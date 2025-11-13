from typing import Dict, Any, List, Tuple

def _norm(s: str) -> str:
    return (s or "").strip()

def _add_issue(issues: List[Dict[str, Any]], severidad: str, tipo: str, donde: str, detalle: str, sugerencia: str):
    issues.append({
        "severidad": severidad,   # "alta" | "media" | "baja"
        "tipo": tipo,             # categoría (estructura, contenido, evaluación, rúbrica, multimedia)
        "donde": donde,           # módulo/lección/ítem
        "detalle": detalle,
        "sugerencia": sugerencia
    })

def _check_course_structure(curso: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    issues: List[Dict[str, Any]] = []
    m = {"modulos": 0, "lecciones": 0, "lecciones_sin_contenido": 0, "introducciones_ok": 0}

    mods = curso.get("modulos") or []
    if not mods:
        _add_issue(issues, "alta", "estructura", "curso", "No hay módulos en el curso.", "Ejecuta mapping/authoring nuevamente.")
        return issues, m

    m["modulos"] = len(mods)

    for mod in mods:
        titulo_m = _norm(mod.get("titulo") or "Módulo")
        lecciones = mod.get("lecciones") or []
        if len(lecciones) < 2:
            _add_issue(issues, "media", "estructura", titulo_m, "Módulo con menos de 2 lecciones.", "Agrega lecciones (mínimo 2 por módulo).")
        m["lecciones"] += len(lecciones)

        for i, lec in enumerate(lecciones, start=1):
            where = f"{titulo_m} > Lección {i}: {_norm(lec.get('titulo','Lección'))[:80]}"
            cont = lec.get("contenido") or {}
            conceptos = cont.get("conceptos_clave") or []
            procedimientos = cont.get("procedimientos") or []
            introduccion = _norm(cont.get("introduccion") or "")
            if not conceptos and not procedimientos:
                _add_issue(issues, "media", "contenido", where, "Lección sin conceptos ni procedimientos.", "Incluye al menos 1 concepto o 1 procedimiento.")
                m["lecciones_sin_contenido"] += 1
            if i == 1 and introduccion:
                m["introducciones_ok"] += 1

            # multimedia presente
            multimedia = lec.get("multimedia") or []
            if not multimedia:
                _add_issue(issues, "baja", "multimedia", where, "Lección sin recursos multimedia.", "Añade prompts/recursos en el nodo media.")

    return issues, m

def _check_assessments(ev: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    issues: List[Dict[str, Any]] = []
    m = {"modulos_con_assessment": 0, "total_items_quiz": 0, "rubricas_ok": 0}

    mods = (ev or {}).get("modulos") or []
    for mm in mods:
        titulo_m = _norm(mm.get("modulo") or "Módulo")
        quiz = (mm.get("quiz") or {}).get("items") or []
        rubrica = mm.get("rubrica") or []

        if quiz:
            m["modulos_con_assessment"] += 1
            m["total_items_quiz"] += len(quiz)
            if len(quiz) < 8:
                _add_issue(issues, "media", "evaluación", titulo_m, f"Quiz con pocos ítems ({len(quiz)}).", "Apunta a 10 ítems por módulo.")
        else:
            _add_issue(issues, "alta", "evaluación", titulo_m, "Módulo sin quiz.", "Genera evaluación sumativa en assessments.")

        # rúbrica suma 100
        pesos = [c.get("peso") or 0 for c in rubrica]
        total = sum(pesos)
        if total != 100:
            _add_issue(issues, "alta", "rúbrica", titulo_m, f"Rúbrica no suma 100 (suma {total}).", "Normaliza pesos para total=100.")
        else:
            m["rubricas_ok"] += 1

    return issues, m

def _score_from_issues(issues: List[Dict[str, Any]]) -> int:
    score = 100
    for it in issues:
        sev = it["severidad"]
        if sev == "alta":
            score -= 12
        elif sev == "media":
            score -= 6
        else:
            score -= 2
    # límites
    score = max(0, min(100, score))
    return score

def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valida curso y evaluaciones.
    Lee: state['curso_m2_multimedia'] (o 'curso_m2'), state['evaluaciones_m2']
    Escribe: state['control_calidad_m2'] con issues, métricas y score.
    """
    curso = state.get("curso_m2_multimedia") or state.get("curso_m2")
    if not curso:
        raise ValueError("Falta curso_m2 o curso_m2_multimedia. Ejecuta authoring/media antes.")

    ev = state.get("evaluaciones_m2") or {}

    all_issues: List[Dict[str, Any]] = []
    metrics: Dict[str, Any] = {}

    # 1) Estructura de curso/lecciones
    issues1, m1 = _check_course_structure(curso)
    all_issues.extend(issues1)
    metrics.update({"curso": m1})

    # 2) Evaluaciones (quiz + rúbrica)
    issues2, m2 = _check_assessments(ev)
    all_issues.extend(issues2)
    metrics.update({"evaluaciones": m2})

    # 3) Score global
    score = _score_from_issues(all_issues)

    report = {
        "resumen": {
            "score_global": score,
            "modulos": metrics.get("curso", {}).get("modulos", 0),
            "lecciones": metrics.get("curso", {}).get("lecciones", 0),
            "quizzes_total_items": metrics.get("evaluaciones", {}).get("total_items_quiz", 0),
            "rubricas_ok": metrics.get("evaluaciones", {}).get("rubricas_ok", 0)
        },
        "metrics": metrics,
        "issues": all_issues,
        "sugerencias_generales": [
            "Asegurar al menos 2 lecciones por módulo con conceptos o procedimientos.",
            "Mantener quizzes ~10 ítems por módulo (mezcla VF/MCQ).",
            "Verificar que las rúbricas sumen 100.",
            "Incluir al menos un recurso multimedia por lección."
        ]
    }

    state["control_calidad_m2"] = report
    return state
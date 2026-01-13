# graphs/m3_entrega/nodes/gamificacion.py
"""
Nodo de Gamificación
Subproceso 3.2.2
"""

import logging
from typing import Dict, Any, List

from api.config.database import SessionLocal
from api.models.lms import LessonProgress
from .utils import load_prompt

logger = logging.getLogger(__name__)

PROMPT_GAMIFICACION = load_prompt("gamificacion_prompt.txt")


def _calcular_puntos_y_medallas(db, enrollment_id: int) -> Dict[str, Any]:
    """
    Cálculo simple de gamificación:
      - 10 puntos por lección completada
      - Medalla "COMPLETO_50" cuando llega a 50% completado
      - Medalla "COMPLETO_100" cuando llega a 100% completado
    """
    progresses: List[LessonProgress] = (
        db.query(LessonProgress)
        .filter(LessonProgress.enrollment_id == enrollment_id)
        .all()
    )

    if not progresses:
        return {"points": 0, "medals": []}

    total = len(progresses)
    completed = sum(1 for p in progresses if p.status == "COMPLETADA")

    ratio = completed / total if total > 0 else 0.0
    points = completed * 10
    medals: List[str] = []

    if ratio >= 0.5:
        medals.append("COMPLETO_50")
    if ratio >= 1.0:
        medals.append("COMPLETO_100")

    return {"points": points, "medals": medals}


def preparar_gamificacion(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepara datos de gamificación (iniciales) para cada matrícula.

    Lee:
      - enrollment_ids

    Hace:
      - Calcula puntos/medallas iniciales
      - Guarda un snapshot en analytics.gamification_snapshot

    Además:
      - Agrega el prompt del agente al estado.
    """
    db = SessionLocal()
    try:
        state["prompt_gamificacion"] = PROMPT_GAMIFICACION

        enrollment_ids: List[int] = state.get("enrollment_ids", [])
        gamification: Dict[int, Dict[str, Any]] = {}

        for eid in enrollment_ids:
            g = _calcular_puntos_y_medallas(db, eid)
            gamification[eid] = g
            logger.info(
                "[M3][GAMIFICACION] Enrollment %s -> puntos=%s, medallas=%s",
                eid,
                g["points"],
                g["medals"],
            )

        # Actualizar analytics (usado internamente)
        analytics = state.get("analytics", {})
        analytics["gamification_snapshot"] = gamification
        state["analytics"] = analytics
        
        # También actualizar analytics_dashboard (usado por API)
        dashboard = state.get("analytics_dashboard", {})
        dashboard["gamification_snapshot"] = gamification
        state["analytics_dashboard"] = dashboard
        state["gamificacion_activa"] = True

        return state
    except Exception as e:
        logger.exception("[M3][GAMIFICACION] Error preparando gamificación: %s", e)
        errors = state.get("errors", [])
        errors.append(f"GAMIFICACION: {str(e)}")
        state["errors"] = errors
        return state
    finally:
        db.close()

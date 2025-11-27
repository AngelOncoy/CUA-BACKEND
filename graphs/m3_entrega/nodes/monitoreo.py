# graphs/m3_entrega/nodes/monitoreo.py
"""
Nodo de Monitoreo y Analytics
Subproceso 3.3.1
"""

import logging
from typing import Dict, Any

from api.config.database import SessionLocal
from api.models.lms import CourseEdition, Enrollment
from .utils import load_prompt

logger = logging.getLogger(__name__)

PROMPT_MONITOREO = load_prompt("monitoreo_prompt.txt")


def generar_analytics(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calcula métricas básicas de la edición del curso.

    Lee:
      - edition_id

    Métricas:
      - total_participantes
      - en_progreso
      - completado
      - abandono
      - tasa_finalizacion

    Además:
      - Agrega el prompt del agente al estado.
    """
    db = SessionLocal()
    try:
        state["prompt_monitoreo"] = PROMPT_MONITOREO

        edition_id = state.get("edition_id")
        if not edition_id:
            raise ValueError("edition_id es requerido para analytics")

        edition = (
            db.query(CourseEdition).filter(CourseEdition.id == edition_id).first()
        )
        if not edition:
            raise ValueError(f"CourseEdition id={edition_id} no encontrada")

        enrollments = (
            db.query(Enrollment).filter(Enrollment.edition_id == edition_id).all()
        )

        total = len(enrollments)
        en_progreso = sum(1 for e in enrollments if e.status == "EN_PROGRESO")
        completado = sum(1 for e in enrollments if e.status == "COMPLETADO")
        abandono = sum(1 for e in enrollments if e.status == "ABANDONADO")

        tasa_finalizacion = completado / total if total > 0 else 0.0

        analytics = state.get("analytics", {})
        analytics.update(
            {
                "edition_id": edition_id,
                "total_participantes": total,
                "en_progreso": en_progreso,
                "completado": completado,
                "abandono": abandono,
                "tasa_finalizacion": tasa_finalizacion,
            }
        )

        state["analytics"] = analytics
        
        # Copiar a analytics_dashboard para que la API pueda leerlo
        state["analytics_dashboard"] = analytics
        
        logger.info(
            "[M3][MONITOREO] Analytics edición %s -> %s",
            edition_id,
            analytics,
        )
        return state
    except Exception as e:
        logger.exception("[M3][MONITOREO] Error actualizando analytics: %s", e)
        errors = state.get("errors", [])
        errors.append(f"MONITOREO: {str(e)}")
        state["errors"] = errors
        return state
    finally:
        db.close()

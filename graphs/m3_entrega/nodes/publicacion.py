# graphs/m3_entrega/nodes/publicacion.py
"""
Nodo de Publicación Automática en LMS
Subproceso 3.1.1
"""

import logging
from typing import Dict, Any
from datetime import datetime

from api.config.database import SessionLocal
from api.models.lms import Course, CourseEdition
from .utils import load_prompt

logger = logging.getLogger(__name__)

# Prompt del agente de publicación
PROMPT_PUBLICACION = load_prompt("publicacion_prompt.txt")


def publicar_en_lms(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Publica el curso en el LMS de forma automática.

    Lee:
      - course_id
      - company_id (opcional, para validar)

    Hace:
      - Marca el curso como PUBLICADO
      - Crea una CourseEdition (edición de curso)
      - Escribe en el estado: edition_id

    Además:
      - Agrega el prompt del agente al estado para auditoría.
    """
    db = SessionLocal()
    try:
        # Guardamos el prompt en el estado (para trazabilidad / inspección)
        state["prompt_publicacion"] = PROMPT_PUBLICACION

        course_id = state.get("course_id")
        company_id = state.get("company_id")

        if not course_id:
            raise ValueError("course_id es obligatorio en el estado M3")

        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise ValueError(f"Curso con id={course_id} no encontrado")

        if company_id and course.company_id and course.company_id != company_id:
            logger.warning(
                "[M3][PUBLICACION] El curso %s pertenece a otra empresa (course.company_id=%s, company_id=%s)",
                course_id,
                course.company_id,
                company_id,
            )

        # Actualizar estado del curso
        course.status = "PUBLICADO"

        # Crear edición
        edition = CourseEdition(
            course_id=course.id,
            start_date=datetime.utcnow(),
            status="EN_PROGRESO",
        )
        db.add(edition)
        db.commit()
        db.refresh(edition)

        state["edition_id"] = edition.id
        state["status"] = "PUBLICADO"

        logger.info(
            "[M3][PUBLICACION] Curso %s publicado en LMS con edición %s",
            course.id,
            edition.id,
        )
        return state
    except Exception as e:
        logger.exception("[M3][PUBLICACION] Error publicando en LMS: %s", e)
        errors = state.get("errors", [])
        errors.append(f"PUBLICACION: {str(e)}")
        state["errors"] = errors
        state["status"] = "ERROR_PUBLICACION"
        return state
    finally:
        db.close()

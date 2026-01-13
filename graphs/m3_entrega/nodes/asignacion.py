# graphs/m3_entrega/nodes/asignacion.py
"""
Nodo de Asignación Automática de Cursos a Empleados
Subproceso 3.2.1
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from api.config.database import SessionLocal
from api.models.lms import (
    Company,
    Participant,
    CourseEdition,
    Enrollment,
    Lesson,
    LessonProgress,
)
from .utils import load_prompt

logger = logging.getLogger(__name__)

PROMPT_ASIGNACION = load_prompt("asignacion_prompt.txt")


def asignar_empleados(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Asigna el curso a los empleados definidos en el estado.

    Lee:
      - company_id
      - employees: [{name, email}]
      - edition_id

    Hace:
      - Crea Participant si no existe (por email + company)
      - Crea Enrollment para cada participant
      - Crea LessonProgress para cada lección del curso
      - Guarda enrollment_ids en el estado

    Además:
      - Agrega el prompt del agente al estado.
    """
    db = SessionLocal()
    try:
        state["prompt_asignacion"] = PROMPT_ASIGNACION

        company_id = state.get("company_id")
        edition_id = state.get("edition_id")
        employees: List[Dict[str, str]] = state.get("employees", [])

        if not company_id or not edition_id:
            raise ValueError("company_id y edition_id son obligatorios en asignación")

        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise ValueError(f"Empresa id={company_id} no encontrada")

        edition = db.query(CourseEdition).filter(CourseEdition.id == edition_id).first()
        if not edition:
            raise ValueError(f"Edición id={edition_id} no encontrada")

        lessons = db.query(Lesson).filter(Lesson.course_id == edition.course_id).all()
        if not lessons:
            logger.warning(
                "[M3][ASIGNACION] El curso %s no tiene lecciones registradas",
                edition.course_id,
            )

        enrollment_ids: List[int] = []

        for emp in employees:
            email = emp.get("email")
            name = emp.get("name") or email
            if not email:
                continue

            # Buscar o crear participant
            participant = (
                db.query(Participant)
                .filter(
                    Participant.email == email,
                    Participant.company_id == company.id,
                )
                .first()
            )
            if not participant:
                participant = Participant(
                    company_id=company.id,
                    name=name,
                    email=email,
                    is_active=True,
                )
                db.add(participant)
                db.flush()

            # Crear matrícula
            enrollment = Enrollment(
                participant_id=participant.id,
                edition_id=edition.id,
                assigned_at=datetime.utcnow(),
                status="ASIGNADO",
            )
            db.add(enrollment)
            db.flush()

            # Crear progreso por lección
            for lesson in lessons:
                prog = LessonProgress(
                    enrollment_id=enrollment.id,
                    lesson_id=lesson.id,
                    status="NO_INICIADA",
                    last_event_at=datetime.utcnow(),
                )
                db.add(prog)

            enrollment_ids.append(enrollment.id)
            logger.info(
                "[M3][ASIGNACION] Asignado participant %s (email=%s) a edition %s",
                participant.id,
                participant.email,
                edition.id,
            )

        db.commit()
        state["enrollment_ids"] = enrollment_ids
        return state
    except Exception as e:
        logger.exception("[M3][ASIGNACION] Error asignando empleados: %s", e)
        errors = state.get("errors", [])
        errors.append(f"ASIGNACION: {str(e)}")
        state["errors"] = errors
        return state
    finally:
        db.close()

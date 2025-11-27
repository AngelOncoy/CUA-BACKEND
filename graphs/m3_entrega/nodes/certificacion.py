# graphs/m3_entrega/nodes/certificacion.py
"""
Nodo de Certificación Automática
Subproceso 3.3.2
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
import uuid

from api.config.database import SessionLocal
from api.models.lms import Enrollment, Certificate
from .utils import load_prompt

logger = logging.getLogger(__name__)

PROMPT_CERTIFICACION = load_prompt("certificacion_prompt.txt")


def _emitir_certificado(db, enrollment: Enrollment) -> Certificate:
    """
    Crea un certificado simple para una matrícula COMPLETADA.
    """
    code = str(uuid.uuid4())
    cert = Certificate(
        enrollment_id=enrollment.id,
        issued_at=datetime.utcnow(),
        code=code,
        url=f"/certificates/{code}.pdf",  # simulación
        grade=None,
    )
    db.add(cert)
    return cert


def generar_certificados(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Emite certificados para las matrículas completadas que aún no tienen certificado.

    Lee:
      - edition_id

    Hace:
      - Busca enrollments COMPLETADO sin certificado
      - Crea Certificate
      - Añade resumen de certificados al estado

    Además:
      - Agrega el prompt del agente al estado.
    """
    db = SessionLocal()
    try:
        state["prompt_certificacion"] = PROMPT_CERTIFICACION

        edition_id = state.get("edition_id")
        if not edition_id:
            raise ValueError("edition_id es requerido para certificación")

        enrollments: List[Enrollment] = (
            db.query(Enrollment)
            .filter(
                Enrollment.edition_id == edition_id,
                Enrollment.status == "COMPLETADO",
            )
            .all()
        )

        certificados_emitidos: List[Dict[str, Any]] = []

        for enr in enrollments:
            if enr.certificate:
                continue  # ya tiene certificado
            cert = _emitir_certificado(db, enr)
            db.flush()
            certificados_emitidos.append(
                {
                    "certificate_id": cert.id,
                    "code": cert.code,
                    "enrollment_id": enr.id,
                }
            )
            logger.info(
                "[M3][CERTIFICACION] Certificado emitido enrollment=%s code=%s",
                enr.id,
                cert.code,
            )

        db.commit()

        # Actualizar estado con campos esperados por la API
        state["certificados_emitidos"] = certificados_emitidos
        state["certificates"] = certificados_emitidos  # Mantener compatibilidad
        state["timestamp_fin"] = datetime.utcnow().isoformat()
        
        return state
    except Exception as e:
        logger.exception("[M3][CERTIFICACION] Error generando certificados: %s", e)
        errors = state.get("errors", [])
        errors.append(f"CERTIFICACION: {str(e)}")
        state["errors"] = errors
        return state
    finally:
        db.close()

# graphs/m3_entrega/nodes/notificacion.py

"""
Nodo de Notificación Automática
Macroproceso 3 – Subproceso 3.1.2
Registra eventos de notificación en la base de datos.
"""

import logging
from datetime import datetime
import json

from api.config.database import SessionLocal
from api.models.lms import NotificationEvent

logger = logging.getLogger("M3_Notificaciones")


def enviar_notificacion(state: dict) -> dict:
    """
    Registra un evento de notificación para cada participante.
    No envía correos reales. Solo registra en la BD como requiere el proyecto.
    """

    db = SessionLocal()

    try:
        recipients = state.get("recipients", [])
        notification_type = state.get("notification_type", "CURSO_ASIGNADO")

        registrados = []

        for r in recipients:
            evento = NotificationEvent(
                type=notification_type,
                recipient_email=r["email"],
                payload=json.dumps({
                    "nombre": r["name"],
                    "curso": state.get("course_name"),
                    "company": state.get("company_name")
                }),
                sent_at=datetime.utcnow(),
                status="REGISTRADO"
            )
            db.add(evento)
            db.commit()
            db.refresh(evento)

            registrados.append({
                "email": evento.recipient_email,
                "id": evento.id
            })

        logger.info(f"[M3] Notificaciones registradas: {len(registrados)}")

        state["notificaciones_registradas"] = registrados
        return state

    except Exception as e:
        logger.error(f"Error en enviar_notificacion: {e}")
        raise

    finally:
        db.close()

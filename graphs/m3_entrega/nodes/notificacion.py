# graphs/m3_entrega/nodes/notificacion.py
"""
Nodo de Notificación Automática
Subproceso 3.1.2
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
import json

from api.config.database import SessionLocal
from api.models.lms import Company, NotificationEvent
from .utils import load_prompt

logger = logging.getLogger(__name__)

PROMPT_NOTIFICACION = load_prompt("notificacion_prompt.txt")


def _registrar_notificacion(
    db,
    tipo: str,
    email: str,
    payload: Dict[str, Any],
    status: str = "ENVIADO",
):
    ev = NotificationEvent(
        type=tipo,
        recipient_email=email,
        payload=json.dumps(payload, ensure_ascii=False),
        sent_at=datetime.utcnow(),
        status=status,
    )
    db.add(ev)


def enviar_notificaciones(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Envía (registra) notificaciones al cliente y a los empleados.

    Lee:
      - company_id
      - employees (lista de {name, email})
      - edition_id

    Hace:
      - Crea registros NotificationEvent para:
          * contacto principal de la empresa (PUBLICACION_CURSO)
          * cada empleado (INVITACION_CURSO)
      - Marca notifications_sent = True en el estado

    Además:
      - Agrega el prompt del agente al estado.
    """
    db = SessionLocal()
    try:
        state["prompt_notificacion"] = PROMPT_NOTIFICACION

        company_id = state.get("company_id")
        edition_id = state.get("edition_id")
        employees: List[Dict[str, str]] = state.get("employees", [])

        if not company_id:
            raise ValueError("company_id es obligatorio para notificar")
        if not edition_id:
            raise ValueError("edition_id es obligatorio para notificar")

        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise ValueError(f"Empresa (Company) con id={company_id} no encontrada")

        # Notificación al contacto de la empresa
        payload_empresa = {
            "message": "Su curso ha sido publicado y la edición está activa.",
            "edition_id": edition_id,
        }
        _registrar_notificacion(
            db,
            tipo="PUBLICACION_CURSO",
            email=company.contact_email,
            payload=payload_empresa,
        )
        logger.info(
            "[M3][NOTIF] Notificación de publicación enviada al contacto de la empresa %s",
            company.contact_email,
        )

        # Notificaciones a empleados
        for emp in employees:
            email = emp.get("email")
            if not email:
                continue
            payload_emp = {
                "message": "Se le ha asignado un nuevo curso.",
                "edition_id": edition_id,
                "employee_name": emp.get("name"),
            }
            _registrar_notificacion(
                db,
                tipo="INVITACION_CURSO",
                email=email,
                payload=payload_emp,
            )
            logger.info("[M3][NOTIF] Invitación de curso enviada a %s", email)

        db.commit()
        
        # Actualizar estado con campos esperados por la API
        state["notificacion_enviada"] = True
        state["email_status"] = {
            "empresa_notificada": True,
            "empleados_notificados": len(employees),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return state
    except Exception as e:
        logger.exception("[M3][NOTIF] Error enviando notificaciones: %s", e)
        errors = state.get("errors", [])
        errors.append(f"NOTIFICACION: {str(e)}")
        state["errors"] = errors
        return state
    finally:
        db.close()

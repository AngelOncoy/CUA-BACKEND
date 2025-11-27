"""
api.routes.m3_entrega.py
Endpoints oficiales del Macroproceso 3
Entrega y Administración Automatizada del Aprendizaje
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Optional
import uuid
import logging

from graphs.m3_entrega.graph import m3_app

router = APIRouter(
    prefix="/m3",
    tags=["Macroproceso 3 - Entrega"]
)

logger = logging.getLogger(__name__)


# ============================================================
# Modelos
# ============================================================

class IniciarEntregaRequest(BaseModel):
    """Request para iniciar el proceso de entrega"""
    curso_id: str
    cliente_id: str
    cliente_email: EmailStr
    syllabus_aprobado: Dict[str, Any]
    empleados: Optional[List[Dict[str, Any]]] = None


class ConsultarProgressRequest(BaseModel):
    """Request para consultar el progreso"""
    run_id: str


# ============================================================
# Inicio del macroproceso
# ============================================================

@router.post("/iniciar")
async def iniciar_entrega(request: IniciarEntregaRequest):
    """
    Inicia el macroproceso completo M3: publicación, notificación,
    asignación, gamificación, analytics y certificación.
    """

    try:
        run_id = f"M3-{uuid.uuid4().hex[:12].upper()}"
        logger.info(f"🔵 [M3] Iniciando entrega {run_id} para curso {request.curso_id}")

        # Convertir IDs a enteros si son strings numéricos (para compatibilidad con DB)
        curso_id = request.curso_id
        if isinstance(curso_id, str) and curso_id.isdigit():
            curso_id = int(curso_id)
        
        cliente_id = request.cliente_id
        if isinstance(cliente_id, str) and cliente_id.isdigit():
            cliente_id = int(cliente_id)

        initial_state = {
            "run_id": run_id,
            "curso_id": curso_id,
            "cliente_id": cliente_id,
            "cliente_email": request.cliente_email,
            "syllabus_aprobado": request.syllabus_aprobado,
            "empleados": request.empleados or [],
            "status": "INICIANDO",
            "errors": []
        }

        config = {"configurable": {"thread_id": run_id}}

        final_state = await m3_app.ainvoke(initial_state, config=config)

        response = {
            "run_id": run_id,
            "status": final_state.get("status", "COMPLETADO"),
            "curso_publicado": final_state.get("curso_publicado", False),
            "lms_course_id": final_state.get("lms_course_id"),
            "url_acceso": final_state.get("url_acceso"),
            "notificacion_enviada": final_state.get("notificacion_enviada", False),
            "empleados_asignados_count": len(final_state.get("enrollment_ids", [])),
            "gamificacion_activa": final_state.get("gamificacion_activa", False),
            "certificados_emitidos_count": len(final_state.get("certificados_emitidos", [])),
            "errors": final_state.get("errors", [])
        }

        logger.info(f"🟢 [M3] Entrega finalizada {run_id}")
        return response

    except Exception as e:
        logger.error(f"🔴 [M3] Error en iniciar_entrega: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al iniciar entrega: {str(e)}")


# ============================================================
# Consultar progreso
# ============================================================

@router.post("/consultar-progreso")
async def consultar_progreso(request: ConsultarProgressRequest):
    """
    Consulta el progreso de un proceso M3.
    NOTA: Este endpoint requiere persistencia (checkpointer) que no está habilitada actualmente.
    """
    raise HTTPException(
        status_code=501,
        detail="Endpoint no disponible: requiere persistencia de estado (checkpointer). "
               "El flujo M3 se ejecuta de principio a fin en una sola llamada."
    )


# ============================================================
# Actualizar métricas manualmente
# ============================================================

@router.post("/actualizar-analytics/{run_id}")
async def actualizar_analytics(run_id: str):
    """
    Fuerza una re-evaluación de analytics y certificación.
    NOTA: Este endpoint requiere persistencia (checkpointer) que no está habilitada actualmente.
    """
    raise HTTPException(
        status_code=501,
        detail="Endpoint no disponible: requiere persistencia de estado (checkpointer). "
               "El flujo M3 se ejecuta de principio a fin en una sola llamada."
    )


# ============================================================
# Health
# ============================================================

@router.get("/health")
async def health_check():
    return {
        "service": "Macroproceso 3",
        "status": "healthy",
        "version": "1.0.0"
    }

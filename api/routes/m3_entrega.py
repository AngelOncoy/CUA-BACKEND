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

        initial_state = {
            "run_id": run_id,
            "curso_id": request.curso_id,
            "cliente_id": request.cliente_id,
            "cliente_email": request.cliente_email,
            "syllabus_aprobado": request.syllabus_aprobado,
            "empleados_asignados": request.empleados or [],
            "status": "INICIANDO",
            "errors": [],
            "timestamp_inicio": None
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
            "empleados_asignados_count": len(final_state.get("empleados_asignados", [])),
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

    try:
        run_id = request.run_id
        logger.info(f"🟡 [M3] Consultando progreso de {run_id}")

        config = {"configurable": {"thread_id": run_id}}
        state = await m3_app.aget_state(config)

        if not state or not state.values:
            raise HTTPException(status_code=404, detail="Proceso no encontrado")

        s = state.values

        return {
            "run_id": run_id,
            "status": s.get("status"),
            "lms_course_id": s.get("lms_course_id"),
            "analytics_dashboard": s.get("analytics_dashboard", {}),
            "metricas_empleados": s.get("metricas_progreso", []),
            "certificados_emitidos": s.get("certificados_emitidos", []),
            "ultima_actualizacion": s.get("timestamp_fin")
        }

    except Exception as e:
        logger.error(f"🔴 [M3] Error consultando progreso: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error consultando progreso: {str(e)}")


# ============================================================
# Actualizar métricas manualmente
# ============================================================

@router.post("/actualizar-analytics/{run_id}")
async def actualizar_analytics(run_id: str):
    """
    Fuerza una re-evaluación de analytics y certificación.
    """

    try:
        logger.info(f"🟠 [M3] Actualizando analytics para {run_id}")

        config = {"configurable": {"thread_id": run_id}}
        state = await m3_app.aget_state(config)

        if not state or not state.values:
            raise HTTPException(status_code=404, detail="Proceso no encontrado")

        current = state.values

        from graphs.m3_entrega.nodes.monitoreo import generar_analytics
        from graphs.m3_entrega.nodes.certificacion import emitir_certificados

        updated = await generar_analytics(current)
        updated = await emitir_certificados(updated)

        await m3_app.aupdate_state(config, updated)

        return {
            "run_id": run_id,
            "actualizado": True,
            "analytics_dashboard": updated.get("analytics_dashboard", {}),
            "nuevos_certificados": len(updated.get("certificados_emitidos", []))
        }

    except Exception as e:
        logger.error(f"🔴 [M3] Error en actualizar_analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error actualizando analytics: {str(e)}")


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

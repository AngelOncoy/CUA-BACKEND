"""
Endpoints de API para el Macroproceso 3
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Optional
import uuid
import logging

from graphs.m3_entrega.graph import m3_app

router = APIRouter(prefix="/m3", tags=["Macroproceso 3 - Entrega"])
logger = logging.getLogger(__name__)


# ===== MODELOS DE REQUEST =====

class IniciarEntregaRequest(BaseModel):
    """Request para iniciar el proceso de entrega"""
    curso_id: str
    cliente_id: str
    cliente_email: EmailStr
    syllabus_aprobado: Dict[str, Any]
    empleados: Optional[List[Dict[str, Any]]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "curso_id": "CURSO-001",
                "cliente_id": "CLI-123",
                "cliente_email": "cliente@empresa.com",
                "syllabus_aprobado": {
                    "titulo": "Técnicas Avanzadas de Ventas B2B",
                    "descripcion": "Curso completo de ventas",
                    "duracion_horas": 12,
                    "nivel": "intermedio",
                    "industria": "ventas",
                    "precio": 2500.00
                },
                "empleados": [
                    {
                        "empleado_id": "EMP001",
                        "nombre": "Juan Pérez",
                        "email": "juan@empresa.com",
                        "departamento": "Ventas"
                    }
                ]
            }
        }


class ConsultarProgressRequest(BaseModel):
    """Request para consultar progreso"""
    run_id: str


# ===== ENDPOINTS =====

@router.post("/iniciar")
async def iniciar_entrega(request: IniciarEntregaRequest):
    """
    Inicia el proceso completo de entrega y administración del aprendizaje.
    
    Ejecuta secuencialmente:
    1. Publicación en LMS
    2. Notificación al cliente
    3. Asignación de empleados
    4. Activación de gamificación
    5. Generación de analytics
    6. Emisión de certificados (si aplica)
    
    Returns:
        - run_id: ID único del proceso
        - status: Estado actual
        - lms_course_id: ID del curso en el LMS
        - url_acceso: URL para acceder al curso
    """
    try:
        # Generar ID único para el proceso
        run_id = f"M3-{uuid.uuid4().hex[:12].upper()}"
        
        logger.info(f"[API] Iniciando entrega {run_id} para curso {request.curso_id}")
        
        # Preparar estado inicial
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
        
        # Configuración para persistencia
        config = {
            "configurable": {
                "thread_id": run_id
            }
        }
        
        # Ejecutar el grafo completo
        final_state = await m3_app.ainvoke(initial_state, config=config)
        
        # Preparar respuesta
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
        
        if response["errors"]:
            logger.warning(f"[API] Entrega {run_id} completada con errores: {response['errors']}")
        else:
            logger.info(f"[API] ✓ Entrega {run_id} completada exitosamente")
        
        return response
        
    except Exception as e:
        logger.error(f"[API] ✗ Error en iniciar_entrega: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al iniciar entrega: {str(e)}"
        )


@router.post("/consultar-progreso")
async def consultar_progreso(request: ConsultarProgressRequest):
    """
    Consulta el progreso actual de un curso en ejecución.
    
    Returns:
        - Analytics dashboard con métricas en tiempo real
        - Progreso individual de cada empleado
        - Certificados emitidos
    """
    try:
        run_id = request.run_id
        
        logger.info(f"[API] Consultando progreso de {run_id}")
        
        # Configuración para recuperar el estado
        config = {
            "configurable": {
                "thread_id": run_id
            }
        }
        
        # Obtener estado actual del grafo
        state = await m3_app.aget_state(config)
        
        if not state or not state.values:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró el proceso {run_id}"
            )
        
        current_state = state.values
        
        # Preparar respuesta con analytics
        response = {
            "run_id": run_id,
            "status": current_state.get("status"),
            "lms_course_id": current_state.get("lms_course_id"),
            "analytics_dashboard": current_state.get("analytics_dashboard", {}),
            "metricas_empleados": current_state.get("metricas_progreso", []),
            "certificados_emitidos": current_state.get("certificados_emitidos", []),
            "ultima_actualizacion": current_state.get("timestamp_fin")
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[API] ✗ Error en consultar_progreso: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al consultar progreso: {str(e)}"
        )


@router.post("/actualizar-analytics/{run_id}")
async def actualizar_analytics(run_id: str):
    """
    Fuerza una actualización del dashboard de analytics.
    
    Útil para refrescar métricas en tiempo real.
    """
    try:
        logger.info(f"[API] Actualizando analytics para {run_id}")
        
        config = {
            "configurable": {
                "thread_id": run_id
            }
        }
        
        # Obtener estado actual
        state = await m3_app.aget_state(config)
        
        if not state or not state.values:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró el proceso {run_id}"
            )
        
        current_state = state.values
        
        # Re-ejecutar solo el nodo de monitoreo
        from graphs.m3_entrega.nodes.monitoreo import generar_analytics
        from graphs.m3_entrega.nodes.certificacion import emitir_certificados
        
        # Actualizar analytics
        updated_state = await generar_analytics(current_state)
        
        # Re-evaluar certificaciones
        updated_state = await emitir_certificados(updated_state)
        
        # Actualizar el checkpoint
        await m3_app.aupdate_state(config, updated_state)
        
        return {
            "run_id": run_id,
            "actualizado": True,
            "analytics_dashboard": updated_state.get("analytics_dashboard", {}),
            "nuevos_certificados": len(updated_state.get("certificados_emitidos", []))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[API] ✗ Error en actualizar_analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar analytics: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check del servicio M3"""
    return {
        "service": "Macroproceso 3 - Entrega y Administración",
        "status": "healthy",
        "version": "1.0.0"
    }
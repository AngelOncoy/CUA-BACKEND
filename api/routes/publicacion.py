"""
Endpoints granulares para Publicación de Cursos (Proceso 3.1)
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uuid
import logging
from graphs.m3_entrega.nodes.publicacion import publicar_curso
from graphs.m3_entrega.nodes.notificacion import enviar_notificacion_cliente

router = APIRouter(prefix="/m3/publicacion", tags=["M3 - Publicación"])
logger = logging.getLogger(__name__)

class PublicarCursoRequest(BaseModel):
    """Request para publicar curso individualmente"""
    curso_id: str
    cliente_id: str
    syllabus_aprobado: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "curso_id": "CURSO-001",
                "cliente_id": "CLI-123",
                "syllabus_aprobado": {
                    "titulo": "Técnicas Avanzadas de Ventas B2B",
                    "descripcion": "Curso completo de ventas",
                    "duracion_horas": 12,
                    "nivel": "intermedio",
                    "industria": "ventas",
                    "precio": 2500.00
                }
            }
        }

@router.post("/publicar")
async def publicar_curso_endpoint(request: PublicarCursoRequest):
    """Publica un curso en el LMS de forma independiente"""
    try:
        publicacion_id = f"PUB-{uuid.uuid4().hex[:8].upper()}"
        logger.info(f"[PUBLICACION] Publicando curso {request.curso_id} - ID: {publicacion_id}")
        
        # Estado mínimo para publicación
        state = {
            "run_id": publicacion_id,
            "curso_id": request.curso_id,
            "cliente_id": request.cliente_id,
            "syllabus_aprobado": request.syllabus_aprobado,
            "status": "PUBLICANDO"
        }
        
        # Ejecutar solo nodo de publicación
        result = await publicar_curso(state)
        
        # Enviar notificación
        await enviar_notificacion_cliente(result)
        
        return {
            "publicacion_id": publicacion_id,
            "status": "PUBLICADO",
            "lms_course_id": result.get("lms_course_id"),
            "url_acceso": result.get("url_acceso"),
            "tiempo_ejecucion": result.get("tiempo_ejecucion", 0)
        }
        
    except Exception as e:
        logger.error(f"[PUBLICACION] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en publicación: {str(e)}")

@router.get("/status/{publicacion_id}")
async def consultar_publicacion(publicacion_id: str):
    """Consulta el estado de una publicación específica"""
    try:
        from graphs.m3_entrega.graph import m3_app
        config = {"configurable": {"thread_id": publicacion_id}}
        state = await m3_app.aget_state(config)
        
        if not state or not state.values:
            raise HTTPException(status_code=404, detail="Publicación no encontrada")
        
        return {
            "publicacion_id": publicacion_id,
            "status": state.values.get("status"),
            "lms_course_id": state.values.get("lms_course_id"),
            "url_acceso": state.values.get("url_acceso")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error consultando publicación: {str(e)}")
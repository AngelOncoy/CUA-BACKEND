"""
Nodo de Publicación Automática en LMS
Subproceso 3.1.1
"""
import logging
from typing import Dict, Any
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)


async def publicar_en_lms(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Publica el curso en el LMS de forma automática.
    
    Pasos:
    1. Preparar el payload del curso
    2. Crear el curso en el LMS vía API
    3. Configurar permisos y visibilidad
    4. Generar URL de acceso
    """
    logger.info(f"[PUBLICACIÓN] Iniciando publicación del curso {state.get('curso_id')}")
    
    try:
        syllabus = state.get("syllabus_aprobado", {})
        curso_id = state.get("curso_id")
        
        # Preparar datos del curso para el LMS
        curso_data = {
            "external_id": curso_id,
            "title": syllabus.get("titulo", "Curso sin título"),
            "description": syllabus.get("descripcion", ""),
            "duration_hours": syllabus.get("duracion_horas", 12),
            "level": syllabus.get("nivel", "intermedio"),
            "industry": syllabus.get("industria", "general"),
            "modules": syllabus.get("modulos", []),
            "syllabus_content": syllabus.get("markdown", ""),
            "price": syllabus.get("precio", 0),
            "status": "published",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Simulación de publicación en LMS
        # En producción, aquí iría la llamada real a la API del LMS
        lms_response = await _publicar_curso_lms(curso_data)
        
        if lms_response["success"]:
            state["curso_publicado"] = True
            state["lms_course_id"] = lms_response["course_id"]
            state["url_acceso"] = lms_response["access_url"]
            state["status"] = "PUBLICADO"
            
            logger.info(f"[PUBLICACIÓN] ✓ Curso publicado exitosamente: {lms_response['course_id']}")
        else:
            state["curso_publicado"] = False
            state["errors"] = state.get("errors", [])
            state["errors"].append(f"Error en publicación LMS: {lms_response.get('error')}")
            logger.error(f"[PUBLICACIÓN] ✗ Fallo en publicación: {lms_response.get('error')}")
            
    except Exception as e:
        logger.error(f"[PUBLICACIÓN] ✗ Excepción: {str(e)}")
        state["curso_publicado"] = False
        state["errors"] = state.get("errors", [])
        state["errors"].append(f"Excepción en publicación: {str(e)}")
    
    return state


async def _publicar_curso_lms(curso_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Llama a la API del LMS para publicar el curso.
    
    En producción, esto haría una llamada HTTP real:
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{LMS_API_URL}/courses",
            json=curso_data,
            headers={"Authorization": f"Bearer {LMS_API_KEY}"}
        )
        return response.json()
    """
    # Simulación para desarrollo
    import uuid
    
    # Simular latencia de API
    import asyncio
    await asyncio.sleep(0.5)
    
    lms_course_id = f"LMS-{uuid.uuid4().hex[:8].upper()}"
    
    return {
        "success": True,
        "course_id": lms_course_id,
        "access_url": f"https://lms.ultraautomatizado.com/courses/{lms_course_id}",
        "published_at": datetime.utcnow().isoformat()
    }


def timed_node(func):
    """Decorador para medir el tiempo de ejecución de un nodo"""
    async def wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
        start = datetime.now()
        result = await func(state)
        elapsed = (datetime.now() - start).total_seconds()
        logger.info(f"[TIMING] {func.__name__} ejecutado en {elapsed:.2f}s")
        return result
    return wrapper


# Exportar versión decorada
publicar_en_lms = timed_node(publicar_en_lms)
"""
Servicio para interactuar con el LMS
"""
import os
import logging
import httpx
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

LMS_API_URL = os.getenv("LMS_API_URL", "https://api.tu-lms.com")
LMS_API_KEY = os.getenv("LMS_API_KEY", "tu_api_key_del_lms")

async def publicar_curso_lms(curso_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Publica un curso en el LMS.
    
    Args:
        curso_data: Datos del curso (curso_id, titulo, etc.)
        
    Returns:
        Respuesta con lms_course_id, url_acceso
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{LMS_API_URL}/courses",
                json=curso_data,
                headers={"Authorization": f"Bearer {LMS_API_KEY}"}
            )
            response.raise_for_status()
            data = response.json()
            return {
                "lms_course_id": data.get("course_id", f"LMS-{curso_data['curso_id']}"),
                "url_acceso": data.get("url", f"{LMS_API_URL}/courses/{curso_data['curso_id']}"),
                "tiempo_ejecucion": response.elapsed.total_seconds()
            }
    except Exception as e:
        logger.error(f"[LMS] Error publicando curso: {str(e)}")
        raise Exception(f"Error en LMS: {str(e)}")

async def asignar_empleados_lms(lms_course_id: str, empleados: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Asigna empleados a un curso en el LMS.
    
    Args:
        lms_course_id: ID del curso en el LMS
        empleados: Lista de empleados (empleado_id, email, nombre)
        
    Returns:
        Respuesta con estado de asignación
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{LMS_API_URL}/courses/{lms_course_id}/enroll",
                json={"empleados": empleados},
                headers={"Authorization": f"Bearer {LMS_API_KEY}"}
            )
            response.raise_for_status()
            return {"status": "ASIGNADOS", "empleados_count": len(empleados)}
    except Exception as e:
        logger.error(f"[LMS] Error asignando empleados: {str(e)}")
        raise Exception(f"Error en LMS: {str(e)}")

async def configurar_gamificacion(lms_course_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Configura gamificación para un curso.
    
    Args:
        lms_course_id: ID del curso en el LMS
        config: Configuración de gamificación (puntos, insignias)
        
    Returns:
        Respuesta con configuración aplicada
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{LMS_API_URL}/courses/{lms_course_id}/gamification",
                json=config,
                headers={"Authorization": f"Bearer {LMS_API_KEY}"}
            )
            response.raise_for_status()
            data = response.json()
            return {
                "puntos_configurados": data.get("puntos_por_modulo", config["puntos_por_modulo"]),
                "insignias_activas": data.get("insignias", [i["nombre"] for i in config["insignias"]])
            }
    except Exception as e:
        logger.error(f"[LMS] Error configurando gamificación: {str(e)}")
        raise Exception(f"Error en LMS: {str(e)}")

async def generar_certificado(curso_id: str, lms_course_id: str, empleado_id: str, empleado_nombre: str) -> Dict[str, Any]:
    """
    Genera un certificado para un empleado.
    
    Args:
        curso_id: ID del curso
        lms_course_id: ID del curso en el LMS
        empleado_id: ID del empleado
        empleado_nombre: Nombre del empleado
        
    Returns:
        Respuesta con certificado_id, url_certificado
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{LMS_API_URL}/courses/{lms_course_id}/certificates",
                json={
                    "curso_id": curso_id,
                    "empleado_id": empleado_id,
                    "empleado_nombre": empleado_nombre
                },
                headers={"Authorization": f"Bearer {LMS_API_KEY}"}
            )
            response.raise_for_status()
            data = response.json()
            return {
                "certificado_id": data.get("certificado_id", f"CERT-{empleado_id}"),
                "url_certificado": data.get("url", f"{LMS_API_URL}/certificates/CERT-{empleado_id}")
            }
    except Exception as e:
        logger.error(f"[LMS] Error generando certificado: {str(e)}")
        raise Exception(f"Error en LMS: {str(e)}")
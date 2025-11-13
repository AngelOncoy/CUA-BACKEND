"""
Servicio para obtener métricas de analytics del LMS
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

async def obtener_metricas_lms(lms_course_id: str) -> Dict[str, Any]:
    """
    Obtiene métricas de progreso de un curso desde el LMS.
    
    Args:
        lms_course_id: ID del curso en el LMS
        
    Returns:
        Diccionario con métricas (progreso_empleados)
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{LMS_API_URL}/courses/{lms_course_id}/metrics",
                headers={"Authorization": f"Bearer {LMS_API_KEY}"}
            )
            response.raise_for_status()
            data = response.json()
            return {
                "progreso_empleados": data.get("empleados", []),
                "tiempo_ejecucion": response.elapsed.total_seconds()
            }
    except Exception as e:
        logger.error(f"[ANALYTICS] Error obteniendo métricas para curso {lms_course_id}: {str(e)}")
        raise Exception(f"Error en analytics: {str(e)}")
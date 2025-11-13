"""
Endpoints granulares para Gestión de Empleados y Gamificación (Proceso 3.2)
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid
import logging
from graphs.m3_entrega.nodes.asignacion import asignar_empleados
from graphs.m3_entrega.nodes.gamificacion import activar_gamificacion

router = APIRouter(prefix="/m3/gestion", tags=["M3 - Gestión"])
logger = logging.getLogger(__name__)

class AsignarEmpleadosRequest(BaseModel):
    """Request para asignar empleados a un curso"""
    curso_id: str
    lms_course_id: str
    empleados: List[Dict[str, Any]]
    
    class Config:
        json_schema_extra = {
            "example": {
                "curso_id": "CURSO-001",
                "lms_course_id": "LMS-12345",
                "empleados": [
                    {"empleado_id": "EMP001", "nombre": "Juan Pérez", "email": "juan@empresa.com", "departamento": "Ventas"},
                    {"empleado_id": "EMP002", "nombre": "María García", "email": "maria@empresa.com", "departamento": "Ventas"}
                ]
            }
        }

@router.post("/asignar-empleados")
async def asignar_empleados_endpoint(request: AsignarEmpleadosRequest):
    """Asigna empleados a un curso de forma independiente"""
    try:
        gestion_id = f"GEST-{uuid.uuid4().hex[:8].upper()}"
        logger.info(f"[GESTION] Asignando {len(request.empleados)} empleados - ID: {gestion_id}")
        
        state = {
            "run_id": gestion_id,
            "curso_id": request.curso_id,
            "lms_course_id": request.lms_course_id,
            "empleados_asignados": request.empleados,
            "status": "ASIGNANDO"
        }
        
        result = await asignar_empleados(state)
        
        return {
            "gestion_id": gestion_id,
            "status": "ASIGNADOS",
            "empleados_asignados_count": len(result.get("empleados_asignados", [])),
            "tiempo_ejecucion": result.get("tiempo_ejecucion", 0)
        }
        
    except Exception as e:
        logger.error(f"[GESTION] Error asignando empleados: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error asignando empleados: {str(e)}")

@router.post("/activar-gamificacion/{curso_id}")
async def activar_gamificacion_endpoint(curso_id: str):
    """Activa gamificación para un curso específico"""
    try:
        gam_id = f"GAM-{uuid.uuid4().hex[:8].upper()}"
        logger.info(f"[GAMIFICACION] Activando gamificación para {curso_id}")
        
        state = {
            "run_id": gam_id,
            "curso_id": curso_id,
            "status": "ACTIVANDO_GAMIFICACION"
        }
        
        result = await activar_gamificacion(state)
        
        return {
            "gamificacion_id": gam_id,
            "status": "ACTIVA",
            "puntos_configurados": result.get("puntos_configurados", {}),
            "insignias_activas": result.get("insignias_activas", [])
        }
        
    except Exception as e:
        logger.error(f"[GAMIFICACION] Error activando gamificación: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error activando gamificación: {str(e)}")
"""
Endpoints granulares para Monitoreo y Certificación (Proceso 3.3)
"""
from fastapi import APIRRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import logging
from graphs.m3_entrega.nodes.monitoreo import generar_analytics
from graphs.m3_entrega.nodes.certificacion import emitir_certificados

router = APIRouter(prefix="/m3/monitoreo", tags=["M3 - Monitoreo"])
logger = logging.getLogger(__name__)

class MonitoreoRequest(BaseModel):
    """Request para monitoreo específico"""
    run_id: str

@router.post("/analytics/{run_id}")
async def generar_analytics_endpoint(run_id: str):
    """Genera analytics para un curso específico"""
    try:
        logger.info(f"[MONITOREO] Generando analytics para {run_id}")
        
        from graphs.m3_entrega.graph import m3_app
        config = {"configurable": {"thread_id": run_id}}
        state = await m3_app.aget_state(config)
        
        if not state or not state.values:
            raise HTTPException(status_code=404, detail="Proceso no encontrado")
        
        current_state = state.values
        updated_state = await generar_analytics(current_state)
        
        # Actualizar estado
        await m3_app.aupdate_state(config, updated_state)
        
        return {
            "run_id": run_id,
            "analytics_actualizados": True,
            "dashboard": updated_state.get("analytics_dashboard", {}),
            "progreso_promedio": updated_state.get("progreso_promedio", 0),
            "tasa_completacion": updated_state.get("tasa_completacion", 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[MONITOREO] Error generando analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generando analytics: {str(e)}")

@router.post("/certificados/{run_id}")
async def emitir_certificados_endpoint(run_id: str):
    """Emite certificados para empleados que completaron el curso"""
    try:
        logger.info(f"[CERTIFICACION] Emitiendo certificados para {run_id}")
        
        from graphs.m3_entrega.graph import m3_app
        config = {"configurable": {"thread_id": run_id}}
        state = await m3_app.aget_state(config)
        
        if not state or not state.values:
            raise HTTPException(status_code=404, detail="Proceso no encontrado")
        
        current_state = state.values
        updated_state = await emitir_certificados(current_state)
        
        # Actualizar estado
        await m3_app.aupdate_state(config, updated_state)
        
        nuevos_certificados = len(updated_state.get("certificados_emitidos", []))
        
        return {
            "run_id": run_id,
            "certificados_emitidos": nuevos_certificados,
            "total_certificados": len(updated_state.get("certificados_emitidos", [])),
            "certificados": updated_state.get("certificados_emitidos", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[CERTIFICACION] Error emitiendo certificados: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error emitiendo certificados: {str(e)}")

@router.get("/resumen/{run_id}")
async def resumen_completo(run_id: str):
    """Resumen completo de un proceso M3"""
    try:
        from graphs.m3_entrega.graph import m3_app
        config = {"configurable": {"thread_id": run_id}}
        state = await m3_app.aget_state(config)
        
        if not state or not state.values:
            raise HTTPException(status_code=404, detail="Proceso no encontrado")
        
        current_state = state.values
        
        return {
            "run_id": run_id,
            "status": current_state.get("status"),
            "curso": current_state.get("syllabus_aprobado", {}),
            "empleados_count": len(current_state.get("empleados_asignados", [])),
            "progreso_promedio": current_state.get("progreso_promedio", 0),
            "tasa_completacion": current_state.get("tasa_completacion", 0),
            "certificados_count": len(current_state.get("certificados_emitidos", []))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo resumen: {str(e)}")
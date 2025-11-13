"""
Nodo de Asignación Automática de Cursos a Empleados
Subproceso 3.2.1
"""
import logging
from typing import Dict, Any, List
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


async def asignar_empleados(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Asigna automáticamente el curso a los empleados registrados 
    en la cuenta empresarial del cliente.
    """
    logger.info(f"[ASIGNACIÓN] Iniciando asignación de empleados al curso {state.get('lms_course_id')}")
    
    try:
        lms_course_id = state.get("lms_course_id")
        cliente_id = state.get("cliente_id")
        empleados_lista = state.get("empleados_asignados", [])
        
        if not empleados_lista:
            # Si no se proporcionó lista, obtener de la base de datos del cliente
            empleados_lista = await _obtener_empleados_cliente(cliente_id)
        
        # Realizar asignaciones en lote
        resultados = await _asignar_curso_empleados(lms_course_id, empleados_lista)
        
        # Actualizar estado
        state["empleados_asignados"] = resultados["asignados"]
        state["asignaciones_completadas"] = resultados["success"]
        
        if resultados["success"]:
            logger.info(f"[ASIGNACIÓN] ✓ {len(resultados['asignados'])} empleados asignados exitosamente")
        else:
            state["errors"] = state.get("errors", [])
            state["errors"].append(f"Asignación parcial: {resultados.get('error')}")
            logger.warning(f"[ASIGNACIÓN] ⚠ Asignación parcial: {resultados.get('error')}")
            
    except Exception as e:
        logger.error(f"[ASIGNACIÓN] ✗ Excepción: {str(e)}")
        state["asignaciones_completadas"] = False
        state["errors"] = state.get("errors", [])
        state["errors"].append(f"Excepción en asignación: {str(e)}")
    
    return state


async def _obtener_empleados_cliente(cliente_id: str) -> List[Dict[str, Any]]:
    """
    Obtiene la lista de empleados activos de un cliente desde la base de datos.
    
    En producción, esto consultaría la tabla de empleados:
    
    async with get_db_session() as session:
        result = await session.execute(
            select(Empleado).where(
                Empleado.cliente_id == cliente_id,
                Empleado.estado == "activo"
            )
        )
        return [emp.to_dict() for emp in result.scalars().all()]
    """
    # Simulación para desarrollo
    await asyncio.sleep(0.3)
    
    return [
        {
            "empleado_id": "EMP001",
            "nombre": "Juan Pérez",
            "email": "juan.perez@empresa.com",
            "departamento": "Ventas",
            "rol": "Ejecutivo"
        },
        {
            "empleado_id": "EMP002",
            "nombre": "María García",
            "email": "maria.garcia@empresa.com",
            "departamento": "Ventas",
            "rol": "Supervisor"
        },
        {
            "empleado_id": "EMP003",
            "nombre": "Carlos Rodríguez",
            "email": "carlos.rodriguez@empresa.com",
            "departamento": "Ventas",
            "rol": "Ejecutivo"
        }
    ]


async def _asignar_curso_empleados(
    lms_course_id: str, 
    empleados: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Realiza las asignaciones en el LMS.
    
    En producción, haría llamadas a la API del LMS:
    
    async with httpx.AsyncClient() as client:
        tasks = [
            client.post(
                f"{LMS_API_URL}/enrollments",
                json={
                    "course_id": lms_course_id,
                    "user_id": emp["empleado_id"],
                    "enrollment_type": "required"
                }
            )
            for emp in empleados
        ]
        results = await asyncio.gather(*tasks)
    """
    # Simulación para desarrollo
    await asyncio.sleep(0.5)
    
    asignados = []
    for emp in empleados:
        asignados.append({
            **emp,
            "curso_id": lms_course_id,
            "fecha_asignacion": datetime.utcnow().isoformat(),
            "estado_inscripcion": "activo",
            "progreso": 0
        })
    
    return {
        "success": True,
        "asignados": asignados,
        "total": len(asignados)
    }
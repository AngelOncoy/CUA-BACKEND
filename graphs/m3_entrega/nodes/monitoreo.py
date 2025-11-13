"""
Nodo de Monitoreo y Dashboard de Analítica
Subproceso 3.3.1
"""
import logging
from typing import Dict, Any, List
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


async def generar_analytics(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Genera el dashboard de analítica en tiempo real con métricas de progreso.
    
    Métricas clave:
    - Porcentaje de avance por empleado
    - Lecciones vistas y evaluaciones completadas
    - Tasa de finalización
    """
    logger.info(f"[ANALYTICS] Generando dashboard para {state.get('lms_course_id')}")
    
    try:
        lms_course_id = state.get("lms_course_id")
        empleados = state.get("empleados_asignados", [])
        
        # Obtener métricas de progreso de cada empleado
        metricas_empleados = await _obtener_metricas_empleados(lms_course_id, empleados)
        
        # Calcular estadísticas agregadas
        analytics_dashboard = _calcular_estadisticas_agregadas(metricas_empleados)
        
        # Actualizar estado
        state["metricas_progreso"] = metricas_empleados
        state["analytics_dashboard"] = analytics_dashboard
        state["status"] = "MONITOREANDO"
        
        logger.info(f"[ANALYTICS] ✓ Dashboard generado: {analytics_dashboard['resumen']['empleados_totales']} empleados")
        
    except Exception as e:
        logger.error(f"[ANALYTICS] ✗ Excepción: {str(e)}")
        state["errors"] = state.get("errors", [])
        state["errors"].append(f"Excepción en analytics: {str(e)}")
    
    return state


async def _obtener_metricas_empleados(
    curso_id: str, 
    empleados: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Obtiene las métricas de progreso de cada empleado desde el LMS.
    
    En producción:
    
    async with httpx.AsyncClient() as client:
        tasks = [
            client.get(
                f"{LMS_API_URL}/progress/{curso_id}/{emp['empleado_id']}"
            )
            for emp in empleados
        ]
        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses]
    """
    # Simulación para desarrollo
    await asyncio.sleep(0.5)
    
    import random
    metricas = []
    
    for emp in empleados:
        # Simular progreso variado
        lecciones_totales = 36  # 3 módulos x 12 lecciones
        lecciones_completadas = random.randint(0, lecciones_totales)
        evaluaciones_totales = 12
        evaluaciones_completadas = min(lecciones_completadas // 3, evaluaciones_totales)
        
        metricas.append({
            "empleado_id": emp["empleado_id"],
            "nombre": emp["nombre"],
            "curso_id": curso_id,
            "porcentaje_avance": round((lecciones_completadas / lecciones_totales) * 100, 1),
            "lecciones_completadas": lecciones_completadas,
            "lecciones_totales": lecciones_totales,
            "evaluaciones_completadas": evaluaciones_completadas,
            "evaluaciones_totales": evaluaciones_totales,
            "tiempo_invertido_minutos": random.randint(30, 480),
            "ultimo_acceso": datetime.utcnow().isoformat(),
            "puntos_ganados": lecciones_completadas * 10 + evaluaciones_completadas * 25,
            "medallas_obtenidas": _generar_medallas_obtenidas(lecciones_completadas),
            "racha_dias": random.randint(0, 7)
        })
    
    return metricas


def _generar_medallas_obtenidas(lecciones: int) -> List[str]:
    """Genera medallas basadas en el progreso"""
    medallas = []
    if lecciones >= 1:
        medallas.append("🚀 Inicio Rápido")
    if lecciones >= 5:
        medallas.append("📚 Estudiante Dedicado")
    if lecciones >= 12:
        medallas.append("⚡ Velocista")
    if lecciones >= 36:
        medallas.append("🏆 Completista")
    return medallas


def _calcular_estadisticas_agregadas(metricas: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calcula estadísticas agregadas para el dashboard.
    """
    if not metricas:
        return {
            "resumen": {
                "empleados_totales": 0,
                "progreso_promedio": 0,
                "tasa_finalizacion": 0
            }
        }
    
    total_empleados = len(metricas)
    progreso_total = sum(m["porcentaje_avance"] for m in metricas)
    progreso_promedio = progreso_total / total_empleados
    
    empleados_completado = sum(1 for m in metricas if m["porcentaje_avance"] >= 100)
    tasa_finalizacion = (empleados_completado / total_empleados) * 100
    
    # Top performers
    top_performers = sorted(
        metricas, 
        key=lambda x: x["puntos_ganados"], 
        reverse=True
    )[:5]
    
    # Empleados en riesgo (menos de 20% de avance después de X días)
    en_riesgo = [m for m in metricas if m["porcentaje_avance"] < 20]
    
    return {
        "resumen": {
            "empleados_totales": total_empleados,
            "progreso_promedio": round(progreso_promedio, 1),
            "tasa_finalizacion": round(tasa_finalizacion, 1),
            "empleados_completado": empleados_completado,
            "empleados_en_progreso": total_empleados - empleados_completado,
            "tiempo_promedio_minutos": round(
                sum(m["tiempo_invertido_minutos"] for m in metricas) / total_empleados
            )
        },
        "top_performers": [
            {
                "nombre": p["nombre"],
                "puntos": p["puntos_ganados"],
                "progreso": p["porcentaje_avance"]
            }
            for p in top_performers
        ],
        "en_riesgo": [
            {
                "nombre": r["nombre"],
                "progreso": r["porcentaje_avance"],
                "ultimo_acceso": r["ultimo_acceso"]
            }
            for r in en_riesgo
        ],
        "distribucion_progreso": {
            "0-25%": sum(1 for m in metricas if 0 <= m["porcentaje_avance"] < 25),
            "25-50%": sum(1 for m in metricas if 25 <= m["porcentaje_avance"] < 50),
            "50-75%": sum(1 for m in metricas if 50 <= m["porcentaje_avance"] < 75),
            "75-100%": sum(1 for m in metricas if 75 <= m["porcentaje_avance"] <= 100)
        },
        "generado_at": datetime.utcnow().isoformat()
    }
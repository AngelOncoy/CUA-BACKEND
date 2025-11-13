"""
Nodo de Configuración de Gamificación
Subproceso 3.2.2
"""
import logging
from typing import Dict, Any
from datetime import datetime
import os

logger = logging.getLogger(__name__)


async def activar_gamificacion(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Configura el sistema de gamificación (logros, puntos, medallas) 
    integrado al LMS para el curso publicado.
    """
    logger.info(f"[GAMIFICACIÓN] Configurando gamificación para {state.get('lms_course_id')}")
    
    try:
        lms_course_id = state.get("lms_course_id")
        syllabus = state.get("syllabus_aprobado", {})
        
        # Configuración de puntos desde variables de entorno
        config_gamificacion = {
            "curso_id": lms_course_id,
            "puntos_por_leccion": int(os.getenv("POINTS_PER_LESSON", 10)),
            "puntos_por_quiz": int(os.getenv("POINTS_PER_QUIZ", 25)),
            "puntos_por_modulo": int(os.getenv("POINTS_PER_MODULE", 50)),
            "puntos_por_curso": int(os.getenv("POINTS_PER_COURSE", 200)),
            "medallas": _generar_sistema_medallas(syllabus),
            "leaderboard_activo": True,
            "notificaciones_logros": True
        }
        
        # Activar en el LMS
        resultado = await _configurar_gamificacion_lms(config_gamificacion)
        
        if resultado["success"]:
            state["gamificacion_activa"] = True
            state["config_gamificacion"] = config_gamificacion
            logger.info(f"[GAMIFICACIÓN] ✓ Gamificación activada con {len(config_gamificacion['medallas'])} medallas")
        else:
            state["gamificacion_activa"] = False
            state["errors"] = state.get("errors", [])
            state["errors"].append(f"Error en gamificación: {resultado.get('error')}")
            logger.error(f"[GAMIFICACIÓN] ✗ Fallo: {resultado.get('error')}")
            
    except Exception as e:
        logger.error(f"[GAMIFICACIÓN] ✗ Excepción: {str(e)}")
        state["gamificacion_activa"] = False
        state["errors"] = state.get("errors", [])
        state["errors"].append(f"Excepción en gamificación: {str(e)}")
    
    return state


def _generar_sistema_medallas(syllabus: Dict[str, Any]) -> list:
    """
    Genera automáticamente las medallas basadas en el contenido del curso.
    """
    medallas = [
        {
            "id": "inicio_rapido",
            "nombre": "Inicio Rápido",
            "descripcion": "Completar la primera lección en las primeras 24 horas",
            "icono": "🚀",
            "puntos_bonus": 20,
            "condicion": "primera_leccion_24h"
        },
        {
            "id": "estudiante_dedicado",
            "nombre": "Estudiante Dedicado",
            "descripcion": "Completar 5 lecciones consecutivas sin fallar",
            "icono": "📚",
            "puntos_bonus": 50,
            "condicion": "5_lecciones_consecutivas"
        },
        {
            "id": "maestro_evaluaciones",
            "nombre": "Maestro de Evaluaciones",
            "descripcion": "Obtener 100% en 3 evaluaciones",
            "icono": "🎯",
            "puntos_bonus": 75,
            "condicion": "3_evaluaciones_perfectas"
        },
        {
            "id": "velocista",
            "nombre": "Velocista del Aprendizaje",
            "descripcion": "Completar un módulo en menos de 2 horas",
            "icono": "⚡",
            "puntos_bonus": 40,
            "condicion": "modulo_bajo_2h"
        },
        {
            "id": "completista",
            "nombre": "Completista",
            "descripcion": "Finalizar el 100% del curso",
            "icono": "🏆",
            "puntos_bonus": 200,
            "condicion": "curso_completo"
        }
    ]
    
    # Agregar medallas específicas por módulo
    modulos = syllabus.get("modulos", [])
    for idx, modulo in enumerate(modulos, 1):
        medallas.append({
            "id": f"modulo_{idx}_maestro",
            "nombre": f"Maestro de {modulo.get('nombre', f'Módulo {idx}')}",
            "descripcion": f"Completar todas las lecciones del módulo {idx} con calificación superior a 80%",
            "icono": "🌟",
            "puntos_bonus": 30,
            "condicion": f"modulo_{idx}_completo_80"
        })
    
    return medallas


async def _configurar_gamificacion_lms(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Envía la configuración de gamificación al LMS.
    
    En producción:
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{LMS_API_URL}/gamification/config",
            json=config,
            headers={"Authorization": f"Bearer {LMS_API_KEY}"}
        )
        return response.json()
    """
    # Simulación para desarrollo
    import asyncio
    await asyncio.sleep(0.3)
    
    return {
        "success": True,
        "config_id": f"GAM-{datetime.utcnow().timestamp()}",
        "medallas_creadas": len(config["medallas"]),
        "configurado_at": datetime.utcnow().isoformat()
    }
    
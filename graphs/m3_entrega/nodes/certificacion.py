"""
Nodo de Emisión de Certificaciones Digitales
Subproceso 3.3.2
"""
import logging
from typing import Dict, Any, List
from datetime import datetime
import hashlib
import os

logger = logging.getLogger(__name__)


async def emitir_certificados(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Emite certificados digitales automáticamente para empleados que 
    alcanzan el umbral de finalización configurado.
    
    Umbral por defecto: 80% de progreso
    """
    logger.info(f"[CERTIFICACIÓN] Evaluando empleados para certificación")
    
    try:
        umbral = float(os.getenv("CERT_COMPLETION_THRESHOLD", 80))
        metricas = state.get("metricas_progreso", [])
        curso_id = state.get("lms_course_id")
        curso_titulo = state.get("syllabus_aprobado", {}).get("titulo", "Curso")
        
        # Filtrar empleados elegibles
        elegibles = [
            m for m in metricas 
            if m["porcentaje_avance"] >= umbral
        ]
        
        if not elegibles:
            logger.info(f"[CERTIFICACIÓN] ℹ No hay empleados elegibles (umbral: {umbral}%)")
            state["certificados_emitidos"] = []
            return state
        
        # Emitir certificados
        certificados = []
        for emp in elegibles:
            cert = await _generar_certificado(
                empleado=emp,
                curso_id=curso_id,
                curso_titulo=curso_titulo
            )
            certificados.append(cert)
        
        state["certificados_emitidos"] = certificados
        logger.info(f"[CERTIFICACIÓN] ✓ {len(certificados)} certificados emitidos")
        
        # Enviar notificaciones de certificados
        await _notificar_certificados(certificados)
        
    except Exception as e:
        logger.error(f"[CERTIFICACIÓN] ✗ Excepción: {str(e)}")
        state["errors"] = state.get("errors", [])
        state["errors"].append(f"Excepción en certificación: {str(e)}")
    
    return state


async def _generar_certificado(
    empleado: Dict[str, Any],
    curso_id: str,
    curso_titulo: str
) -> Dict[str, Any]:
    """
    Genera un certificado digital con hash de verificación.
    """
    import uuid
    
    certificado_id = f"CERT-{uuid.uuid4().hex[:12].upper()}"
    fecha_emision = datetime.utcnow().isoformat()
    
    # Generar hash de verificación
    data_verificacion = f"{certificado_id}{empleado['empleado_id']}{curso_id}{fecha_emision}"
    hash_verificacion = hashlib.sha256(data_verificacion.encode()).hexdigest()[:16]
    
    # Calcular calificación final
    calificacion_final = empleado.get("porcentaje_avance", 0)
    
    certificado = {
        "certificado_id": certificado_id,
        "empleado_id": empleado["empleado_id"],
        "nombre_empleado": empleado["nombre"],
        "curso_id": curso_id,
        "nombre_curso": curso_titulo,
        "fecha_emision": fecha_emision,
        "calificacion_final": calificacion_final,
        "puntos_totales": empleado.get("puntos_ganados", 0),
        "url_certificado": f"https://lms.ultraautomatizado.com/certificates/{certificado_id}",
        "url_verificacion": f"https://lms.ultraautomatizado.com/verify/{hash_verificacion}",
        "hash_verificacion": hash_verificacion,
        "medallas_obtenidas": empleado.get("medallas_obtenidas", [])
    }
    
    # Guardar en base de datos (simulación)
    await _guardar_certificado_db(certificado)
    
    logger.info(f"[CERT] Generado {certificado_id} para {empleado['nombre']}")
    
    return certificado


async def _guardar_certificado_db(certificado: Dict[str, Any]):
    """
    Guarda el certificado en la base de datos.
    
    En producción:
    
    async with get_db_session() as session:
        cert_model = Certificado(**certificado)
        session.add(cert_model)
        await session.commit()
    """
    import asyncio
    await asyncio.sleep(0.1)
    logger.debug(f"[DB] Certificado {certificado['certificado_id']} guardado")


async def _notificar_certificados(certificados: List[Dict[str, Any]]):
    """
    Envía notificaciones por email con los certificados.
    """
    # Aquí se integraría con el servicio de email
    for cert in certificados:
        logger.info(
            f"[NOTIF] Email de certificado enviado a "
            f"{cert['nombre_empleado']} ({cert['certificado_id']})"
        )
    
    import asyncio
    await asyncio.sleep(0.2)
"""
api.routes.m3_entrega.py
Endpoints oficiales del Macroproceso 3
Ahora integrados al central_graph (M3 → M4)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Optional
import uuid
import logging

# 🚀 CAMBIO CLAVE: usar central_graph en lugar del grafo viejo M3
from graphs.central_graph import build_graph

router = APIRouter(
    prefix="/m3",
    tags=["Macroproceso 3 - Entrega"]
)

logger = logging.getLogger(__name__)

# Construimos el grafo central solo una vez
central_app = build_graph()


# ============================================================
# Modelos
# ============================================================

class IniciarEntregaRequest(BaseModel):
    """Request para iniciar el proceso de entrega"""
    curso_id: str
    cliente_id: str
    cliente_email: EmailStr
    syllabus_aprobado: Dict[str, Any]
    empleados: Optional[List[Dict[str, Any]]] = None


class ConsultarProgressRequest(BaseModel):
    """Request para consultar el progreso"""
    run_id: str


# ============================================================
# Inicio del macroproceso (INICIO DE M3)
# ============================================================

@router.post("/iniciar")
async def iniciar_entrega(request: IniciarEntregaRequest):
    """
    Inicia el macroproceso M3 completo dentro del grafo integrado:
    M3_INICIALIZAR → ... → M3_CERTIFICAR → M4_EXTRACT → ... → M4_KB
    """

    try:
        run_id = f"M3-{uuid.uuid4().hex[:12].upper()}"
        logger.info(f"🔵 [M3] Iniciando entrega {run_id} para curso {request.curso_id}")

        # Conversión a int si corresponde
        curso_id = int(request.curso_id) if request.curso_id.isdigit() else request.curso_id
        cliente_id = int(request.cliente_id) if request.cliente_id.isdigit() else request.cliente_id

        # =============================
        # ESTADO INICIAL DEL CENTRAL_GRAPH
        # =============================
        initial_state = {
            "prompt_raw": "",
            "entidades": {},
            "confianza_nlp": 1.0,
            "requiere_clarificacion": False,
            "preguntas": [],
            "respuestas": [],
            "mapping": {},
            "syllabus": request.syllabus_aprobado,
            "precio": {},
            "propuesta_html": "",
            "decision": "",
            "metricas": {},
            "historial": [],

            # M3 datos
            "curso_id": curso_id,
            "cliente_id": cliente_id,
            "cliente_email": request.cliente_email,
            "empleados": request.empleados or [],
            "m3_publicado": False,
            "certificados": [],
            "gamificacion": {},
            "analytics": {},

            # M4 datos mínimos
            "course_data": request.syllabus_aprobado,
            "prompts_analysis": {},
            "success_patterns": {},
            "gaps": [],
            "additional_content": [],
            "updated_content": {}
        }

        # =========================================
        # EJECUTAR el grafo central desde M3_INICIALIZAR
        # =========================================

        final_state = await central_app.ainvoke(
            initial_state,
            start_at="M3_INICIALIZAR"
        )

        # =========================================
        # Generar respuesta limpia
        # =========================================
        response = {
            "run_id": run_id,
            "status": "COMPLETADO",
            "curso_publicado": final_state.get("m3_publicado", False),
            "certificados_emitidos_count": len(final_state.get("certificados", [])),
            "gamificacion": final_state.get("gamificacion", {}),
            "analytics": final_state.get("analytics", {}),

            # Datos M4
            "rules": final_state.get("rules", []),
            "gaps_detected": final_state.get("gaps", []),
            "updated_content": final_state.get("updated_content", {}),
            "knowledge_base_updates": final_state.get("knowledge_base_updates", [])
        }

        logger.info(f"🟢 [M3+M4] Macroproceso completado {run_id}")
        return response

    except Exception as e:
        logger.error(f"🔴 [M3] Error en iniciar_entrega: {str(e)}")
        raise HTTPException(status_code=500, detail=f"[M3 ERROR] {str(e)}")


# ============================================================
# Endpoints NO usados (persistencia no implementada)
# ============================================================

@router.post("/consultar-progreso")
async def consultar_progreso(request: ConsultarProgressRequest):
    raise HTTPException(
        status_code=501,
        detail="Progreso no disponible: M3 se ejecuta completo en una sola llamada."
    )


@router.post("/actualizar-analytics/{run_id}")
async def actualizar_analytics(run_id: str):
    raise HTTPException(
        status_code=501,
        detail="Analytics no puede actualizarse manualmente: no hay persistencia."
    )


# ============================================================
# Healthcheck
# ============================================================

@router.get("/health")
async def health_check():
    return {
        "service": "Macroproceso 3",
        "status": "healthy",
        "version": "2.0.0 (integrado)"
    }

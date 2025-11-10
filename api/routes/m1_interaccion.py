# api/routes/m1_interaccion.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid
import logging

from graphs.m1_interaccion.graph import build_graph

# Configuración del logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

router = APIRouter()
app_graph = build_graph()


# -----------------------------
# MODELOS DE ENTRADA
# -----------------------------
class PromptIn(BaseModel):
    prompt: str


class AnswersIn(BaseModel):
    run_id: str
    respuestas: List[str]


class ApprovalIn(BaseModel):
    run_id: str
    decision: str  # "APROBADO" | "ACLARAR" | "RECHAZADO"


# -----------------------------
# FUNCIÓN AUXILIAR PARA CONFIG
# -----------------------------
def cfg_for(run_id: str) -> Dict[str, Any]:
    """Construye la configuración del grafo con el ID de hilo (thread_id)."""
    return {"configurable": {"thread_id": run_id}}


# -----------------------------
# ENDPOINT: /m1/prompt
# -----------------------------
@router.post("/m1/prompt")
def submit_prompt(data: PromptIn):
    """
    Inicia un nuevo flujo del Macroproceso 1.
    Evalúa el prompt inicial y determina si requiere aclaración
    o si puede generar directamente la propuesta.
    """
    run_id = str(uuid.uuid4())
    log.info(f"[PROMPT] Nuevo flujo iniciado con run_id={run_id}")

    # Ejecutamos el grafo con el prompt inicial
    state = app_graph.invoke({"prompt_raw": data.prompt}, config=cfg_for(run_id))

    # --- Si requiere aclaración ---
    if state.get("preguntas"):
        log.info(f"[PROMPT] Se requieren aclaraciones. Preguntas generadas: {len(state['preguntas'])}")
        return {
            "run_id": run_id,
            "status": "WAITING_FOR_ANSWERS",
            "preguntas": state["preguntas"],
        }

    # --- Si ya se generó una propuesta ---
    if state.get("propuesta_html"):
        log.info(f"[PROMPT] Flujo llegó a propuesta. Esperando aprobación.")
        return {
            "run_id": run_id,
            "status": "WAITING_FOR_APPROVAL",
            "propuesta_html": state["propuesta_html"],
        }

    # --- Si por alguna razón aún está procesando ---
    log.warning("[PROMPT] No se generaron preguntas ni propuesta. Estado intermedio.")
    return {
        "run_id": run_id,
        "status": "IN_PROGRESS",
        "message": "El flujo sigue ejecutándose internamente."
    }


# -----------------------------
# ENDPOINT: /m1/answers
# -----------------------------
@router.post("/m1/answers")
def submit_answers(data: AnswersIn):
    """
    Envía las respuestas del usuario a las preguntas de aclaración.
    El grafo se reanuda desde el checkpoint del mismo run_id.
    """
    log.info(f"[ANSWERS] Continuando flujo {data.run_id} con {len(data.respuestas)} respuestas")

    # Retomamos desde el checkpoint y agregamos las respuestas
    state = app_graph.invoke({"respuestas": data.respuestas}, config=cfg_for(data.run_id))

    # --- Si genera nuevas preguntas (raro, pero posible) ---
    if state.get("preguntas"):
        return {
            "run_id": data.run_id,
            "status": "WAITING_FOR_ANSWERS",
            "preguntas": state["preguntas"],
        }

    # --- Si llega a propuesta ---
    if state.get("propuesta_html"):
        return {
            "run_id": data.run_id,
            "status": "WAITING_FOR_APPROVAL",
            "propuesta_html": state["propuesta_html"],
        }

    # --- Control preventivo ---
    return {
        "run_id": data.run_id,
        "status": "IN_PROGRESS",
        "message": "El flujo sigue ejecutándose internamente."
    }


# -----------------------------
# ENDPOINT: /m1/approval
# -----------------------------
@router.post("/m1/approval")
def submit_approval(data: ApprovalIn):
    """
    Recibe la decisión del usuario respecto a la propuesta generada.
    """
    log.info(f"[APPROVAL] run_id={data.run_id} decisión={data.decision}")

    state = app_graph.invoke({"decision": data.decision}, config=cfg_for(data.run_id))

    # --- Determinar estado final ---
    if data.decision in ("APROBADO", "RECHAZADO"):
        status = "END"
        log.info(f"[APPROVAL] Flujo finalizado para {data.run_id}.")
    elif data.decision == "ACLARAR":
        status = "WAITING_FOR_ANSWERS"
        log.info(f"[APPROVAL] Flujo vuelve a fase de aclaraciones.")
    else:
        status = "WAITING_FOR_APPROVAL"
        log.info(f"[APPROVAL] Decisión pendiente o inválida.")

    return {
        "run_id": data.run_id,
        "status": status,
        "preguntas": state.get("preguntas"),
        "propuesta_html": state.get("propuesta_html"),
    }

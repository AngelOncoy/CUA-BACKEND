# api/routes/m1_interaccion.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid
import logging

from graphs.m1_interaccion.graph import build_graph

# -----------------------------
# SERVICIO PAYPAL
# -----------------------------
from services.paypal_service import (
    create_paypal_order,
    capture_paypal_order
)

# Configuración del logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

router = APIRouter()
app_graph = build_graph()


# -----------------------------
# MODELOS DE ENTRADA DEL FLUJO
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
# MODELOS PARA PAYPAL
# -----------------------------
class PaymentRequest(BaseModel):
    monto: float
    descripcion: str = "Pago de curso automatizado"


# -----------------------------
# FUNCIÓN AUXILIAR
# -----------------------------
def cfg_for(run_id: str) -> Dict[str, Any]:
    """Construye la configuración del grafo con el ID de hilo (thread_id)."""
    return {"configurable": {"thread_id": run_id}}


# -----------------------------
# ENDPOINT: /m1/prompt
# -----------------------------
@router.post("/m1/prompt")
def submit_prompt(data: PromptIn):

    run_id = str(uuid.uuid4())
    log.info(f"[PROMPT] Nuevo flujo iniciado con run_id={run_id}")

    state = app_graph.invoke({"prompt_raw": data.prompt}, config=cfg_for(run_id))

    if state.get("preguntas"):
        return {
            "run_id": run_id,
            "status": "WAITING_FOR_ANSWERS",
            "preguntas": state["preguntas"],
        }

    if state.get("propuesta_html"):
        return {
            "run_id": run_id,
            "status": "WAITING_FOR_APPROVAL",
            "propuesta_html": state["propuesta_html"],
        }

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

    log.info(f"[ANSWERS] Continuando flujo {data.run_id}")

    state = app_graph.invoke({"respuestas": data.respuestas}, config=cfg_for(data.run_id))

    if state.get("preguntas"):
        return {
            "run_id": data.run_id,
            "status": "WAITING_FOR_ANSWERS",
            "preguntas": state["preguntas"],
        }

    if state.get("propuesta_html"):
        return {
            "run_id": data.run_id,
            "status": "WAITING_FOR_APPROVAL",
            "propuesta_html": state["propuesta_html"],
        }

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

    log.info(f"[APPROVAL] run_id={data.run_id} decisión={data.decision}")

    state = app_graph.invoke({"decision": data.decision}, config=cfg_for(data.run_id))

    if data.decision in ("APROBADO", "RECHAZADO"):
        status = "END"
    elif data.decision == "ACLARAR":
        status = "WAITING_FOR_ANSWERS"
    else:
        status = "WAITING_FOR_APPROVAL"

    return {
        "run_id": data.run_id,
        "status": status,
        "preguntas": state.get("preguntas"),
        "propuesta_html": state.get("propuesta_html"),
    }


# =======================================================
# ✅ NUEVOS ENDPOINTS: PAGOS CON PAYPAL
# =======================================================

# -----------------------------
# ENDPOINT: /m1/paypal/create (crear orden)
# -----------------------------
@router.post("/m1/paypal/create")
def create_paypal_payment(data: PaymentRequest):
    """
    Crea una orden de pago PayPal y devuelve el link de aprobación.
    """
    log.info(f"[PAYPAL] Creando pago por {data.monto} USD")

    approval_url = create_paypal_order(
        total=data.monto,
        description=data.descripcion
    )

    return {
        "status": "PAYMENT_CREATED",
        "approval_url": approval_url
    }


# -----------------------------
# ENDPOINT: /m1/paypal/success
# -----------------------------
@router.get("/m1/paypal/success")
def paypal_success(paymentId: str, PayerID: str):

    log.info(f"[PAYPAL] Pago exitoso paymentId={paymentId}")

    result = capture_paypal_order(paymentId, PayerID)

    return {
        "status": "SUCCESS",
        "paypal_response": result
    }


# -----------------------------
# ENDPOINT: /m1/paypal/cancel
# -----------------------------
@router.get("/m1/paypal/cancel")
def paypal_cancel():
    log.info("[PAYPAL] Pago cancelado por el usuario")

    return {
        "status": "CANCELLED",
        "message": "El usuario canceló el pago."
    }

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid
import logging

from graphs.central_graph import build_graph

# Servicio de PayPal
from services.paypal_service import create_paypal_order, capture_paypal_order

# Configuración del logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# Inicializar el router y el grafo
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
async def submit_prompt(data: PromptIn):
    run_id = str(uuid.uuid4())
    log.info(f"[PROMPT] Nuevo flujo iniciado con run_id={run_id}")

    state = app_graph.invoke({"prompt_raw": data.prompt}, config=cfg_for(run_id))

    if "preguntas" in state:
        return {"run_id": run_id, "status": "WAITING_FOR_ANSWERS", "preguntas": state["preguntas"]}

    if "propuesta_html" in state:
        return {"run_id": run_id, "status": "WAITING_FOR_APPROVAL", "propuesta_html": state["propuesta_html"]}

    return {"run_id": run_id, "status": "IN_PROGRESS", "message": "El flujo sigue ejecutándose internamente."}


# -----------------------------
# ENDPOINT: /m1/answers
# -----------------------------
@router.post("/m1/answers")
async def submit_answers(data: AnswersIn):
    log.info(f"[ANSWERS] Continuando flujo {data.run_id}")

    # Ejecuta el grafo y procesa las respuestas del usuario
    state = app_graph.invoke({"respuestas": data.respuestas}, config=cfg_for(data.run_id))

    # Si el sistema necesita más respuestas
    if "preguntas" in state:
        return {"run_id": data.run_id, "status": "WAITING_FOR_ANSWERS", "preguntas": state["preguntas"]}

    # Si el sistema generó una propuesta HTML
    if "propuesta_html" in state:
        return {"run_id": data.run_id, "status": "WAITING_FOR_APPROVAL", "propuesta_html": state["propuesta_html"]}

    return {"run_id": data.run_id, "status": "IN_PROGRESS", "message": "El flujo sigue ejecutándose internamente."}


# -----------------------------
# ENDPOINT: /m1/approval
# -----------------------------
@router.post("/m1/approval")
async def submit_approval(data: ApprovalIn):
    log.info(f"[APPROVAL] run_id={data.run_id} decisión={data.decision}")

    # Ejecuta el grafo y procesa la decisión del usuario
    state = app_graph.invoke({"decision": data.decision}, config=cfg_for(data.run_id))

    # Determina la acción según la decisión del usuario
    if data.decision == "APROBADO":
        status = "END"
    elif data.decision == "RECHAZADO":
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
async def create_paypal_payment(data: PaymentRequest):
    """
    Crea una orden de pago PayPal y devuelve el link de aprobación.
    """
    try:
        log.info(f"[PAYPAL] Creando pago por {data.monto} USD")

        order = create_paypal_order(
            amount=data.monto,
            description=data.descripcion
        )

        return {
            "status": "PAYMENT_CREATED",
            "order_id": order["order_id"],
            "approval_url": order["approval_url"]
        }

    except Exception as e:
        log.error(f"[PAYPAL ERROR] {e}")
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------------
# ENDPOINT: /m1/paypal/success
# -----------------------------
@router.get("/m1/paypal/success")
async def paypal_success(paymentId: str, PayerID: str):
    log.info(f"[PAYPAL] Pago exitoso paymentId={paymentId}")

    try:
        result = capture_paypal_order(paymentId, PayerID)
        return {
            "status": "SUCCESS",
            "paypal_response": result
        }
    except Exception as e:
        log.error(f"[PAYPAL ERROR] {e}")
        raise HTTPException(status_code=400, detail=f"Error procesando el pago: {str(e)}")


# -----------------------------
# ENDPOINT: /m1/paypal/cancel
# -----------------------------
@router.get("/m1/paypal/cancel")
async def paypal_cancel():
    log.info("[PAYPAL] Pago cancelado por el usuario")

    return {
        "status": "CANCELLED",
        "message": "El usuario canceló el pago."
    }

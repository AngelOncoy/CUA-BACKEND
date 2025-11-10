# api/routes/m1_interaccion.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid
from graphs.m1_interaccion.graph import build_graph

router = APIRouter()
app_graph = build_graph()

class PromptIn(BaseModel):
    prompt: str

class AnswersIn(BaseModel):
    run_id: str
    respuestas: List[str]

class ApprovalIn(BaseModel):
    run_id: str
    decision: str  # "APROBADO" | "ACLARAR" | "RECHAZADO"

def cfg_for(run_id: str) -> Dict[str, Any]:
    return {"configurable": {"thread_id": run_id}}

@router.post("/prompt")
def submit_prompt(data: PromptIn):
    run_id = str(uuid.uuid4())
    state = app_graph.invoke({"prompt_raw": data.prompt}, config=cfg_for(run_id))
    return {
        "run_id": run_id,
        "step": "ASK" if state.get("preguntas") else "PROPOSAL",
        "preguntas": state.get("preguntas"),
        "propuesta_html": state.get("propuesta_html")
    }

@router.post("/answers")
def submit_answers(data: AnswersIn):
    state = app_graph.invoke({"respuestas": data.respuestas}, config=cfg_for(data.run_id))
    return {
        "run_id": data.run_id,
        "step": "ASK" if state.get("preguntas") else ("PROPOSAL" if state.get("propuesta_html") else "NLP"),
        "preguntas": state.get("preguntas"),
        "propuesta_html": state.get("propuesta_html")
    }

@router.post("/approval")
def submit_approval(data: ApprovalIn):
    state = app_graph.invoke({"decision": data.decision}, config=cfg_for(data.run_id))
    return {"run_id": data.run_id, "status": "END" if data.decision in ("APROBADO","RECHAZADO") else "ASK"}

# --- ENDPOINT TEMPORAL PARA PROBAR SOLO EL NLP ---
from graphs.m1_interaccion.nodes.nlp import nlp_node

@router.post("/nlp_test")
def test_nlp_node(data: PromptIn):
    """
    Prueba aislada del nodo NLP. Recibe un prompt y devuelve las entidades detectadas.
    """
    state = {"prompt_raw": data.prompt}
    result = nlp_node(state)
    return {
        "entidades": result.get("entidades"),
        "confianza_nlp": result.get("confianza_nlp")
    }

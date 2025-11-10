# graphs/m1_interaccion/nodes/proposal.py
from typing import Dict, Any, TYPE_CHECKING
import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from core.config import GOOGLE_API_KEY, GEMINI_MODEL
from core.utils import timed_node

# Evita importación circular, solo para tipado
if TYPE_CHECKING:
    from graphs.m1_interaccion.graph import M1State

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    temperature=0.2,
    api_key=GOOGLE_API_KEY
)

prompt_prop = ChatPromptTemplate.from_messages([
    (
        "system",
        "Genera una propuesta ejecutiva en HTML simple (h2, p, ul) con sílabus y precio. "
        "Evita usar caracteres difíciles de procesar como las tildes y la ñ para evitar "
        "problemas de codificación en el HTML."
    ),
    ("user", "Sílabus:\n{syllabus}\nPrecio:\n{precio}")
])


@timed_node
def proposal_node(state: Dict[str, Any]) -> Dict[str, Any]:
    log.info("Generando propuesta ejecutiva...")

    html = (prompt_prop | llm).invoke({
        "syllabus": state.get("syllabus", {}),
        "precio": state.get("precio", {})
    })

    state["propuesta_html"] = str(html.content)
    log.info("Propuesta generada correctamente. Esperando aprobación.")
    return state


def approval_router(state: "M1State") -> str:  # 👈 nota las comillas
    decision = state.get("decision")
    log.info(f"Evaluando decisión del usuario → {decision}")

    if decision in ("APROBADO", "RECHAZADO"):
        log.info("Flujo finalizado.")
        return "END"
    elif decision == "ACLARAR":
        log.info("Volviendo a nodo ASK para aclaraciones.")
        return "ASK"
    else:
        log.info("Esperando decisión del usuario (estado WAIT).")
        return "WAIT"

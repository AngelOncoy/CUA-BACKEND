# graphs/m1_interaccion/nodes/clarify.py
from typing import Dict, Any
from core.config import UMBRAL_CONFIANZA_NLP, GOOGLE_API_KEY, GEMINI_MODEL
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from core.utils import timed_node
import logging
import os

llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, temperature=0.2, api_key=GOOGLE_API_KEY)
log = logging.getLogger(__name__)

# Función para leer el archivo de prompt
def read_file(file_path: str) -> str:
    dir_actual = os.path.dirname(os.path.abspath(__file__))
    prompt_file_path = os.path.join(dir_actual, file_path)

    with open(prompt_file_path, "r", encoding="utf-8") as file:
        return file.read()

# Cargar el prompt de clarificación desde el archivo
prompt_clarify_text = read_file("prompts/prompt_clarify.txt")

# -----------------------------------------------------
# Decide si el prompt tiene suficiente información
# -----------------------------------------------------
@timed_node
def clarify_decide(state: Dict[str, Any]) -> str:
    e = state.get("entidades", {})
    confianza = float(state.get("confianza_nlp", 0.0))

    # Determinar si faltan datos
    industria = e.get("industria", "").strip()
    nivel = e.get("nivel", "").strip()
    competencias = e.get("competencias", [])

    faltan = (not industria) or (not nivel)
    pocos_temas = len(competencias) < 1  # antes era <2, relajamos la regla

    log.info(f"[CLARIFY] Confianza={confianza:.2f} / Umbral={UMBRAL_CONFIANZA_NLP} / Faltan={faltan} / Competencias={len(competencias)}")
    log.info(f"[DEBUG] Entidades detectadas → {e}")

    # --- Condición realista ---
    if confianza < UMBRAL_CONFIANZA_NLP:
        log.info("[CLARIFY] Confianza insuficiente → ASK")
        state["requiere_clarificacion"] = True
        return "ASK"

    if faltan:
        log.info("[CLARIFY] Faltan datos clave → ASK")
        state["requiere_clarificacion"] = True
        return "ASK"

    # Caso donde el modelo está seguro pero solo hay una competencia → seguimos igual
    if pocos_temas and confianza >= 0.8:
        log.info("[CLARIFY] Confianza alta con pocos temas → se continúa")
        state["requiere_clarificacion"] = False
        return "MAP"

    # Todo OK → seguimos flujo normal
    state["requiere_clarificacion"] = False
    return "MAP"

# -----------------------------------------------------
# Genera las preguntas solo si faltan datos
# -----------------------------------------------------
prompt_ask = ChatPromptTemplate.from_messages([
    ("system", prompt_clarify_text),
    ("user", "Entidades detectadas: {entidades}")
])

@timed_node
def ask_node(state: Dict[str, Any]) -> Dict[str, Any]:
    if not state.get("requiere_clarificacion"):
        return state
    ent = state.get("entidades", {})
    msg = (prompt_ask | llm).invoke({"entidades": ent})
    qs = [q.strip("- ").strip() for q in str(msg.content).split("\n") if q.strip()]
    state["preguntas"] = qs[:3]
    return state

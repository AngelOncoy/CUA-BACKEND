# graphs/m1_interaccion/nodes/clarify.py
from typing import Dict, Any
from core.config import UMBRAL_CONFIANZA_NLP, GOOGLE_API_KEY
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2, google_api_key=GOOGLE_API_KEY)

def clarify_decide(state: Dict[str, Any]) -> str:
    e = state.get("entidades", {})
    faltan = (not e.get("industria")) or (not e.get("nivel")) or len(e.get("competencias", [])) < 2
    if state.get("confianza_nlp", 0.0) < UMBRAL_CONFIANZA_NLP or faltan:
        state["requiere_clarificacion"] = True
        return "ASK"
    return "MAP"

prompt_ask = ChatPromptTemplate.from_messages([
    ("system", "Formula hasta 3 preguntas de clarificación para completar datos faltantes, concisas."),
    ("user", "Entidades detectadas: {entidades}")
])

def ask_node(state: Dict[str, Any]) -> Dict[str, Any]:
    ent = state.get("entidades", {})
    msg = (prompt_ask | llm).invoke({"entidades": ent})
    qs = [q.strip("- ").strip() for q in str(msg.content).split("\n") if q.strip()]
    state["preguntas"] = qs[:3]
    return state

def after_answers_router(state: Dict[str, Any]) -> str:
    return "NLP"

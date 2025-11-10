# graphs/m1_interaccion/nodes/syllabus.py
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from core.config import GOOGLE_API_KEY, GEMINI_MODEL
from core.utils import timed_node

llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, temperature=0.2, api_key=GOOGLE_API_KEY)

prompt_syl = ChatPromptTemplate.from_messages([
    (
        "system",
        """Eres un diseñador instruccional especializado en formación empresarial.
        Tu trabajo dentro del sistema AUTOMA es crear sílabus detallados a partir
        de un mapa de competencias.

        Debes generar:
        - Objetivo general del curso.
        - Lista de módulos con título, descripción y horas estimadas.
        - Resultados de aprendizaje claros y medibles.

        Formato: texto estructurado en Markdown.

        Sé conciso, profesional y pedagógico. Usa verbos de acción (identificar,
        aplicar, analizar, diseñar)."""
    ),
    ("user", "Competencias: {mapping}\nIndustria: {industria}\nNivel: {nivel}")
])

@timed_node
def syllabus_node(state: Dict[str, Any]) -> Dict[str, Any]:
    ent = state.get("entidades", {})
    msg = (prompt_syl | llm).invoke({
        "mapping": state.get("mapping", {}),
        "industria": ent.get("industria",""),
        "nivel": ent.get("nivel","")
    })
    state["syllabus"] = {"markdown": msg.content}
    return state


# graphs/m1_interaccion/nodes/proposal.py
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from core.config import GOOGLE_API_KEY, GEMINI_MODEL

llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, temperature=0.2, api_key=GOOGLE_API_KEY)

prompt_prop = ChatPromptTemplate.from_messages([
    ("system", "Genera una propuesta ejecutiva en HTML simple (h2, p, ul) con sílabus y precio."),
    ("user", "Sílabus:\n{syllabus}\nPrecio:\n{precio}")
])


def proposal_node(state: Dict[str, Any]) -> Dict[str, Any]:
    html = (prompt_prop | llm).invoke({
        "syllabus": state.get("syllabus", {}),
        "precio": state.get("precio", {})
    })
    state["propuesta_html"] = str(html.content)
    return state

def approval_router(state: Dict[str, Any]) -> str:
    d = state.get("decision")
    if d == "APROBADO":
        return "END"
    if d == "ACLARAR":
        return "ASK"
    if d == "RECHAZADO":
        return "END"
    return "WAIT"

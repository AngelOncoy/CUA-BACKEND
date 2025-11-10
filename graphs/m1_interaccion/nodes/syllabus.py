# backend/graphs/m1_interaccion/nodes/syllabus.py
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from core.config import GOOGLE_API_KEY

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2, google_api_key=GOOGLE_API_KEY)

prompt_syl = ChatPromptTemplate.from_messages([
    ("system", "Genera un sílabus modular con objetivos medibles y estimación de horas por módulo."),
    ("user", "Mapping: {mapping}\nIndustria: {industria}\nNivel: {nivel}")
])

def syllabus_node(state: Dict[str, Any]) -> Dict[str, Any]:
    ent = state.get("entidades", {})
    msg = (prompt_syl | llm).invoke({
        "mapping": state.get("mapping", {}),
        "industria": ent.get("industria",""),
        "nivel": ent.get("nivel","")
    })
    state["syllabus"] = {"markdown": msg.content}
    return state


# graphs/m1_interaccion/nodes/nlp.py
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from core.config import GOOGLE_API_KEY

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2, google_api_key=GOOGLE_API_KEY)

class Entidades(BaseModel):
    competencias: list[str] = Field(default_factory=list)
    industria: str = ""
    nivel: str = ""
    confianza: float = 0.0

parser = PydanticOutputParser(pydantic_object=Entidades)

prompt_nlp = ChatPromptTemplate.from_messages([
    ("system", "Eres un extractor de entidades. Devuelve JSON exacto: competencias(list), industria(str), nivel(str), confianza(float 0-1)."),
    ("user", "{prompt}")
])

def nlp_node(state: Dict[str, Any]) -> Dict[str, Any]:
    chain = prompt_nlp | llm | parser
    ent = chain.invoke({"prompt": state["prompt_raw"]})
    state["entidades"] = ent.model_dump()
    state["confianza_nlp"] = ent.confianza
    return state


# graphs/m1_interaccion/nodes/nlp.py
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from core.config import GOOGLE_API_KEY, GEMINI_MODEL

llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, temperature=0.2, api_key=GOOGLE_API_KEY)

class Entidades(BaseModel):
    competencias: list[str] = Field(default_factory=list)
    industria: str = ""
    nivel: str = ""
    confianza: float = 0.0

parser = PydanticOutputParser(pydantic_object=Entidades)

prompt_nlp = ChatPromptTemplate.from_messages([
    (
        "system",
        """Eres un analista senior especializado en educación corporativa,
        recursos humanos y modelado de competencias. Trabajas dentro del
        sistema AUTOMA, un motor de inteligencia artificial que automatiza la
        creación de cursos empresariales.

        Tu objetivo es analizar los requerimientos textuales de los clientes
        (prompts escritos en lenguaje natural) y traducirlos a una estructura
        semántica que el sistema pueda entender.

        Debes extraer:
        - 'competencias': habilidades o temas mencionados (lista de strings)
        - 'industria': tipo de empresa o sector (string)
        - 'nivel': grado de profundidad requerido (básico/intermedio/avanzado)
        - 'confianza': número entre 0 y 1 que indique qué tan seguro estás de tu análisis

        Reglas:
        1. Si el texto es muy ambiguo, devuelve confianza menor a 0.7.
        2. Nunca inventes información no explícita.
        3. Siempre responde en formato JSON válido, sin explicaciones.

        Ejemplo:
        Usuario: 'Quiero un curso para mi equipo de ventas sobre empatía y negociación.'
        Respuesta:
        {{
          "competencias": ["Empatía", "Negociación"],
          "industria": "Ventas",
          "nivel": "Intermedio",
          "confianza": 0.9
        }}
        """
    ),
    ("user", "{prompt}")
])

def nlp_node(state: Dict[str, Any]) -> Dict[str, Any]:
    chain = prompt_nlp | llm | parser
    ent = chain.invoke({"prompt": state["prompt_raw"]})
    state["entidades"] = ent.model_dump()
    state["confianza_nlp"] = ent.confianza
    return state


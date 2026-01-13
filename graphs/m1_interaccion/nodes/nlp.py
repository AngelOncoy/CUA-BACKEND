# graphs/m1_interaccion/nodes/nlp.py
import os
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from core.config import GOOGLE_API_KEY, GEMINI_MODEL
from core.utils import timed_node
import logging

log = logging.getLogger(__name__)


def read_file(file_path: str) -> str:
    dir_actual = os.path.dirname(os.path.abspath(__file__))
    prompt_file_path = os.path.join(dir_actual, file_path)

    with open(prompt_file_path, "r", encoding="utf-8") as file:
        return file.read()


# Cambio en la ruta: eliminamos 'nodes/' del inicio
prompt_nlp_text = read_file("prompts/prompt_nlp.txt")

# LLM setup
llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, temperature=0.2, api_key=GOOGLE_API_KEY)

# Pydantic model for parsing the result
class Entidades(BaseModel):
    competencias: list[str] = Field(default_factory=list)
    industria: str = ""
    nivel: str = ""
    confianza: float = 0.0

# Output parser for the LLM
parser = PydanticOutputParser(pydantic_object=Entidades)

# Define the prompt template (no need to reference variables yet)
prompt_nlp = ChatPromptTemplate.from_messages([
    ( "system", prompt_nlp_text),
    ("user", "{prompt}")
])

@timed_node
def nlp_node(state: Dict[str, Any]) -> Dict[str, Any]:
    # Pasa solo el 'prompt' a la cadena de procesamiento
    chain = prompt_nlp | llm | parser
    ent = chain.invoke({"prompt": state["prompt_raw"]})
    log.info(f"[NLP] Estado actual: {state}")
    prompt = state["prompt_raw"]
    # Asigna las entidades extraídas del LLM al estado
    state["entidades"] = ent.model_dump()
    state["confianza_nlp"] = ent.confianza
    return state

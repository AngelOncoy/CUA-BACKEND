# graphs/m1_interaccion/nodes/syllabus.py
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from core.config import GOOGLE_API_KEY, GEMINI_MODEL
from core.utils import timed_node
import os

# Inicializar el modelo de IA
llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, temperature=0.2, api_key=GOOGLE_API_KEY)


# Función para leer el archivo de prompt
def read_file(file_path: str) -> str:
    dir_actual = os.path.dirname(os.path.abspath(__file__))
    prompt_file_path = os.path.join(dir_actual, file_path)

    with open(prompt_file_path, "r", encoding="utf-8") as file:
        return file.read()


# Cargar el prompt desde el archivo
prompt_syl_text = read_file("prompts/prompt_syl.txt")

# Crear el ChatPromptTemplate con el prompt cargado
prompt_syl = ChatPromptTemplate.from_messages([
    ("system", prompt_syl_text),
    ("user", "Competencias: {mapping}\nIndustria: {industria}\nNivel: {nivel}")
])


@timed_node
def syllabus_node(state: Dict[str, Any]) -> Dict[str, Any]:
    # Obtener las entidades del estado
    ent = state.get("entidades", {})

    # Generar el syllabus usando el modelo de IA
    msg = (prompt_syl | llm).invoke({
        "mapping": state.get("mapping", {}),
        "industria": ent.get("industria", ""),
        "nivel": ent.get("nivel", "")
    })

    # Almacenar el syllabus generado en formato Markdown en el estado
    state["syllabus"] = {"markdown": msg.content}

    return state